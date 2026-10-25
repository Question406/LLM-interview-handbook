---
id: sys-verl-fsdp-vs-megatron
section: systems
order: 241
level: A
title: veRL 训练后端选 FSDP 还是 Megatron？
quick: "7B 到 30B、已有 HF 权重且想尽快跑通时，先用 FSDP/FSDP2；70B+、需要 TP/PP/EP 或 MoE 专家并行时，再考虑 Megatron。两者都能经 HybridEngine 接 vLLM / SGLang，主要区别是训练分片与重新分片的成本。"
tags:
  - VeRL
  - FSDP
  - Megatron
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
  - title: HybridFlow
    url: https://arxiv.org/abs/2409.19256
    type: primary
---

我会先看模型大小、有没有 MoE、现有 checkpoint 格式和集群是否同构。7B 到 30B、手里是 HF 权重、还不需要层内 TP 时，通常先用 FSDP/FSDP2；70B+、all-gather 后仍放不下，或需要 MoE 专家并行时，再考虑 Megatron。已有预训练栈就是 Megatron，继续沿用也能省掉转换成本。

FSDP 按 unit wrap，分片参数、梯度和优化器状态，配置相对少，容易对接 HuggingFace 权重、LoRA、PEFT 和社区 checkpoint，单机或多机都能尽快跑通 `actor_rollout_ref` 和 DAPO。LoRA 或冻结底层只训练部分参数时，wrap 与 `use_orig_params` 的问题也比 Megatron 少，后者还要自行对接并行切分。新路径里的 FSDP2 使用更清晰的 DTensor 布局，重新分片到推理 TP 时更容易描述张量布局。

FSDP 的瓶颈常出在超大模型跨节点 all-gather：每层要收齐参数才能算，通信量随参数增加，长序列还会让激活争带宽。70B 时这种等待可能明显，但层少、带宽足、prefetch 做得好时也未必慢，要看 profile。它的 MoE 专家并行不够完整，小专家数还能尝试，上百专家时，token 路由、容量丢弃和 EP 更适合 Megatron 或专用专家并行实现。

Megatron 提供层内 TP、层间 PP，以及 CP / EP，列切和行切的通信模式固定，吞吐上限高。接入时要处理 Megatron-Bridge、分片 `torch_dist` ckpt，配置 tp/pp/ep/cp，并与 rollout TP 对齐。训练 shard 和推理布局若对不上，reshard 可能退回近乎全量 gather，HybridEngine 少存一份整模的收益就会消失。Megatron 带 PP 时，还要额外对齐流水线阶段和推理 TP。

veRL 也支持 Megatron-FSDP 混合，例如主干走 Megatron，其余模块由 FSDP wrap。介绍时应说明模块边界，以及自己是否真正跑过，避免把文档路线当成生产经历。没有 OOM 或 EP 需求就提前引入 TP/PP，会同时扩大算法和并行配置的调试范围。

选训练后端与选 rollout 引擎是两件事。FSDP 和 Megatron 都能进 HybridEngine，再接 vLLM / SGLang；同构 GPU 上训显存紧张的 70B，可以考虑 Megatron + HybridEngine，7B 快速复现 DAPO 则 FSDP + vLLM 就够。若目标是 SGLang 生产栈，可以评估 slime，但它默认 Megatron，从 veRL FSDP 迁过去要转换 checkpoint。OpenRLHF 默认 DeepSpeed ZeRO，是另一条训练后端，不能把它的分片术语和 Megatron 混用。

## 追问

**单看模型参数量，能决定用哪个吗？**
不能。MoE、现成 HF ckpt、团队配置并行的经验和集群拓扑都会改变成本。先用 FSDP 把算法跑对，出现明确的显存或 EP 需求再换，通常更容易定位问题。

**换后端会影响 HybridEngine 吗？**
会改变 reshard 路径，不会改变复用同一批卡的目的。运行前就应核对 shard、TP 和 PP，避免算法调完才发现重新分片退回全量 gather。

**没跑过 Megatron，面试怎么讲？**
直接说明主栈和验证范围。跑过的可以讲一次分片 checkpoint 或 reshard 对不上的实际问题，没跑过的就把选型边界讲清楚。

相关：`sys-verl-hybridengine`、`sys-verl-vs-slime`、`sys-expert-parallel`、`sys-verl-vllm-vs-sglang`
