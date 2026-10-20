---
id: sys-cont-batch
section: systems
order: 5
level: S
title: 系统：continuous batching，iteration-level 调度，hole 碎片
quick: "静态 batch 等最长那条，短请求的槽位是空洞。Orca 把调度改到每个逐 token 生成（decode）步骤：结束的立刻腾位，waiting 里补进新请求。吞吐来自少空等，不是更大的静态矩阵。空洞要靠 ragged batch 和分页 KV 才能真正填上。"
tags:
  - Serving
  - NVIDIA
  - vLLM
  - TGI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: "Orca: A Distributed Serving System for Transformer-Based Generative Models"
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: Continuous batching from first principles
    url: https://huggingface.co/blog/continuous_batching
    type: secondary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: secondary
---

## 题怎么来的

NVIDIA TensorRT-LLM 叫 in-flight batching，vLLM / Hugging Face TGI 叫 continuous batching，论文原点是 OSDI'22 的 Orca。OpenAI serving 岗也会问同一套调度（见 `openai-continuous-batching`）。核心不是「动态 padding」，是 **调度粒度从整条请求改成每个 iteration**。

## 静态 batch 的空洞

$B$ 条请求一起 generate，长度可以差一个数量级。静态实现 pad 到最长那条：先结束的行仍占着计算槽和按 `max_len` 预留的 KV，直到最慢那条写完。GPU 看起来在做 $[B,d]\times[d,d]$，有的行已经是 mask 掉的废计算。LLM 生成长度方差远大于分类模型，这个税更重。

调大静态 `batch_size` 只是让空洞更贵：更多行在等最长尾部。hole 碎片有两类：时间上的洞（短请求结束后空转）和内存上的洞（按 max length 预留、实际没用满）。两件都要补。

## 每个 iteration 都重新调度请求

Orca 每个逐 token 生成（decode）步骤：

1. 把本步已结束的序列移出，释放它的计算槽。
2. 若还有槽位和 KV 容量，从 waiting 插入新请求；新请求往往要先处理输入并建立缓存（prefill）。
3. 对仍在处理的请求集合做一步 decode。

GPU 上的有效 $B$ 维持在高位，decode 的瘦 GEMM 被喂得更满。Hugging Face 那篇从 first principles 把这条路拆成：KV cache、ragged 张量（不要为了对齐而 pad）、再加动态补位。TensorRT-LLM 的 IFB 同一件事：context 阶段和 generation 阶段可以出现在同一个 iteration 里。

具体形状：某一步 batch 里 24 条在 decode、2 条在 chunked prefill。结束 3 条、插入 3 条 waiting，下一步还是约 26 条活着，没有人在等最长那条写完。静态 batch 里这 3 个空槽会一直 pad 到 max length。这就是 hole：时间洞（空等）和内存洞（预留没用满）。

空洞不会因为「开了 continuous batching」自动消失：

- **计算空洞：** 还用稠密 padded 张量，结束行仍在 GEMM 里吃 mask。要 packed / ragged kernel，只算有效的 token。
- **内存空洞：** 仍按 `max_len` 连续预留 KV，新请求没有地方插。要 PagedAttention 按块分配、结束即回收，见 `sys-paged-attn`。
- **prefill 打断：** 一条长输入提示（prompt） 插入 decode batch，会把 memory-bound 的 decode 流水拆碎。工程上用 chunked prefill 把长 prompt 切块，块之间仍插入 decode；再狠就 prefill/decode 分池，见 `sys-prefill-decode-disagg`。

调度目标往往是 SLO 内的 goodput，不是瞬时 tokens/s。`max_num_seqs` 提高到接近 KV 容量上限，P99 TPOT 先坏。短请求一直插入会饿死长请求，要 aging / 抢占。NVIDIA 岗可能追 Nsight 上 SM 是在算 decode、在算一段巨大 prefill，还是在等 KV 分配失败后的抢占。

## 追问

- **和动态 padding 是一回事吗？** 不是。动态 padding 仍等整 batch 结束才换人；continuous batching 在每个 decode token 边界就移出、插入。
- **没有 paging 只做 iteration 调度行不行？** 很快 OOM：结束序列的 KV 按最大长度占着，新请求没有页。Orca 的调度和 vLLM 的分页是配套。
- **batch 越大越好吗？** 有效 $B$ 提高 decode 算术强度，但 KV 容量和 TPOT SLO 封顶。应比较满足 SLO 的有效吞吐量（goodput）。
- **和 PD 分离什么关系？** Continuous batching 是单池时间复用；PD 分离是跨池空间复用。Chunked prefill 是单池折中。三层不要说成一个开关。
- **hole 和 KV 碎片是一件事吗？** 时间 hole 是调度粒度；KV 碎片是分配粒度。要同时做 iteration 调度和 paging，只开一个补不全。
