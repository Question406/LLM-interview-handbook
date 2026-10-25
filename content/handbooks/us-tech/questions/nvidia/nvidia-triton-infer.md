---
id: nvidia-triton-infer
section: nvidia
order: 8
level: A
title: NVIDIA：Triton Inference Server 动态 batch、多模型、GPU 共享
quick: "Triton Inference Server 管模型仓库、调度和后端接入。动态 batch 会短暂排队，把兼容请求合并执行，用排队延迟换吞吐；多模型可以用 instance group 共享 GPU，更强的硬件隔离用 MIG。LLM decode 的请求进出则由 TensorRT-LLM 等引擎的 in-flight 调度处理。"
tags:
  - NVIDIA
  - Triton
  - Inference
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Triton Inference Server documentation
    url: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html
    type: primary
  - title: Triton Inference Server
    url: https://github.com/triton-inference-server/server
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
---

Triton Inference Server 负责接入和调度模型请求：管理模型版本、选择后端、合并 batch，也能把多个模型串成执行流程。比如单个图像请求的 batch 只有 1，GPU 没吃满，可以等一小会儿合并兼容请求；代价是这些请求多了一段排队时间。

我会先说明动态 batch 怎么取舍吞吐和延迟，再讲多模型共享 GPU。LLM 连续批处理的 KV 管理见 `nvidia-paged-kv`，它还需要引擎在生成循环里安排请求的进出。

## 动态 batch 在干什么

如果一个请求就 launch 一次、每次 batch 为 1，Tensor Core 可能利用不足。Dynamic batcher 让请求短暂排队，凑到 `preferred_batch_size`、等过 `max_queue_delay_microseconds`，或碰到 `max_batch_size`，再交给后端。形状、dtype 要对齐；动态维要用 padding 或 backend 自己的 ragged 支持。这是延迟换吞吐：p50 可能几乎不变，p99 会被队列延迟抬起来。SLA 是 20ms 的交互接口，delay 开 8ms 就要小心。

图像、embedding、encoder 和 LLM prefill 等受计算限制的任务，通常更容易从大 batch 获益。若已经主要受延迟限制，或请求长度差很多、padding 开销大，就要谨慎设置排队。LLM 逐 token 生成（decode） 每步 query 长度是 1，经典动态 batch 还要求「同一时刻一群请求一起进、一起出」，短序列要等长序列，这正是 in-flight / continuous batching 要打破的。

配置里我还会看是否保序、有没有优先级队列、以及是否按输入长度分组统计。分组统计能减 padding，等于间接减气泡。

## 多模型和 GPU 共享

一个 model repository 里可以挂很多模型、每个模型多个 version。`instance_group` 决定副本数和绑哪张卡。默认同一张 GPU 上 Triton 可以 concurrent model execution：两个模型的 kernel 交错，前提是显存都放得下、而且没有自己把设备占死。

共享方式取决于要多强的隔离。直接时间片或并发 kernel 成本低，但会争 SM、HBM，大模型一次 prefill 就可能影响小模型 p99。CUDA MPS 可以让多个上下文在同一 SM 调度，隔离强于直接共享、弱于 MIG。MIG 把 A100/H100 切成硬件实例，QoS 更强，同时把可用容量也切开了。

设置两个 instance 后，还要验证显存水位和互相干扰。用分开的流量制造 noisy neighbor，再看 Nsight Systems 上两组 kernel 的重叠和等待，确认大模型到达时小模型能否守住延迟。

tokenizer、主模型、detok 这类线性流程可以放进 ensemble 图，减少 Python 客户端来回拷贝；带分支的逻辑用 BLS（Business Logic Scripting）。CPU 预处理可用 pinned memory、shared memory，避免 HtoD 又成为等待来源。

TensorRT-LLM 后端自己做 in-flight batching：请求在 decode 循环里随时进出，KV 用 paged block，见 `nvidia-paged-kv`。这时 Triton 侧的动态 batch 往往只负责把请求送进 LLM 引擎，真正的 GPU 占用率由引擎的 scheduler 决定。把 `max_queue_delay` 调很大，只会让首 token 更慢，填不满 decode 的空洞。

多 LoRA 同服务见 `nvidia-lora-serve`：那是权重共享，不是再复制一份 Triton 模型。

## 追问

**preferred_batch_size 写成 1,2,4,8？**
应按 profile 过的 TensorRT 动态 shape tactic 来选这些尺寸，让 scheduler 优先组成有高效 kernel 的 batch；随手列一串质数没有依据。
**一张卡跑两个 70B？**
先算权重和 KV 能否放下。容量够了再测 MPS、优先级和干扰；容量不够，就先比较量化或跨卡拆分。
**为什么线上关了动态 batch 反而稳？**
流量已经是大 batch，或 p99 SLA 吃不进排队。关 delay、靠客户端攒批，有时更可控。
**和 vLLM 怎么选？**
Triton 适合多模型、多后端和企业网关；纯 LLM 吞吐服务也常直接使用引擎。先按系统职责选，再比较性能；动态 batch 与 PagedAttention 的缓存管理分别讨论。
**ensemble 和 BLS 怎么选？**
线性流程用 ensemble 图，有 if 或路由用 BLS。模型仓库的 version 管版本，不承担业务分支。
