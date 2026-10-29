---
id: nvidia-flashinfer
section: nvidia
order: 22
level: A
title: NVIDIA：FlashInfer 的 append KV、sampler，和 vLLM 什么关系
quick: >-
  FlashInfer 提供直接处理 paged、ragged KV 的 attention、append 和 sampling 核，vLLM、SGLang
  负责请求调度和 KV 页管理。我的接法是先让引擎分好页，再调用核写入和计算；sorting-free sampler 能避免 vocabulary
  全排序，但必须保持原来的 sampling 分布。
tags:
  - NVIDIA
  - FlashInfer
  - vLLM
  - Sampling
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      FlashInfer — Efficient and Customizable Attention Engine for LLM Inference
      Serving
    url: 'https://arxiv.org/abs/2501.01005'
    type: primary
  - title: Run High-Performance LLM Inference Kernels from NVIDIA Using FlashInfer
    url: >-
      https://developer.nvidia.com/blog/run-high-performance-llm-inference-kernels-from-nvidia-using-flashinfer/
    type: secondary
  - title: flashinfer-ai/flashinfer
    url: 'https://github.com/flashinfer-ai/flashinfer'
    type: primary
  - title: Sorting-Free GPU Kernels for LLM Sampling
    url: 'https://flashinfer.ai/2025/03/10/sampling.html'
    type: primary
---

## 可以这样回答

FlashInfer 负责推理 kernel，vLLM、SGLang 和自研引擎负责调度请求、分配 KV 页，两层可以组合使用。比如 append 核写新 KV 前，引擎必须已经分好页，核本身不会替你决定容量。Ye 等人的论文讨论 serving attention 引擎，NVIDIA 博客也说明了把 TRT-LLM 中优化过的核提供给 FlashInfer 的做法；引擎定位见 `nvidia-trt-llm`。

FlashAttention 解决的是「别把 $[T,T]$ 写进 HBM」，训练 / 连续 prefill 最赚，见 `nvidia-flash-attn`。Serving 的 KV 不是连续的：页大小固定、序列长短不一、还有共享前缀。FlashInfer 把 KV 看成 **block-sparse**，核直接按 page index gather，不必先 gather 成连续缓冲再跑 FA。论文还写 JIT 模板：causal、sliding window、GQA、MLA，一种调度多种变体。

## 技术备查

FlashInfer 负责推理 kernel，vLLM、SGLang 和自研引擎负责调度请求、分配 KV 页，两层可以组合使用。比如 append 核写新 KV 前，引擎必须已经分好页，核本身不会替你决定容量。Ye 等人的论文讨论 serving attention 引擎，NVIDIA 博客也说明了把 TRT-LLM 中优化过的核提供给 FlashInfer 的做法；引擎定位见 `nvidia-trt-llm`。

## Attention 如何适配 serving

FlashAttention 解决的是「别把 $[T,T]$ 写进 HBM」，训练 / 连续 输入 prefill 最赚，见 `nvidia-flash-attn`。Serving 的 KV 不是连续的：页大小固定、序列长短不一、还有共享前缀。FlashInfer 把 KV 看成 **block-sparse**，核直接按 page index gather，不必先 gather 成连续缓冲再跑 FA。论文还写 JIT 模板：causal、sliding window、GQA、MLA，一种调度多种变体。

调度和 CUDA Graph 的缝：IFB 每步 $T_i$ 都在变，Graph 要静态配置。FlashInfer 把 **tile 尺寸** 留在编译期，把 **各请求的 KV 长度** 留在运行期调度，用 load-balanced 的 split 让长序列多拿 CTA、短序列少拿，和 `nvidia-flash-decode` 的 split-K 是同一类 occupancy 药。Wrapper 名字面试能说即可：`BatchDecodeWithPagedKVCacheWrapper`、`BatchPrefillWithPagedKVCacheWrapper`。POD-Attention 把同一步里的 prefill 行和 逐 token 生成（decode） 行融进一个核，对应 chunked / inflight 混部，见 `nvidia-chunked-prefill`、`nvidia-inflight-batch`。

