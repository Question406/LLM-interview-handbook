---
id: sys-chunk-pd
section: systems
order: 10
level: A
title: Chunked Prefill 与 Prefill–Decode Disaggregation 在解决什么？
quick: "两者都减少长 prefill 对 decode 的干扰：chunked prefill 在同卡切块混排，PD 分离把两阶段放进不同资源池。先用切块改善混合流量的等待，再按角色差异考虑拆池，并把 KV 传输算进收益。"
tags:
  - Serving
  - Prefill
  - Decode
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DistServe
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: vLLM PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

Chunked prefill 在同一张卡上切块调度，PD 分离则把 prefill 和 decode 放到不同资源池，两者可以叠加。它们都想避免大段输入预填充（prefill，即处理输入并建立缓存）占满 SM，让逐 token 生成（decode）久等。判断收益时要同时看 throughput、首个 token 等待时间（TTFT）、TPOT、KV transfer cost 和利用率，基本机制见 `sys-prefill-decode`。

把超长 输入提示（prompt） 切成固定 token 块，块与正在进行的 decode step 交错。一条 $8\mathrm{k}$ prefill 不再一次占满几十到数百毫秒，decode 可以按步插入，P99 TPOT 不被单条长 prompt 打穿。**不需要跨机传 KV**，实现成本低，vLLM / SGLang 都有。

代价是同 GPU 上仍有调度权衡：块太大，decode 仍需等待；块太小，prefill GEMM 变瘦、TTFT 变差。适合单池、长短请求混部、还不想上两套集群。

Prefill 算术强度高、偏 compute；decode 每步读整份权和历史 KV，偏 bandwidth。DistServe 把两类算子拆到不同资源池，各自扩容：prefill 堆算力，decode 堆带宽和 KV 容量。TTFT 与 TPOT 才能独立调。

必须把 prefill 生成的 KV 传给 decode worker。上下文很长时，KV transfer 本身可能比算子贵，网络拓扑和 cache placement 是一等设计，不是细节。slime 的生产配法见 `slime-pd-disagg`。

短单轮、卡少时，我会先用 chunked prefill；长多轮中，如果 prefill/decode 需要不同 TP 或机型，再考虑 PD。两者可以叠：prefill 池内部仍可切块，避免一条超长 prompt 独占 prefill 机。短单轮（GSM8K 一类）通常不必拆 PD。验收画两条曲线：TTFT 是否因切块变差、TPOT P99 是否因混排变好；PD 再加一条 KV 传输占比，超过算子时间就要先优网络而不是再加卡。

## 追问

**PD 一定更快吗？**
KV 传输和两套调度是税。短请求、弱网络上可能更慢。用 goodput 和 P99 说话。
**Chunked 会改变注意力结果吗？**
正确实现是 exact 的因果注意力，只是把 $QK^\top$ 按块算完。实现 bug 另说。
**为什么 PD 要 session affinity？**
KV 在特定 decode 机上，下一轮或下一 token 要回到对应 worker，见 `slime-router-session`。
**和 PagedAttention 什么关系？**
Paging 管 KV 怎么存；chunk / PD 管 prefill 和 decode 谁先跑、跑在哪。三层不要混。
**KV transfer 用什么介质？**
同机 NVLink / 共享显存便宜；跨机要 IB 或专用 KV 通道。介质选错时，PD 的额外开销会超过拆池收益。
