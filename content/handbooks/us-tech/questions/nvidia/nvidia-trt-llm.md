---
id: nvidia-trt-llm
section: nvidia
order: 13
level: A
title: NVIDIA：TensorRT-LLM 相对 vLLM / Triton 的定位，plugin、inflight、量化
quick: >-
  TensorRT-LLM 是 LLM 引擎：注意力 / GEMM / 量化走 TensorRT plugin，runtime 做 in-flight batch
  和 paged KV。vLLM 是同一套 serving 语义的 Python 栈，PagedAttention 从那边来。Triton 是网关，不是第三套
  attention。别把 Triton 动态 batch 说成 inflight。
tags:
  - NVIDIA
  - TensorRT-LLM
  - Inference
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: NVIDIA TensorRT-LLM Supercharges Large Language Model Inference on NVIDIA H100 GPUs
    url: https://developer.nvidia.com/blog/nvidia-tensorrt-llm-supercharges-large-language-model-inference-on-nvidia-h100-gpus/
    type: secondary
  - title: TensorRT-LLM Overview
    url: https://nvidia.github.io/TensorRT-LLM/overview.html
    type: primary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: NVIDIA TensorRT-LLM
    url: https://github.com/NVIDIA/TensorRT-LLM
    type: primary
---

## 题怎么来的

NVIDIA LLM 推理 / CUDA 岗爱问「TRT-LLM、vLLM、Triton 你怎么摆」。我会先画三层，再落到 plugin、in-flight batch、量化三件产品功能。NeMo 训完导出引擎也走这条。要讲职责切分，别答「都是推理框架」四个字。

## 三层各管什么

TensorRT-LLM 是引擎。模型定义（现在也走 PyTorch 路径）编成执行计划：GPT Attention plugin、GEMM plugin、量化 kernel、paged KV、in-flight batching、chunked prefill。多卡 TP / PP / EP 写在模型定义里。它不管 HTTP、模型仓库、A/B。

vLLM 是另一套引擎加 serving。PagedAttention 论文从那边来；continuous batching 和 TRT-LLM 的 in-flight 是同一调度粒度。强项是改 kernel、改调度都在 Python/CUDA 栈里，迭代快。NVIDIA 面不要贬 vLLM；要说「语义对齐，编译器和 plugin 是 TRT-LLM 的差」。分页对比见 `nvidia-paged-kv`。

Triton Inference Server 是网关：动态 batch、ensemble、多后端、metrics。LLM 路径上它把请求送进 TensorRT-LLM backend，真正的 GPU 占用由引擎 scheduler 决定。Triton 的 `max_queue_delay` 是把形状相同的请求拼成一次 launch，要求一起进、一起出。LLM decode 长度差几个数量级，这套对不上。Triton 怎么配见 `nvidia-triton-infer`。

Triton 管进出；TRT-LLM / vLLM 管一步 transformer 怎么跑。

## Plugin 在补什么

朴素 TensorRT 吃固定形状 CNN / Encoder 很稳。自回归 LLM 每步 query 长度是 1、KV 变长、还要 RoPE / 量化 / paged gather，图里会炸成一串小核。Plugin 把这些收成自定义 op：

- **GPT Attention plugin**：context 走 FMHA（FlashAttention 一类，不物化 $[T, T]$），generation 走 masked MHA，原地写 KV。RoPE、QKV bias、KV 的量化 / 反量化可以在核里做。关掉 context FMHA 会把 $QK^{\top}$ 写回 HBM，长 prompt 显存和带宽一起爆。
- **GEMM plugin**：cuBLAS / 量化 GEMM，Hopper 上 FP8 走 Tensor Core。
- **remove_input_padding**：变长序列 packed，不再为对齐 pad 到 `max_seq_len`。

面试别背插件名单。一句话：没有 plugin，编译器不知道 KV cache 和 inflight 的间接索引，只会生成「先物化 attention 矩阵」的慢图。FlashAttention 的 IO 账见 `nvidia-flash-attn`。

## Inflight 和量化别并成「都优化了」

In-flight batching：每个 iteration 结束的序列立刻腾槽，新请求插进来，context 和 generation 可以同一步。这是调度，依赖 paged KV，细节见 `nvidia-inflight-batch`。量化是 dtype 和 kernel：Hopper 上权 / 激活 FP8，KV 还可以单独 FP8；INT8 SmoothQuant、INT4 AWQ / GPTQ 是另一组配方。权重量化和 KV 量化不是一把开关，见 `nvidia-fp8`、`nvidia-fp8-kv`、`nvidia-int8-quant`。

小 batch、带宽墙：先压权重，少读 $W$。大 batch、算力墙：激活也量化才喂满 Tensor Core。只能量化权重却把 KV 留 fp16，长上下文照样 OOM。

## 追问

- **为什么不直接用 TensorRT 建 LLM？** 能建 encoder。Decode 的动态 KV、inflight、paged gather 要 plugin 和 runtime，不是再开一个 optimization profile 就完事。
- **和 vLLM 怎么选？** 要 NVIDIA 编译栈、FP8 / FP4、Triton / NIM 生产网关，走 TRT-LLM。要快改 kernel、社区模型，走 vLLM。面试两者的调度名词要对得上。
- **Plugin 和 CUDA Graph 谁先？** Plugin 决定图里有哪些大核；Graph 把 decode 那串 launch 收成一次 replay，见 `nvidia-cuda-graph`。先融合再捕获。
- **NeMo 在哪？** 训练 / 对齐走 NeMo + Megatron-Core，导出 TRT-LLM 或 NIM。NeMo 不是推理引擎。
