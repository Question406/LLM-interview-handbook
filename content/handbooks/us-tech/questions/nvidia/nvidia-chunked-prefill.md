---
id: nvidia-chunked-prefill
section: nvidia
order: 20
level: A
title: NVIDIA：chunked prefill 把长 prompt 切开和 decode 混部
quick: "长输入一次性处理完，会让正在逐 token 生成的请求等太久。Chunked prefill 把输入切成小块，与其他请求的生成步骤放在同一批里处理。块大小受每批 token 预算限制，并要对齐 KV 缓存页；它仍在同一套设备上执行。"
tags:
  - NVIDIA
  - Chunked Prefill
  - TensorRT-LLM
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: SARATHI — Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
    url: https://arxiv.org/abs/2308.16369
    type: primary
  - title: Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
    url: https://arxiv.org/abs/2403.02310
    type: primary
  - title: Long Sequences — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/long-sequence.html
    type: primary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: primary
---

大模型推理分成两个阶段：prefill 一次处理输入，decode 每一步生成一个新 token。长输入如果必须在一次调度中全部处理完，就可能占住 GPU，让其他正在生成的请求停下来等。

Chunked prefill 的做法是把长输入切成块。每轮处理一块输入，同时推进其他请求的 decode。vLLM 使用 chunked prefill 这个名称，TensorRT-LLM 称为 chunked context。Sarathi 和 Sarathi-Serve 讨论了这种减少生成停顿的调度方式。

## 为什么长输入会影响其他请求

Prefill 中，一条序列的 $Q,K,V$ 都是 $[T_{\mathrm{in}}, D]$。输入长度增加时，矩阵乘法可以利用更多计算能力，但整轮执行也可能达到几十至几百毫秒。

Decode 每条请求的 $Q$ 长度为 1，每步要读取权重和历史 KV，通常更受内存带宽限制；一步往往是一两毫秒量级，见 `nvidia-flash-attn`。

如果新请求的整段输入必须在一轮完成，这一轮的时间就由最长输入决定。其他请求的 token 间隔（TPOT / TBT）会突然变长。短请求也可能排队更久，增加首个 token 的等待时间（TTFT）。

此外，`max_num_tokens` 必须容纳最长输入时，每轮工作集会占用更多 HBM 显存，挤压 KV 缓存可用空间，降低并发。请求动态进入和退出批次的机制见 `nvidia-inflight-batch`。

## 一轮里怎么安排请求

设每轮 token 预算为 $U$，对应 TRT-LLM 的 `max_num_tokens`。Sarathi-Serve 的典型安排是：

1. 先为正在 decode 的请求各安排 1 个 token，尽量保持稳定的生成间隔。
2. 若有尚未处理完的输入，安排它的下一块，长度不超过 $U - B_{\mathrm{decode}}$。
3. 还有剩余预算时，接收新请求，但也只处理其输入的一块。

当前块的 $Q$ 只对应新 token，形状大约为 $[B_{\mathrm{mix}}, T_{\mathrm{chunk}}, \ldots]$；$K,V$ 包含已缓存的前缀和当前块。历史前缀在 KV 缓存里，因此分块仍能遵守因果关系。

除最后一块外，TRT-LLM 要求块长度是 KV block size 的整数倍，常见块大小为 64，以便对齐缓存页，见 `nvidia-paged-kv`。

## 块大小为什么需要权衡

Decode 的小矩阵运算需要大量读内存，prefill 块则提供更大的矩阵计算。放在同一轮，可以改善 GPU 利用率，同时避免完整 8k 输入让一轮持续几百毫秒。

$U$ 太大时，单个输入块仍会让生成请求等待；$U$ 太小时，输入被切得太碎，首 token 延迟会变差，内核执行太短，CUDA Graph 也更难使用，见 `nvidia-cuda-graph`。块应大到能有效执行矩阵乘法，又小到每轮时间满足 token 间隔要求。

每轮工作集由 $U$ 决定后，就不必按服务支持的最大输入长度预留。因此，`max_num_tokens` 可以远小于 128k，把更多 HBM 留给 KV 缓存，提高并发。

这不保证每条请求都更快。某条短输入原本一轮就能处理完，现在可能需要与 decode 请求分享预算，TTFT 反而变长。评估应看排队、平均和最坏延迟，不能只看原本最快的请求。

## 和 prefill/decode 分离部署有什么区别

分块调度仍在同一张 GPU、同一轮里混合输入处理和生成。分离部署则把 prefill 与 decode 放在不同设备池，必须跨设备传输 KV。

所以一个是调度方式，一个是部署方式。引擎与 Triton 的集成见 `nvidia-trt-llm` 和 `nvidia-triton-infer`。

## 面试追问

- **每块只放一个 token 行不行？** 会让 prefill 接近逐 token 的 decode，难以利用大矩阵计算，首 token 延迟很差。
- **如何使用 CUDA Graph？** 混合批次的 token 数会变化，完整图较难捕获。常见做法是纯 decode 使用图，带输入块的批次用普通执行或分段图。
- **为什么需要分页 KV？** 分块和动态批处理使各请求的缓存逐步增长。继续按最大长度连续预留，会重新引入浪费与碎片问题。
- **只有长文档，没有交互式生成呢？** 分块仍可降低峰值工作集，但混合调度收益较小，可以考虑更大的 $U$ 或独立 prefill 池。
