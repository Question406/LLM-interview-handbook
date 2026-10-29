---
id: slime-weight-sync
section: systems
order: 253
level: S
title: slime 权重怎么推到 SGLang？delta 同步在解决什么，和 veRL 重算 logp 是一回事吗？
quick: >-
  先把 Megatron 权重同步到 SGLang，保证 sampling 使用正确版本；再在 Megatron 上重算训练图的 logp。可建通信组时用
  tensor / NCCL，跨集群或外部 engine 可用 `--update-weight-transport disk`，大模型再按变更量考虑
  `--update-weight-mode delta`。
tags:
  - slime
  - SGLang
  - Weight Sync
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Delta 权重同步 — slime
    url: 'https://thudm.github.io/slime/zh/advanced/delta-weight-sync.html'
    type: primary
  - title: slime 使用文档
    url: 'https://thudm.github.io/slime/zh/get_started/usage.html'
    type: primary
---

权重同步让 SGLang 使用正确的 $\theta$ 版本；Megatron 再 forward，则为 $\pi_{\mathrm{old}}$ / $\pi_\theta$ 提供训练图上的 logp。两步分别处理版本和数值一致性，同步完成后仍需重算 logp。可以把流程画成 trainer → engine 更新版本、engine tokens → trainer forward 重算 logp，相关说明见 `meituan-verl-recompute-logprob`、`infra-rl-weight-sync`。

slime 默认由 Megatron 训练、SGLang 推理，两边权重布局不同。搬运方式取决于进程位置和能否建立通信组：

能在同集群建立 comm group 时，tensor / NCCL 路径最快。Colocate 还可以用本机内存 / IPC，把 Megatron 权重装进旁边的 SGLang，省去落盘。`--colocate` 下仍是两套进程，共用 GPU、通过 offload 交替执行，见 `slime-colocate-vs-split`。NCCL 要使用独立通信组，初始化顺序也要写进 runbook，避免与训练并行组冲突。
外部 engine、跨集群或建不了 NCCL 时，可用 `--update-weight-transport disk` 传 full：先写 HF 目录，再由 SGLang `update_weights_from_disk` 加载。`--rollout-external-engine-addrs` 连接已有服务时常走这条，见 `slime-external-engine`。磁盘可作为便于调试的 source of truth，适合扩容和给新 replica 做 seed，但最慢，不适合每步热路径。
大 MoE 或跨机房还可以叠加 `--update-weight-mode delta`，只传两次同步之间变化的 tensor，由 engine `/pull_weights` 原地 apply。官方针对的是全量百 B 级权重每步落盘或广播的高成本；它与 colocate 的 IPC 用途不同。双方必须从同一份 full 起步，版本号对不上就不能 apply diff。

选传输方式时，先看能否建 group：能建就用 NCCL，跨集群可用 disk full，参数极大且变动稀疏时再叠 delta。colocate 的瓶颈通常不在这段传输，强加 delta 未必有收益。Delta 节省传输字节，计算图差异仍需另行处理。MoE 里大部分 expert 本步没被更新时，diff 才划算；稠密模型每层都动，delta 可能并不比 full 小多少，还多了计算 diff 和 apply 的复杂度。是否开 delta，要结合模型结构和进程放置判断。

引擎加载新权重后，不能继续用旧 KV。attention 缓存是旧 $\theta$ 算出来的，必须 flush，否则新权重配旧 KV，sampling 既偏又难复现。同时记下 `rollout_id` / policy version，轨迹进 buffer 时带着版本，异步或 partial sampling 轨迹（rollout） 才能按 age 丢弃。Prefix cache、CUDA graph 也要按版本失效：只清 KV、不失效 graph，可能踩到旧权编译出的图。同步是一条事务：传权、校验 checksum / 形状、flush、打版本号，失败则整步重来，不要让部分 replica 进新版本。

Delta 还有一个运维约束：晚加入的 replica 不能只回放 delta。diff 依赖「从哪一份 full 开始累加」。新 worker 要先吃最近一份 full checkpoint 做 seed，再接后续 delta。只回放 diff 会得到一份无法确认版本的权重。生产上要把 full 的周期写成 SLA：例如每 $k$ 步或每次拓扑变化强制 full，并在元数据里记下「这份 delta 基于哪个 full hash」。没有 hash 链，出事时无法证明引擎里的 $\theta$ 等于 trainer。这和模型发布的 checksum 是同一纪律，只是发生在每一步 RL 热路径上。

SGLang 的 sampling logp（尤其 BF16 训练 + FP8 rollout）和 Megatron 训练图在算子、分块、精度上都不对齐，不能当 $\pi_{\mathrm{old}}$。正确拆法：

1. 同步：让 SGLang 的 $\theta$ 等于刚更新的 actor（本题）。
2. sampling：引擎只负责生成 token，logp 可丢或只做监控。
3. 重算：同一批 token 在 Megatron 上 no-grad forward，得到训练图上的 old / ref logp，再在更新时算 $\rho$。

缺 1，rollout 还在用上一版策略，off-policy 程度被低估。缺 3，clip 和 KL 吃进引擎噪声。TIS（`--use-tis`）修正 sampling 分布的偏差（量化、partial、异步 stale），仍然不能代替 Megatron logp；两者叠加，不是互斥。因此打开 `--use-tis` 后，训练图上的 logp 仍要重算。同步失败要能回滚到上一 `rollout_id` 继续采，不要带着半新半旧的权硬训；colocate 时两边进程的权要一起回同一版本。失败重试要有上限，超时就把该步 rollout 作废，不要用旧权混进新 `rollout_id`。

同步后忘了 flush KV：新 $\theta$ 配旧缓存，sampling 分布既不是 old 也不是 new，ratio 再准也救不了这条轨迹。Delta 在有的 replica 丢包、有的 apply 成功：集群里多版本并存，必须靠 `rollout_id` 丢掉对不上的样本，而不是平均掉。晚加入节点只拉 delta：权重从零加上 diff，数值不正确，要用最近的 full 做 seed。这些都是 版本 问题；logp 对不齐则是 图 问题，不要用同一次「同步失败」解释。

对照 veRL，HybridEngine 在同进程 reshard，传输问题更少、布局转换更重；slime 跨进程 `update_weights`，则要显式处理传输。分卡 + 外部 engine 时 disk/delta 几乎是必选项，见 `slime-external-engine`。跨进程意味着可以独立重启 SGLang、独立升级引擎，这是 slime 相对 HybridEngine 的运维弹性；相应地，同步必须实现为可靠的跨进程协议。要证明训推一致，可以先用版本号和 checksum 核对，再解释 delta 如何传递变更。

## 追问

**Delta 能替代 full 吗？**
不能作为唯一种子。周期 full + 中间 delta，新 replica 必须从 full 起步。只存 delta 链的系统在任意一次 apply 失败后无法自愈，运维上必须保留可回放的 full 点。
**同步频率怎么选？**
每步同步最新、最贵；隔多步则 stale。看 KL、ratio 方差和 `rollout_id` 间隔，而不是固定「越快越好」。异步训练里还要设最大 version gap，超了就丢样本，见 `sys-rl-infra`。
**Colocate 还要 disk 吗？**
通常不必。Disk 是给分卡 / 外部 engine / 跨机房。混用要说清谁是 source of truth。Colocate 上再走 disk 往往是调试手段，会把一步拉成秒级，不该当默认。
**和 HybridEngine reshard 比？**
veRL 同进程换布局，少一份整模；slime 无论 colocate 还是分卡，都是把权 **推到另一个进程**。见 `sys-verl-hybridengine`。一个是布局变换，一个是跨进程运输，监控指标也不一样。
