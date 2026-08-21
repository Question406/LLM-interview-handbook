---
id: slime-weight-sync
section: systems
order: 253
level: S
title: slime 权重怎么推到 SGLang？delta 同步在解决什么，和 veRL 重算 logp 是一回事吗？
quick: >-
  colocate 走内存 / 分布式 group 把 Megatron 权装进本机 SGLang；分卡或外部 engine 用
  `--update-weight-transport disk`，大模型再开 `--update-weight-mode delta` 只传变化字节。同步解决**版本**；Megatron
  上再 forward 解决**训练图 logp**。两步都要做，不能互相替代。
tags:
  - slime
  - SGLang
  - Weight Sync
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Delta 权重同步 — slime
    url: https://thudm.github.io/slime/zh/advanced/delta-weight-sync.html
    type: primary
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

别把「权重已经推到 SGLang」说成「ratio 可以用引擎 logp 了」。同步解决的是 **推理进程看到的 $\theta$ 版本**；Megatron 上再 forward 解决的是 **$\pi_{\mathrm{old}}$ / $\pi_\theta$ 用哪张计算图**。一个管 freshness，一个管数值，见 `meituan-verl-recompute-logprob`、`infra-rl-weight-sync`。现场把 delta、NCCL、disk 背得很熟，却说「同步完 logp 就对齐了」，会直接被判成没做过 on-policy 数学。先画两个箭头：trainer → engine 是版本，engine tokens → trainer forward 是 logp，再往下讲运输方式。

## 三条运输，对应三种放置

slime 默认训练是 Megatron、推理是 SGLang，权重布局本来就不一样。怎么搬，先看进程在不在一起：

- **tensor / NCCL（能建 comm group）。** 同集群、能拉起分布式 group 时最快。Colocate 更进一步：本机内存 / IPC 把 Megatron 权装进旁边的 SGLang，不必先落盘。`--colocate` 时两边仍是两套进程，只是卡共享、offload 轮流上班，见 `slime-colocate-vs-split`。NCCL 路径要独占通信组，和训练并行组冲突是常见翻车，初始化顺序要写进 runbook。
- **`--update-weight-transport disk`（full）。** 写成 HF 目录，SGLang `update_weights_from_disk`。外部 engine、跨集群、建不了 NCCL 时的保底。`--rollout-external-engine-addrs` 接已有服务时经常走这条，见 `slime-external-engine`。磁盘是可调试的 source of truth，也是最慢的一条，适合扩容和新 replica seed，不适合每步热路径。
- **`--update-weight-mode delta`。** 两次同步之间只发 **变化了的 tensor**，engine `/pull_weights` 原地 apply。官方定位是大 MoE、跨机房：全量百 B 级权重每步走磁盘或满带宽广播不可接受。它 **不替代** colocate 的 IPC，也不是「可以少做一次 full」。Diff 的正确性依赖双方从同一份 full 起步，版本号对不上就不要 apply。

选型口诀：能建 group 用 NCCL；跨集群用 disk full；参数极大且变动稀疏再叠 delta。不要在 colocate 上强行 delta 来「优化」，那不是这条路径的瓶颈。Delta 省的是 **传输字节**，不是计算图差异。MoE 里大部分 expert 本步没被更新时，diff 才划算；稠密模型每层都动，delta 可能并不比 full 小多少，还多了计算 diff 和 apply 的复杂度。面试被问「为什么开 delta」要能答到模型结构和放置，而不是「大模型都应该开」。

## 同步之后必须做的两件事

引擎装上新权不等于可以继续用旧 KV。注意力缓存是旧 $\theta$ 算出来的，必须 flush，否则新权重配旧 KV，采样既偏又难复现。同时记下 `rollout_id` / policy version，轨迹进 buffer 时带着版本，异步或 partial rollout 才能按 age 丢弃。Prefix cache、CUDA graph 也要按版本失效：只清 KV、不失效 graph，可能踩到旧权编译出的图。同步是一条事务：传权、校验 checksum / 形状、flush、打版本号，失败则整步重来，不要让部分 replica 进新版本。

Delta 还有一个运维约束：晚加入的 replica **不能只回放 delta**。diff 依赖「从哪一份 full 开始累加」。新 worker 要先吃最近一份 **full** checkpoint 做 seed，再接后续 delta。只回放 diff 会得到一份谁也说不清的权重。生产上要把 full 的周期写成 SLA：例如每 $k$ 步或每次拓扑变化强制 full，并在元数据里记下「这份 delta 基于哪个 full hash」。没有 hash 链，出事时无法证明引擎里的 $\theta$ 等于 trainer。这和模型发布的 checksum 是同一纪律，只是发生在每一步 RL 热路径上。

