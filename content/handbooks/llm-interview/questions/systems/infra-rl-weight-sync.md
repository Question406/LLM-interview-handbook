---
id: infra-rl-weight-sync
section: systems
order: 239
level: S
title: AI Infra 实习：训练完的权重怎么同步到推理引擎？
quick: >-
  三条路：落盘再 load（简单、可扩容、慢）；同卡 / IPC 传 tensor（HybridEngine 原地
  reshard）；分卡用 NCCL/IB 广播 named tensor。同步后必须 flush KV，并记下 policy
  version。全量 70B 每步走磁盘通常不可接受。
tags:
  - RL Infra
  - VeRL
  - vLLM
  - SGLang
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: AI infra实习面经（小厂）
    url: https://www.nowcoder.com/feed/main/detail/166e576d5afa4a298cf9492ed51bed04
    type: candidate-first-hand
  - title: SGLang for RL
    url: https://github.com/sgl-project/sglang/blob/main/docs/advanced_features/sglang_for_rl.md
    type: primary
---

常见误区是：直接答成「存个 checkpoint 再 `load`」。训练后端是 FSDP / Megatron 分片，推理要的是 vLLM / SGLang 的 TP 布局，「同步」= 收集 + 换布局 + 装进引擎 + 清 KV + 记版本。漏后两步，下一轮采样会用旧 KV 配新权重，或轨迹对不上 $\theta$。这和「为什么重算 logp」是两件事：一个管权重版本，另一个管计算结果是否与训练图一致。我会把三件事画成三步：HybridEngine 管布局，本问答管版本怎么送到引擎，重算 logp 管 ratio 用哪张计算图。缺一都会在 $\rho$ 上出不易察觉的偏差。

## 为什么必须换布局

Actor update 结束时，参数按训练并行切开：FSDP 按 unit 分片，Megatron 按 TP/PP/EP 切。引擎要的是推理 TP 下的连续（或按其自己的 sharding）权重，再配 PagedAttention 的 KV。DeepSpeed-Chat 一类朴素路径会先 gather 成整模再切开给推理，峰值多一份完整权重，70B 上常常直接 OOM。veRL HybridEngine 的动机就是少这次全局收集，见 `sys-verl-hybridengine`。slime 则在 Megatron trainer 与 SGLang server 之间 `update_weights`，colocate 时靠 offload 轮流占显存，见 `slime-colocate-vs-split`、`slime-weight-sync`。

## 三条路径

| 路径 | 适用 | 代价 |
| --- | --- | --- |
| 磁盘 checkpoint | 扩容新 replica、容错、冷启动 | I/O，秒到分钟级；全量 70B 每步通常不可接受 |
| in-memory / IPC | 同卡 colocate、HybridEngine 原地 reshard | 几乎不占第二份整模；一步内训推串行 |
| NCCL / IB broadcast named tensor | 训练与 rollout 分节点 | 要专属通信组、带宽；可叠 delta / LoRA |

LoRA 可以只推 adapter，流量从百 GB 降到百 MB 级，但版本语义仍要一致：base 没变、adapter 变了，cache key 也要变。Delta 同步同理：漏一个 name 就会 silently 用半新半旧权。

选型先问拓扑。同构、卡紧、大模型：偏 HybridEngine / 同卡 IPC。已经有独立推理池、要异构扩容：偏 NCCL 广播。磁盘只当兜底和拉新 replica，不要当每步热路径。70B BF16 整模大约 140GB，PCIe 写读一轮就是秒到十秒量级，共享存储更慢；同节点 NVLink 搬切片是毫秒到百毫秒。面试用数量级说明「为什么磁盘不能当热路径」，更有用。LoRA / delta 把流量从整模降到变更切片，但漏 name、漏 layernorm、漏 embedding 会让引擎处于半新半旧状态，比完全不同步更难查。同步协议要有版本号和完整性校验：要么整版切过去，要么失败回滚，不要部分成功还继续 generate。

## 同步之后还要做什么

装进引擎不等于可以继续 generate：

- Flush KV。 旧 KV 是旧 $\theta$ 算的，和新权混用会让后续 token 的数值错乱。Prefix cache 的 key 也必须带上 policy version。
- 记下 `policy_version`。 Buffer 里每条轨迹要知道自己生于哪一版，异步强化学习才可以按版本差丢弃过旧样本，见 `sys-rl-infra`。
- 未完成请求。 要么取消重采，要么吃完旧权并打 off-policy 标记。两边都不做，组内会混两个 $\theta$。

