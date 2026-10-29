---
id: sys-kv-cache-transfer
section: systems
order: 277
level: A
title: 分布式推理里 KV cache 怎么传？多卡通信优化什么？
quick: "先区分传输发生在哪里：TP 做层内集合通信，PD 分离把 prompt 的 KV 从 prefill 池交给 decode 池，请求迁移和远端前缀命中也会搬 KV。优化时先减少要传的字节，再把传输与计算重叠，并选择 NVLink / RDMA 等合适的链路。"
tags:
  - KV Cache
  - PD Disaggregation
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DistServe
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
  - title: Mooncake
    url: https://arxiv.org/abs/2407.00079
    type: primary
---

分布式推理里的 KV 传输要按拓扑分别优化：TP 是层内通信，PD 分离是 prefill 池向 decode 池交接缓存。比如长 prompt 做完 prefill，decode worker 必须拿到对应 KV 才能继续生成，这次搬运可能比 GEMM 还贵。它与权重广播传的对象不同，要分别计算通信量和等待时间；PD 和 chunked prefill 的背景见 `sys-chunk-pd`、`sys-prefill-decode`。

## 先看 KV 在哪些地方移动

1. **张量并行。** 头或隐维切开。标准 MHA 下，某张卡算 attention 可能缺其它头的 K/V，要 all-gather 或把 Q 送到有 K/V 的卡。每层 decode 都可能等待这部分通信，所以 TP 通常希望在 NVLink 互联的卡之间进行。MLA 把 KV 压成共享 latent，传的字节少一个数量级，这是 DeepSeek 推理能把 KV 做小的原因，见 `arch-mla`。
2. **PD 分离。** Prefill worker 算出 prompt KV，decode worker 接着生成。必须跨池传 KV（或传 latent）。上下文一长，传输可能比 GEMM 贵。Mooncake 一类是把 KV 当成可调度的分布式缓存：RDMA、分层存储、跟调度器协同，而不是 `cudaMemcpy` 一下了事。slime 的配法见 `slime-pd-disagg`。
3. **多 replica / 抢占。** 请求从一张卡迁到另一张，或 prefix cache 命中远端块，也是 KV 传输。和 PD 同构，只是触发条件是调度而不是角色拆分。

## 按传输量和等待时间优化

**少传：**
MLA、GQA、KV INT8/FP8、只传 miss 的后缀。量化 KV 减少的是缓存显存占用和网络传输量，和 GPTQ 权重量化不同，见 `sys-int8-vs-fp8`。
**重叠：**
把下一块 prefill 的计算与上一段 KV 的传输放入流水线并行执行；decode 不要空等整段 KV 到齐才开算，能 chunk 就 chunk。
**命中：**
同一 prompt 下的 GRPO 组应尽量复用前缀缓存，见 `sys-rl-engine-kv-util`。命中了就不用传。
**拓扑：**
机内 NVLink / NVSwitch；跨机 RDMA。PD 的 KV 如果走 TCP，额外通信开销可能抵消优化收益。

RL sampling 轨迹（rollout） 里还有第四条：`update_weights` 之后旧 KV 作废，见 `sys-partial-kv-policy`。那是禁止复用，不是又一次 KV 传输。

面试时先画：TP 是层内集合通信，PD 是角色间点对点，权重是参数广播。这三类通信要分别分析，不能都当成 AllReduce。

## 追问

**EP 传的是 KV 吗？**
不是。EP 传的是 token 隐藏状态的分发与结果合并（dispatch / combine），见 `sys-expert-parallel`。MoE decode 仍可能同时有 MLA KV。
**Chunked prefill 要传 KV 吗？**
同卡切块混排，KV 留在本地，不跨机。这是它比 PD 便宜的原因。
**和训练里的 activation 通信？**
训练 PP 传的是激活/梯度，不是 decode KV。RL 训练图重算 logp 时走的是 Megatron / FSDP 那套，见 `sys-rl-multinode-bwd`。
