---
id: nvidia-triton-infer
section: nvidia
order: 8
level: A
title: NVIDIA：Triton Inference Server 动态 batch、多模型、GPU 共享
quick: >-
  Triton 把模型仓库、调度和后端（TensorRT / PyTorch / TensorRT-LLM）拆开。动态 batch 用几毫秒队列把形状
  相同的请求拼成大 batch，换吞吐、加排队延迟。多模型靠 instance group 和并发执行共享一张 GPU；真隔离用
  MIG，不是只开两个 instance。LLM 的 in-flight batching 不是这个动态 batch。
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

## 题怎么来的

NVIDIA 推理 / 系统面常问「模型怎么在 GPU 上跑起来」，不是再写一遍 attention。我会先把 Triton 说成多模型网关：动态 batch、版本、ensemble、TensorRT / TensorRT-LLM 后端。评委要听调度和共享，不接受「我们用 FastAPI 包一层」。LLM 的连续批处理见 `nvidia-paged-kv`，那是另一条调度轴，先分清。

## 动态 batch 在干什么

来一个请求就 launch 一次 GPU，batch 为 1 把 Tensor Core 浪费掉。Dynamic batcher：请求在队列里等到凑够 `preferred_batch_size`、或超过 `max_queue_delay_microseconds`、或碰到 `max_batch_size`，再送进后端。形状、dtype 要对齐；动态维要用 padding 或 backend 自己的 ragged 支持。这是延迟换吞吐：p50 可能几乎不变，p99 会被队列延迟抬起来。SLA 是 20ms 的交互接口，delay 开 8ms 就要小心。

适合：图像、embedding、encoder、LLM prefill 这种计算墙、batch 越大越满。不适合：已经是延迟墙、而且请求长度差很多、padding 浪费算力的场景。LLM decode 每步 query 长度是 1，经典动态 batch 还要求「同一时刻一群请求一起进、一起出」，短序列要等长序列，这正是 in-flight / continuous batching 要打破的。

配置里我还会看是否保序、有没有优先级队列、以及是否按输入长度分桶。分桶能减 padding，等于间接减气泡。

## 多模型和 GPU 共享

一个 model repository 里可以挂很多模型、每个模型多个 version。`instance_group` 决定副本数和绑哪张卡。默认同一张 GPU 上 Triton 可以 concurrent model execution：两个模型的 kernel 交错，前提是显存都放得下、而且没有自己把设备占死。

共享的三个档次，面试要分开：

1. 时间片 / 并发 kernel：最便宜，抢 SM 和 HBM。一个大模型 prefill 能把另一个的 p99 打穿。
2. CUDA MPS：多个上下文在同一 SM 调度，隔离弱于 MIG，好于完全裸奔。
3. MIG：把一张 A100/H100 切成硬件实例，QoS 最硬，容量也切没了。

只说「开两个 instance」而不说显存水位和干扰，评委会追「那大模型来一个请求，小模型还稳吗」。实测要用隔离流量打 noisy neighbor，看 Nsight Systems 上两套 kernel 是否互踩。

Ensemble：tokenizer、主模型、detok 在 Triton 图里串起来，避免 Python 客户端来回拷。BLS（Business Logic Scripting）适合有分支的逻辑。CPU 预处理用 pinned memory / shared memory，别让 HtoD 成为第二条气泡。

## LLM 后端不要套错调度

TensorRT-LLM 后端自己做 in-flight batching：请求在 decode 循环里随时进出，KV 用 paged block，见 `nvidia-paged-kv`。这时 Triton 侧的动态 batch 往往只负责把请求送进 LLM 引擎，真正的 GPU 占用率由引擎的 scheduler 决定。把 `max_queue_delay` 调很大，只会让首 token 更慢，填不满 decode 的空洞。

多 LoRA 同服务见 `nvidia-lora-serve`：那是权重共享，不是再复制一份 Triton 模型。

## 追问

- **preferred_batch_size 写成 1,2,4,8？** 告诉 scheduler 这些尺寸有特化 kernel（TensorRT 动态 shape 的 tactic）。乱写一串质数没有意义，要对着 profile 过的 tactic。
- **一张卡跑两个 70B？** 先算权 + KV。放不下就不是调度问题。放得下再谈 MPS / 优先级，否则先切量化或拆卡。
- **为什么线上关了动态 batch 反而稳？** 流量已经是大 batch，或 p99 SLA 吃不进排队。关 delay、靠客户端攒批，有时更可控。
- **和 vLLM 怎么选？** Triton 强在多模型、多后端、企业网关；纯 LLM 吞吐栈很多人直接引擎。NVIDIA 面试两者都能讲，但别把动态 batch 说成 PagedAttention。
- **ensemble 和 BLS 怎么选？** 线性流水用 ensemble 图；有 if/路由用 BLS。别把业务分支塞进模型仓库的 version 切换里。
