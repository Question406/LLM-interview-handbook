---
id: amazon-trainium
section: amazon
order: 10
level: S
title: Amazon：Trainium / Neuron 上训 LLM，和 GPU 栈公开层差在哪？
quick: "Trainium 与 GPU 的主要差异在编译器、集合通信和自定义内核。GPU 常用 CUDA / NCCL，Trainium 用 Neuron 编译、aws-neuronx-collectives 和 NKI，形状与并行切分也要适配。迁移先验证数值，再测编译时间、吞吐和恢复，公开材料之外的内部架构不推测。"
tags:
  - Amazon
  - Trainium
  - Neuron
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: AWS Trainium
    url: https://aws.amazon.com/machine-learning/trainium/
    type: primary
  - title: AWS Neuron SDK
    url: https://aws.amazon.com/ai/machine-learning/neuron/
    type: primary
  - title: End-to-end LLM training on instance clusters with over 100 nodes using AWS Trainium
    url: https://aws.amazon.com/blogs/machine-learning/end-to-end-llm-training-on-instance-clusters-with-over-100-nodes-using-aws-trainium/
    type: primary
  - title: Collective Communication — AWS Neuron
    url: https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/arch/neuron-features/collective-communication.html
    type: primary
---

从 GPU 迁到 Trainium，主要要适配编译、通信和自定义内核，优化器仍可以是熟悉的 Adam。PyTorch 前端看起来相近，并不表示 Triton 或 FlashAttention 能直接搬过去。Trainium 是 AWS 的训练加速器，Neuron 是其软件栈，与 CUDA 栈不同。

AWS 的公开 Trn1 预训练配方包括激活重计算、张量 / 流水 / 序列 / 数据并行，以及 BF16 加 stochastic rounding。评估迁移时看成本、可复现性和故障诊断，门禁见 `amazon-lp-ml`。

## 从编译到内核逐层适配

GPU 常见 eager 路径会立即执行 CUDA kernel；Neuron 历史上走 XLA / `neuronx-cc` 图编译，先追图再生成 NeuronCore 指令。动态 `seq_len`、MoE 路由和数据依赖控制流可能增加编译与适配困难。公开配方的 `--model-type=transformer`、`--distribution-strategy=llm-training` 会告诉编译器如何处理切分后的参数、梯度和优化器状态。Native PyTorch / `torch.compile` 改善迭代体验，高性能路径仍需编译。

集合通信从 NCCL 换到 Neuron collectives，单机走 NeuronLink，跨机走 EFA；对应公开库包括 aws-neuronx-collectives。编译器先生成 all-reduce 占位，runtime 按拓扑实现。文档描述了专用通信硬件，允许下一层梯度计算与上一层 all-reduce 重叠。连通性测试用 `nccom-test`，GPU 上的 `nccl-tests` 不适用。

自定义算子从 CUDA / Triton 的 warp、shared memory 模型，换成公开的 tensor / vector / scalar 引擎与 SBUF、PSUM 缓冲，使用 NKI，FlashAttention 的 `.cu` 不能直接复制。HuggingFace Optimum Neuron、NeuronX Distributed 和部分 TorchTitan 路径可减少模型代码改动，但手写 attention、fused cross-entropy、自定义量化核仍需重写。`nn.Linear` 往往比这些自定义核好迁。

FSDP、DDP、张量并行接口可以类似 PyTorch，但切分单位是 NeuronCore。`trn1.32xlarge` 的核数不能直接称作「32 卡」，也不能直接照搬 Megatron 的 `tensor_model_parallel_size=8`。BF16 配合 stochastic rounding 把舍入噪声打散，用于提高长训稳定性；不要据此推断 Trainium 没有 FP8。

## 先保证对齐，再比较性能

我会固定 microbatch 和序列档位，减少编译图数量，再用激活重计算管理 Neuron 的 SRAM / HBM 预算。用 `neuron-top` 检查核利用率与通信计算重叠，节点失败恢复可利用 SageMaker / 托管训练的能力。

数值验证使用相同数据和 seed，先比较短序列 token-level loss。对不齐时查精度、collective 顺序，再查 kernel；注意力可用短序列 greedy / teacher-forcing loss 对照 GPU。性能看 token/s/core、MFU 类利用率、loss 曲线，以及第一次 job 的编译时间。

主机 CPU 解码、tokenizer 和 checkpoint 落盘也可能使核空转，这与 GPU 的数据加载问题类似，只是诊断工具换成 Neuron。最终服务在 Bedrock 时，仍按应用任务验收，见 `amazon-titan-eval`。

Inferentia 偏推理，Trainium 偏训练，Neuron SDK 同时覆盖两者。Nova / Titan 内部训练配方没有公开时，介绍停在这些公开栈差异，产品选型见 `amazon-nova`。

## 追问

**应用里的 all-reduce 代码要全改吗？**
应用层仍可写 `torch.distributed.all_reduce`，后端改为 Neuron collectives 与 EFA。

**FlashAttention 能直接用吗？**
不能假设同名 CUDA kernel 可迁移。用编译器支持的 transformer 路径或 NKI 实现，并与 GPU 做数值对齐。

**什么情况下还会用 GPU？**
CUDA 生态、研究内核、调试工具和 Neuron 未支持算子都可能决定选 GPU。Trainium 的规模训练性价比需按实际负载验证。

**Trn1 训练的模型一定在 Bedrock 同类芯片上服务吗？**
不一定。Serving 可能用 Inferentia、GPU 或托管 API，训练实例与 `InvokeModel` 是不同层。
