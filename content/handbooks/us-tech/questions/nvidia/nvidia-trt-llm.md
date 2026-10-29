---
id: nvidia-trt-llm
section: nvidia
order: 13
level: A
title: NVIDIA：TensorRT-LLM 相对 vLLM / Triton 的定位，plugin、inflight、量化
quick: >-
  TensorRT-LLM 和 vLLM 负责 LLM 引擎执行及逐轮调度，Triton Inference Server
  负责模型接入、多后端和网关功能。TensorRT-LLM 用 plugin 和相应 kernel 处理 attention、GEMM 与量化，runtime
  管 in-flight batching 和 paged KV；选择时要分别评估执行、调度和服务接入。
tags:
  - NVIDIA
  - TensorRT-LLM
  - Inference
  - Serving
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      NVIDIA TensorRT-LLM Supercharges Large Language Model Inference on NVIDIA
      H100 GPUs
    url: >-
      https://developer.nvidia.com/blog/nvidia-tensorrt-llm-supercharges-large-language-model-inference-on-nvidia-h100-gpus/
    type: secondary
  - title: TensorRT-LLM Overview
    url: 'https://nvidia.github.io/TensorRT-LLM/overview.html'
    type: primary
  - title: >-
      Efficient Memory Management for Large Language Model Serving with
      PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
  - title: NVIDIA TensorRT-LLM
    url: 'https://github.com/NVIDIA/TensorRT-LLM'
    type: primary
---

## 可以这样回答

我会按职责来放这三个组件：TensorRT-LLM 和 vLLM 都负责 LLM 如何执行和调度，Triton Inference Server 负责模型接入、版本、多后端和服务编排。比如请求从 Triton 进入 TensorRT-LLM backend 后，生成循环里哪个请求占用 KV、哪个请求下一轮进入 batch，是引擎自己的 scheduler 决定的。

TensorRT-LLM 把模型定义组织成执行计划，也有 PyTorch 路径，执行时使用 GPT Attention plugin、GEMM plugin 和量化 kernel，并配合 paged KV、in-flight batching、chunked prefill。多卡 TP、PP、EP 在模型定义中安排，HTTP、模型仓库和 A/B 则交给服务层。

## 技术备查

我会按职责来放这三个组件：TensorRT-LLM 和 vLLM 都负责 LLM 如何执行和调度，Triton Inference Server 负责模型接入、版本、多后端和服务编排。比如请求从 Triton 进入 TensorRT-LLM backend 后，生成循环里哪个请求占用 KV、哪个请求下一轮进入 batch，是引擎自己的 scheduler 决定的。

NeMo 训练后导出引擎也会接到这条路径。下面分别讲执行计划与 plugin，以及 in-flight 调度和量化各解决什么。

TensorRT-LLM 把模型定义组织成执行计划，也有 PyTorch 路径，执行时使用 GPT Attention plugin、GEMM plugin 和量化 kernel，并配合 paged KV、in-flight batching、chunked prefill。多卡 TP、PP、EP 在模型定义中安排，HTTP、模型仓库和 A/B 则交给服务层。

vLLM 是另一套引擎加 serving。PagedAttention 论文从那边来；continuous batching 和 TRT-LLM 的 in-flight 是同一调度粒度。强项是改 kernel、改调度都在 Python/CUDA 栈里，迭代快。比较时先对齐相同的执行与调度语义，再解释 TRT-LLM 的编译器和 plugin 路径。分页对比见 `nvidia-paged-kv`。

Triton Inference Server 在服务层提供动态 batch、ensemble、多后端和 metrics。LLM 路径上它把请求送进 TensorRT-LLM backend，真正的 GPU 占用由引擎 scheduler 决定。Triton 的 `max_queue_delay` 是把形状相同的请求拼成一次 launch，要求一起进、一起出。LLM 逐 token 生成（decode） 长度差几个数量级，这套对不上。Triton 怎么配见 `nvidia-triton-infer`。

## Plugin 在补什么

朴素 TensorRT 吃固定形状 CNN / Encoder 很稳。autoregressive LLM 每步 query 长度是 1、KV 变长、还要 RoPE / 量化 / paged gather，计算图会被拆成一串小 kernel。Plugin 把这些操作融合成自定义 op：

- **GPT Attention plugin**：context 走 FMHA（FlashAttention 一类，不物化 $[T, T]$），generation 走 masked MHA，原地写 KV。RoPE、QKV bias、KV 的量化 / 反量化可以在核里做。关掉 context FMHA 会把 $QK^{\top}$ 写回 HBM，长 prompt 会大幅增加显存占用和带宽需求。
- **GEMM plugin**：cuBLAS / 量化 GEMM，Hopper 上 FP8 走 Tensor Core。
- **remove_input_padding**：变长序列 packed，不再为对齐 pad 到 `max_seq_len`。

这些 plugin 负责让执行计划支持 KV cache 和 in-flight 调度的间接索引，并避免把 attention 矩阵完整写回显存。FlashAttention 的 IO 账见 `nvidia-flash-attn`。

## 调度与量化分别解决什么

In-flight batching 每轮释放已结束序列的槽位，让新请求补入，context、generation 也可在同一步执行。它处理请求调度，依赖 paged KV，细节见 `nvidia-inflight-batch`。

量化改变张量 dtype 和对应 kernel：Hopper 可用 FP8 权重、激活，KV 另行设成 FP8；INT8 SmoothQuant、INT4 AWQ / GPTQ 则是其他配方。权重和 KV 分开配置，见 `nvidia-fp8`、`nvidia-fp8-kv`、`nvidia-int8-quant`。

小 batch 受带宽限制时，先考虑压权重、减少读取 $W$。大 batch 受计算限制时，激活也量化才可能更充分使用 Tensor Core。长上下文还要单算 KV，权重已量化而 KV 仍 fp16，照样可能 OOM。

## 追问

**为什么不直接用 TensorRT 建 LLM？**
普通 TensorRT 可以建 encoder。decode 的动态 KV、inflight 和 paged gather 还需要 plugin、runtime 配合，仅增加 optimization profile 不足以完成整个循环。
**和 vLLM 怎么选？**
如果重点是 NVIDIA 编译栈、FP8 / FP4 和 Triton / NIM 生产接入，可优先评估 TRT-LLM；需要快速改 kernel、跟进社区模型时，可优先评估 vLLM。比较时把相同调度粒度对齐。
**Plugin 和 CUDA Graph 谁先？**
Plugin 决定图里有哪些大核；Graph 把 decode 那串 launch 收成一次 replay，见 `nvidia-cuda-graph`。先融合再捕获。
**NeMo 在哪？**
NeMo 与 Megatron-Core 负责训练、对齐，之后可导出到 TRT-LLM 或 NIM，推理执行由后者承担。

## 相关题

- [[nvidia-w4a8]]：本题「量化」那一层的展开，讲 TRT-LLM 里权重、激活、KV 三个量化开关分别省什么。