频率 vs stale 是产品决策：每步全量同步最干净，实际耗时被通信吃掉；隔 $k$ 步同步则 $\rho$ 偏离 $1$。面试把「带宽 × 同步间隔 × 是否 LoRA」讲清楚，比背框架 API 有用。未完成请求尤其要有书面策略：取消则浪费已经生成的 token，但版本干净；吃完旧权则必须在 Buffer 里打 `policy_version`，后续用 TIS 或丢弃，见 `slime-async-train`。Prefix cache 的 key 若不带版本，公共系统提示的 KV 会跨策略复用，等于把旧激活续进新权，见 `sys-prefix-cache-isolation`。

colocate 场景下同步还和 offload 抢 PCIe：一边在把 Megatron 搬回来，一边在推 SGLang 权，峰值带宽会被打满，一步里出现「同步气泡」。profile 要把 `update_weights` 单独计时，不要全部算进 generate。slime 的 named tensor 广播、veRL 的 HybridEngine reshard、OpenRLHF 的 vLLM actor `load_weights`，都是这张表上的不同格子，先选格子再报框架。

## 和布局、数值怎么分工

面试把三件事画在时间轴上：update 结束 → 换布局（HybridEngine / offload）→ 把 $\theta$ 送到引擎（本题）→ flush KV、打 version → 下一轮 generate → 训练图重算 logp。同步解决的是「引擎里是哪一版权」，不解决「这版权在引擎里算出来的 logp 能不能进 ratio」。后者永远要回训练图。同卡 IPC 看起来「没有同步」，其实 reshard 就是同步，只是不走网络；失败模式变成切片对不齐、短暂缓冲 OOM。

分卡 NCCL 失败模式是 communicator 和带宽。磁盘失败模式是太慢、文件写一半。三条路的验收都是：引擎侧抽样 checksum 与 trainer 一致、KV 已空、version 单调加一。缺 checksum 会在 MoE / LoRA 漏 name 时静默错下去。RL 一步里同步频率是产品参数：每步同步最干净，长分步推理（CoT）场景中通信占比上升；隔 $k$ 步则要 TIS。

把频率、带宽、是否 delta 写在同一张表上，这题才算答完。70B 全量每步走磁盘通常不可接受，这句话要带数量级：整模约 140GB，热路径必须是内存或 RDMA。

## 追问

- **为什么 70B 每步落盘不行？** 写读各一份整模，SSD / 共享存储是秒到分钟，而一步训练可能只要几十秒。热路径必须走内存或 RDMA。磁盘只当扩容 replica 和容错兜底。
- **HybridEngine 还要不要 NCCL？** 同卡 reshard 走卡内 / NVLink 的切片补齐，不是全集群广播整模。分卡部署才需要跨节点 communicator。对不齐会退回朴素 gather，原先的显存节省就无法实现。
- **同步完还要重算 logp 吗？** 要。引擎里的 $\theta$ 已经是新的，但采样 logp 的算子、精度、TP 仍可能和训练图不一致。同步管版本，重算管数值图，见 `meituan-verl-recompute-logprob`。
- **SGLang 的 `update_weights` 失败了怎么办？** 视为版本没切过去：不要继续 rollout，也不要混用新旧 KV。先确认 named tensor 对齐和通信组还在。部分成功比完全失败更危险。
- **LoRA 只推 adapter 还要 flush KV 吗？** 要。adapter 变了，同一输入提示 的 KV 也不能留。cache key 还要带 adapter id 和 policy version。
- **未完成请求怎么处理？** 取消则浪费已生成 decode、版本干净；吃完旧权则必须打 version，后续 TIS 或丢弃。两边都不做，组内会混两个 $\theta$。
- **delta / named tensor 漏一层会怎样？** 引擎处于半新半旧，比完全不同步更难查。要有完整性校验：整版切过去或失败回滚，不要部分成功还继续 generate。
- **和 HybridEngine、重算 logp 怎么一句话分？** HybridEngine 管布局，本题管版本送到引擎并 flush KV，重算 logp 管 ratio 用训练图。缺一都会在 $\rho$ 上无声地偏。70B 每步落盘通常不可接受，热路径走内存或 RDMA，同步后必须清 KV、记版本。
