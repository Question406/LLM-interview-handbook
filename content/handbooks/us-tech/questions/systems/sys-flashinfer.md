---
id: sys-flashinfer
section: systems
order: 24
level: S
title: 系统：FlashInfer 推理核库，append、sampling、调度器接口
quick: >-
  FlashInfer 是核库不是调度器。调度器管 batch、页表、谁进谁出；核只吃 indptr、indices、last_page_len
  做 attention / append / sampling。页表没先留好坑，append 可能写入错误位置。CUDA graph 要求这些元数据形状固定。
tags:
  - NVIDIA
  - vLLM
  - SGLang
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Accelerating Self-Attentions for LLM Serving with FlashInfer
    url: https://flashinfer.ai/2024/02/02/introduce-flashinfer.html
    type: primary
  - title: flashinfer.page.append_paged_kv_cache
    url: https://docs.flashinfer.ai/generated/flashinfer.page.append_paged_kv_cache.html
    type: primary
  - title: Sorting-Free GPU Kernels for LLM Sampling — FlashInfer
    url: https://flashinfer.ai/2025/03/10/sampling.html
    type: secondary
  - title: flashinfer-ai/flashinfer
    url: https://github.com/flashinfer-ai/flashinfer
    type: primary
---

## 题怎么来的

vLLM、SGLang、TensorRT-LLM、TGI 都把注意力、paged KV、采样从 Python 调度器里拆出去。NVIDIA kernel 岗爱问：逐 token 生成（decode） / 输入预填充（prefill，即处理输入并建立缓存） / append 三个阶段的瓶颈分别是什么、采样为什么不要先 sort。OpenAI serving 岗爱问：CUDA graph 捕获之后，调度器还能不能每步改 batch。FlashInfer 的公开博客把 self-attention 拆成 prefill、decode、append 三阶段，正好当这张接口图。分页语义见 `sys-paged-attn`；调度见 `sys-cont-batch` 和 `sys-decode-batch`。

## 核库吃什么、不吃什么

我会先画边界：调度器持有请求状态（哪些序列在飞、每条的 block table、本步是 prefill 块还是 decode、采样参数）。核库拿到的是已经摊平的 GPU 张量。

- **Attention：** $Q$ 加上 paged $K/V$。Decode 是 $T_q=1$ 的 memory-bound；prefill 是长 $T_q$ 的 compute-bound；append（已有前缀再吃一段新 token，chunked prefill 或多轮续写）介于两者之间。
- **Page 元数据：** `kv_indices`、`kv_indptr`（CSR 式，形状 `[B+1]`）、`kv_last_page_len`。页可以是 NHD `[max_pages, page_size, n_{\mathrm{kv}}, d_h]` 或 HND。SGLang 一类为了 radix 灵活性常用 `page_size=1`，FlashInfer 把页表预取进 shared memory，避免页太碎时，间接访问成为性能瓶颈。
- **Append：** 新 $K/V$ 写入已经分配好的页。文档写明：调用前 `kv_indices` / `indptr` / `last_page_len` 必须已经包含新 token 的坑。核不会帮你 malloc。
- **Sampling：** 另一组核。logits `[B, V]` 上 fused temperature、top-$k$、top-$p$，拒绝采样、尽量不全局 sort。和注意力不是一个 launch。

接口边界一句话：策略在调度器，数据平面在核。谁该抢占、prefix 是否命中、agent 等工具时要不要把序列摘出 batch，核一律不知情。

```python
# 调度器先扩页表，再让核写 K/V。坑必须已经在 indices 里。
flashinfer.append_paged_kv_cache(
    k_append, v_append, batch_indices, positions,
    paged_kv_cache, kv_indices, kv_indptr, kv_last_page_len,
)
next_ids = flashinfer.sampling.top_k_top_p_sampling_from_logits(
    logits, top_k, top_p,
)
```

`append` 假设空间已分配；没扩表就调用，是实现 bug，不是「核会自动增长 cache」。

## 和调度器、CUDA graph 的接缝

Iteration-level 调度每步 $B$ 在变，结束序列腾页、新请求插入，见 `sys-decode-batch`。核希望本步元数据已经在 GPU 上、形状对得上捕获图：

- **CUDA graph：** 捕获的是固定 shape 的 launch。`B`、`kv_indptr` 长度、workspace 都要 pad 到捕获时的上限。实际活着的序列数 $B_{\mathrm{live}}\lt B_{\mathrm{graph}}$ 时，用 mask / 有效长度，不要每步重新捕获。seed、`top_k` 若走 graph，要用 GPU 上的 tensor 而不是 Python 标量，FlashInfer 采样 API 为此留了 tensor `seed`。图捕获本身见 `nvidia-cuda-graph`。
- **POD / 混合步：** 公开核可以把 prefill 块和 decode 打进同一次 attention，对应 chunked prefill 混部，见 `sys-chunked-prefill`。调度器决定本步 token 预算，核只看见 packed $Q$ 和各自的 KV 区间。
- **Cascade / 共享前缀：** 公共 KV 和私有 KV 分两段 attention 再合并，给 radix / prefix 共享少读一遍公共页，见 `sys-radix-tree`。

错误说法：FlashInfer 等于 vLLM；append 会自己向 CPU malloc；采样必须先对词表排序；把调度逻辑写进 CUDA 才能快。前三个是接口错；最后一个把不该进核的策略塞进核，graph 和调试都会坏。

NVIDIA 岗可能追 Nsight：decode 步是 HBM SOL 还是 launch 太碎。答案通常是 fused attention + fused sampling、减少 Python 往返；SGLang 的 overlap scheduler 在 GPU 跑本步时 CPU 组下一步的 indptr，正是为了填这条缝。

监控不要只报 kernel TFLOPS。Decode 看 HBM 带宽利用率；prefill 看 Tensor Core；append 看页表 gather 是不是把 L2 打穿。页大小和 `sys-paged-attn` 同一权衡：太小，间接访问多；太大，内部碎片和 radix 分叉浪费。

## 追问

- **Prefill / decode / append 为什么要三套核？** $T_q$ 和 KV 长度差一个数量级，tile 和流水不同。一套核要么浪费算力，要么浪费带宽。
- **为什么 append 不负责分配？** 分配是调度器和页池的事，可能还要抢占、卸到 CPU。核只写字节。
- **Sampling 为什么尽量不 sort？** $V$ 十万级，逐步 decode 每步全排序比 GEMM 还贵。拒绝采样在核内多轮，blog 有公开推导。
- **和调度器谁拥有 block table？** 调度器。核拿的是拷到 GPU 的视图。树结构（radix）在 CPU，见 `sys-radix-tree`。
- **CUDA graph 和动态 $B$ 怎么共存？** 捕获几档上限，pad 到最近档；有效条数用 `last_page_len` / mask。每步 $B$ 变就重捕获，启动开销吃掉 decode。
- **page_size=1 会不会很慢？** 朴素 kernel 会。FlashInfer 预取页号，SGLang 用 1 是为了树节点灵活，不是因为 1 在 roofline 上最优。
