---
id: sys-chunked-prefill
section: systems
order: 19
level: A
title: 系统：chunked prefill 和 decode 混部
quick: "把长 prompt 分成有 token 预算的块，每个 iteration 优先给活跃 decode 一步，再放入能装下的 prefill 块。块太小会拉长 TTFT，太大又会干扰 TPOT，要按 decode SLO、算力与 KV 水位一起调。"
tags:
  - vLLM
  - DistServe
  - Serving
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: "SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills"
    url: https://arxiv.org/abs/2308.16369
    type: primary
  - title: Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
    url: https://arxiv.org/abs/2403.02310
    type: primary
  - title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving"
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: Continuous batching from first principles
    url: https://huggingface.co/blog/continuous_batching
    type: secondary
---

Chunked prefill 用有限的 token 块代替整段 prompt，让每个 iteration 都能穿插 decode。比如 24 条请求正在生成，新来一条 8k prompt，可以一次只放 512-token 的 prefill 块，减少其他请求被长 kernel 阻塞的时间。

vLLM 的 chunked prefill、Microsoft SARATHI / Sarathi-Serve，以及 DistServe 里的不拆池基线，处理的都是 prefill 与 decode 的不同 roofline 如何在同卡共存。跨池分离见 `sys-prefill-decode-disagg`，iteration 调度见 `sys-cont-batch`。

短 prompt、卡少时，跨池搬 KV 的额外开销可能比同卡切块更大，因此可以先用单池切块，再根据 SLO 与资源干扰决定是否分离。

切块之后每一步的 token 预算要封顶，否则又退化成整段 prefill。这和 `max_num_seqs` 是两道闸。

Prefill 算术强度随 prompt 长度涨，一条 $8\mathrm{k}$ 的 prompt 可以占满 SM 几十到几百毫秒。同一 GPU 上的 decode batch 是 memory-bound 的瘦 GEMM，被这次大 kernel 打断，TPOT 出现尖刺。Orca 式 continuous batching 允许新请求在 iteration 边界插入，但插入的是 **整段** prefill 的话，调度粒度仍被最长那次 prefill 绑住。

SARATHI 的修法：把 prefill 切成大约等计算量的 token 块（常见 512-2048，跟 GPU 和 $d$ 走）。每个 iteration 先保证在飞的 decode 都走一步，再塞一块未完成的 prefill，使本步 token 数靠近一个预算。一步实际耗时被块大小封顶，和整段 prompt 多长解耦。这样 decode 不必等整条 8k prompt 算完才继续。

块太小：prefill 变瘦，GEMM 喂不饱，首个 token 的等待时间（TTFT） 变差（同一输入提示 要更多步、每步还有 kernel 启动）。块太大：又接近整段 prefill，decode 尖刺回来。预算要对着「这一步还剩多少 decode token」调，不是固定切 2048 就结束。混合 batch 的形状：24 条 decode + 1 条 512-token 的 prefill 块，比 24 条 decode 等一条 8k prefill 的 P99 好看。

切块没有取消干扰，只是把干扰切碎。每一步仍要读权重；prefill 块还要写 KV 页。Decode 的 HBM 流量和 prefill 的计算挤在同一套 SM 上，Nsight 上两者重叠但各自 SOL 都低，就是抢资源。KV 分页必须在：新 prefill 块按页追加，结束的 decode 还页，否则切块调度没有地方放中间状态，见 `sys-paged-attn`。

和 prefix cache：命中的前缀可以跳过，只对 miss 的后缀切块。块边界尽量靠近页边界，减少同时跨页、跨块的处理。PD 分离把 prefill 池和 decode 池拆开，KV 要搬过网络；chunked prefill 不搬 KV，代价是同卡干扰。短 prompt、卡少、流量里 prefill 不极端时，切块通常够。长上下文、TTFT 和 TPOT 都要紧、两阶段想用不同 TP 度，再上分离。

Chunked prefill 仍在单池中运行，和 PD 分离是不同方案。已完成块的 KV 留给后续块，注意力数值应保持一致；token 预算与 KV 容量仍限制 goodput，不能无限增大 `max_num_seqs`。和 `sys-cont-batch` 一起开：iteration 边界插入请求，插入时只允许一块 prefill。

## 追问

**块大小怎么选？**
对着 decode SLO 和 prefill 能否喂饱 Tensor Core。先定一步最大毫秒，再反推 token 预算。块太小喂不饱 Tensor Core，TTFT 变差；块太大又接近整段 prefill，decode 尖刺回来。
**TTFT 会不会更差？**
常会。同一输入提示 拆多步，中间还插入别人的 decode。换的是别人的 TPOT。两头都要紧就分离。
**和 continuous batching 是一层吗？**
不是。Continuous batching 是 iteration 插入/退出；chunked prefill 是插入时 prefill 不许一次吃完。要一起开。
**pipeline 上为什么也爱切块？**
各 microbatch 计算量齐，气泡小。SARATHI 论文把这当成第二收益，见 `nvidia-pipeline-bubble`。
**切块改注意力数值吗？**
不应改。已完成块的 KV 留下，下一块当带 cache 的 prefill。数值漂了是实现 bug。
**什么时候该放弃切块上分离？**
两阶段 SLO 都紧、想用不同并行度、或 Nsight 上同卡 SOL 互相踩死。搬 KV 的账见 `sys-prefill-decode-disagg`。
