---
id: sys-kv-cache-transfer
section: systems
order: 277
level: A
title: 分布式推理里 KV cache 怎么传？多卡通信优化什么？
quick: "TP 是层内集合通信，PD 分离是 prefill 池把整段 KV 点对点交给 decode 池。优化靠少传（MLA、KV 量化）、与计算重叠、前缀命中，以及走 NVLink / RDMA。"
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

Serving 的 PD / chunked 输入预填充（prefill，即处理输入并建立缓存） 见 `sys-chunk-pd`、`sys-prefill-decode`。本题把 **KV 搬家** 单独拿出来：面试时常把它和「多卡通信」一起问，但 TP 集合通信、PD 点对点、权重广播是三条路。

## 三种会动 KV 的拓扑

1. **张量并行。** 头或隐维切开。标准 MHA 下，某张卡算注意力可能缺其它头的 K/V，要 all-gather 或把 Q 送到有 K/V 的卡。每层 decode 都可能等待这部分通信，所以 TP 通常希望在 NVLink 互联的卡之间进行。MLA 把 KV 压成共享 latent，传的字节少一个数量级，这是 DeepSeek 推理能把 KV 做小的原因，见 `arch-mla`。
2. **PD 分离。** Prefill worker 算出 输入提示（prompt） KV，decode worker 接着生成。必须跨池传 KV（或传 latent）。上下文一长，传输可能比 GEMM 贵。Mooncake 一类是把 KV 当成可调度的分布式缓存：RDMA、分层存储、跟调度器协同，而不是 `cudaMemcpy` 一下了事。slime 的配法见 `slime-pd-disagg`。
3. **多 replica / 抢占。** 请求从一张卡迁到另一张，或 prefix cache 命中远端块，也是 KV 传输。和 PD 同构，只是触发条件是调度而不是角色拆分。

## 优化按字节 × 延迟，不是按名词

- **少传：** MLA、GQA、KV INT8/FP8、只传 miss 的后缀。量化 KV 减少的是缓存显存占用和网络传输量，和 GPTQ 权重量化不同，见 `sys-int8-vs-fp8`。
- **重叠：** 把下一块 prefill 的计算与上一段 KV 的传输放入流水线并行执行；decode 不要空等整段 KV 到齐才开算，能 chunk 就 chunk。
- **命中：** 同一输入提示下的 GRPO 组应尽量复用前缀缓存，见 `sys-rl-engine-kv-util`。命中了就不用传。
- **拓扑：** 机内 NVLink / NVSwitch；跨机 RDMA。PD 的 KV 如果走 TCP，额外通信开销可能抵消优化收益。

强化学习（RL） 采样轨迹（rollout） 里还有第四条：`update_weights` 之后旧 KV 作废，见 `sys-partial-kv-policy`。那是禁止复用，不是又一次 KV 传输。

面试时先画：TP 是层内集合通信，PD 是角色间点对点，权重是参数广播。这三类通信要分别分析，不能都当成 AllReduce。

## 追问

- **EP 传的是 KV 吗？** 不是。EP 传的是 token 隐藏状态的分发与结果合并（dispatch / combine），见 `sys-expert-parallel`。MoE decode 仍可能同时有 MLA KV。
- **Chunked prefill 要传 KV 吗？** 同卡切块混排，KV 留在本地，不跨机。这是它比 PD 便宜的原因。
- **和训练里的 activation 通信？** 训练 PP 传的是激活/梯度，不是 decode KV。RL 训练图重算 logp 时走的是 Megatron / FSDP 那套，见 `sys-rl-multinode-bwd`。