## 和 veRL 重算 logp 不是一回事

SGLang 的采样 logp（尤其 BF16 训练 + FP8 rollout）和 Megatron 训练图在算子、分块、精度上都不对齐，不能当 $\pi_{\mathrm{old}}$。正确拆法：

1. 同步：让 SGLang 的 $\theta$ 等于刚更新的 actor（本题）。
2. 采样：引擎只负责吐 token，logp 可丢或只做监控。
3. 重算：同一批 token 在 Megatron 上 no-grad forward，得到训练图上的 old / ref logp，再在更新时算 $\rho$。

缺 1，rollout 还在用上一版策略，off-policy 程度被低估。缺 3，clip 和 KL 吃进引擎噪声。TIS（`--use-tis`）修的是「采样策略和训练图不一致」的另一层，仍然不能代替 Megatron logp。面试把两步分成「版本」和「计算图」，比背 flag 名更稳。Partial rollout 或 FP8 采样时，TIS 和重算会同时出现：前者修采样分布，后者修训练图数值，不要用其中一个代替另一个。把 `--use-tis` 说成「可以不重算 logp」，是这题的标准错答。TIS 修的是采样分布与训练策略之间的隙，重算修的是两张计算图的数值隙，对象不同。面试把「版本 / 图 / 采样策略」说成三层，比把所有不一致都叫 mismatch 更清楚。slime 的 `--use-tis` 和 Megatron logp 是叠加上去的，不是互斥开关。同步失败要能回滚到上一 `rollout_id` 继续采，而不是带着半新半旧的权硬训。把回滚写进同步事务，比事后从 buffer 里手工丢样本更干净。Colocate 时回滚还意味着两边进程的权要一起回到同一版本，offload 中途失败是高发点。把 trainer 与 engine 的版本号打在同一条日志里，对账比事后 dump 权重快得多。失败重试要有上限，避免同步死循环拖死整步 RL。超时要把该步 rollout 作废，不要用旧权混进新 `rollout_id`。

## 失败长什么样

同步后忘了 flush KV：新 $\theta$ 配旧缓存，采样分布既不是 old 也不是 new，ratio 再准也救不了这条轨迹。Delta 在有的 replica 丢包、有的 apply 成功：集群里多版本并存，必须靠 `rollout_id` 丢掉对不上的样本，而不是平均掉。晚加入节点只拉 delta：权重从零加上 diff，数值是垃圾，要用最近的 full 做 seed。这些都是 **版本** 问题；logp 对不齐则是 **图** 问题，不要用同一次「同步失败」解释。

和 veRL 对答：HybridEngine 同进程 reshard，传输问题更少、布局转换更重；slime 跨进程 `update_weights`，传输问题更显式。分卡 + 外部 engine 时 disk/delta 几乎是必选项，见 `slime-external-engine`。跨进程意味着可以独立重启 SGLang、独立升级引擎，这是 slime 相对 HybridEngine 的运维弹性；代价是必须把同步做成可靠协议，而不是「同进程里改个指针」。面试被问「你们怎么保证训推一致」，先答版本号和 checksum，再答 delta，不要一上来讲 diff 算法。

## 追问

- **Delta 能替代 full 吗？** 不能作为唯一种子。周期 full + 中间 delta，新 replica 必须从 full 起步。只存 delta 链的系统在任意一次 apply 失败后无法自愈，运维上必须保留可回放的 full 点。
- **同步频率怎么选？** 每步同步最新、最贵；隔多步则 stale。看 KL、ratio 方差和 `rollout_id` 间隔，而不是固定「越快越好」。异步训练里还要设最大 version gap，超了就丢样本，见 `sys-rl-infra`。
- **Colocate 还要 disk 吗？** 通常不必。Disk 是给分卡 / 外部 engine / 跨机房。混用要说清谁是 source of truth。Colocate 上再走 disk 往往是调试手段，会把一步拉成秒级，不该当默认。
- **和 HybridEngine reshard 比？** veRL 同进程换布局，少一份整模；slime 无论 colocate 还是分卡，都是把权 **推到另一个进程**。见 `sys-verl-hybridengine`。一个是布局变换，一个是跨进程运输，监控指标也不一样。