Cascade attention：共享 system prompt 的页只算一次，再和各请求私有后缀拼 softmax。这是 kernel 支持 prefix 共享，物理页怎么 refcount 仍是 vLLM 的 block table，见 `nvidia-paged-kv`。

## KV 写入和 sampling 还要做什么

Decode 一步要：(1) 读历史 KV 做 attention；(2) 把本步新的 $K,V$ 写进当前页的空槽。朴素实现是两个 kernel，中间还夹 RoPE。页满了还要让调度器先从 free list 拿新页，**append 假定空间已经留好**（文档写得很死：`kv_indices` / `indptr` / `kv_last_page_len` 必须已经计入新 token）。

形状（NHD）：页池 $[P_{\max}, B_{\mathrm{page}}, H_{\mathrm{kv}}, d_h]$，一次 append 的 $K_{\mathrm{new}}$ 是 $[N_{\mathrm{append}}, H_{\mathrm{kv}}, d_h]$。$N_{\mathrm{append}}$ 在纯 decode 里等于瞬时 batch，在 chunked prefill 里等于这一块的 token 数。核做的是间接写：按 `(batch_idx, position)` 算落在哪一页的哪一槽。和 attention 融，能少一次 HBM round-trip；vLLM 后来接的 RoPE + paged append fusion 就是这条。这里的公式仍是 $QK^{\top}V$，append 处理的是 cache 的写入路径，要单独考虑页地址与写入顺序。

RoPE 必须在写入页之前做：cache 里存的是旋转后的 $K$，下一步 decode 只读不转。融合核的常见顺序是 QKV 投影 → RoPE → 写 K/V 进 page → 用同一份 $Q$ 打 paged attention。拆开写会多一次对页池的 store/load；融错顺序会把未旋转的 $K$ 留下，后面整段上下文的分数全歪。

sampling 阶段也可能成为瓶颈。一步 transformer 结束之后还要从 $[B, V]$ 的 logits 里抽 token。$V=128\mathrm{k}$ 时 GPU 上做完整 sort 的实际耗时可以碰到 attention 同量级，尤其是小 batch decode。FlashInfer 的博客：过滤（top-$k$ / top-$p$ / min-$p$）加 sampling 可以 **sorting-free**，用 dual-pivot rejection，最坏对数级，而不是 $V\log V$。数值上要保持和「先滤再多项式」同一分布，不能图快改 sampling 定义。

投机路径另有 `chain_speculative_sampling`：草稿 token 和两套概率进一个核，按 $p/q$ rejection sampling，输出接受前缀再加一个 bonus token。这是 sampling 核，不是草稿怎么生成。Medusa / EAGLE 见 `nvidia-spec-medusa`。

NVIDIA 博客把工作负载拆成四族：Attention、GEMM、Communication、Sampling。FlashInfer 覆盖其中可模板化的几族；线性层仍常走 CUTLASS / cuBLAS。面试别说「换 FlashInfer 等于换了整个引擎」。

从整套服务看，vLLM 拥有：请求队列、continuous batching、KV 页分配、prefix 共享策略、分布式 TP。FlashInfer 拥有：打在这些页上的 attention / append / sampler 核，以及 JIT。Hopper 上 vLLM 默认常常仍是 FlashAttention 后端，FlashInfer 用环境变量或 `--attention-backend` 打开；Blackwell 上官方叙事是 FlashInfer 更常做默认。TRT-LLM 是另一套引擎，同样可以调 FlashInfer 或自有 plugin，见 `nvidia-trt-llm`。三者不是替代关系：调度 vs 核 vs NVIDIA 编译栈。

## 追问

**能不能当训练核用？**
不是为反向设计的。没有 $P$ 重算那套，别拿它换 Megatron 的 FA。

**JIT 和 CUDA Graph？**
JIT 出固定 tile 的核；Graph 捕获的是 launch 配置。IFB 仍要 pad 到已捕获的 batch / token 档，见 `nvidia-cuda-graph`。

**append 和 attention 必须融合吗？**
不是正确性要求。融合省 launch 和一次写；页池和 RoPE dtype 对不齐时先分核更稳。

**sampler 改了分布怎么办？**
先对 CPU 参考实现做分布检验。加速不能以改 top-$p$ 语义为代价。
