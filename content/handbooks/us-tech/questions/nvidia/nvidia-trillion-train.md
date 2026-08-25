---
id: nvidia-trillion-train
section: nvidia
order: 1
level: S
title: NVIDIA：万亿参数 LLM 怎么分布式训练？并行切在哪？
quick: >-
  参数、激活、优化器状态要分开算。张量并行切层内矩阵，流水线切层，数据并行 / FSDP 切样本和状态。万亿参数单靠数据并行塞不进，通
  常是 3D 并行再加重计算和通信重叠。面试要落到 GPU 利用率，不是背名词。
tags:
  - NVIDIA
  - Distributed Training
  - Megatron
  - Parallelism
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: NVIDIA Senior SWE (LLM Applications) Interview Experience (2025)
    url: https://www.tryexponent.com/experiences/nvidia-senior-software-engineer-interview-5768ad
    type: candidate-first-hand
  - title: Megatron-LM — Training Multi-Billion Parameter Language Models Using Model Parallelism
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 真题记录

- 公司：NVIDIA
- 岗位：Senior Software Engineer, LLM Applications（2025-10 虚拟 onsite）
- 来源：Exponent 候选人报告
- 题面：Design a distributed training environment for a trillion-parameter language model
- 评委追：具体用过哪些工具、并行配置、以及 GPU 为什么没吃满

这轮是 onsite 里最难的一题。候选人反馈评委不太吃「用了 DeepSpeed」这种空话，要你按字节和通信把切分讲清楚。

## 先算状态，再选切分

粗算 bf16 参数 $2$ 字节，Adam 还要 fp32 副本 + 一阶二阶矩，优化器状态大约 $12$ 字节/参数量级。$10^{12}$ 参数光优化器就是数 TB，单机甚至单节点放不下。激活还跟 $B\cdot T\cdot L\cdot d$ 走。所以万亿不是「多加几张卡做 DDP」。

三条轴：

| 轴 | 切什么 | 通信 |
| --- | --- | --- |
| 张量并行 (TP) | 层内 GEMM 的列/行 | 每层 all-gather / all-reduce，延迟敏感，通常限在 NVLink 域 |
| 流水线并行 (PP) | 层分成 stage | 点对点传激活，要 microbatch 填气泡 |
| 数据并行 (DP/FSDP/ZeRO) | 样本，以及分片的参数/梯度/状态 | 梯度 reduce-scatter / all-gather |

万亿常见是 **TP × PP × DP**。TP 取 $8$ 或 $4$（一台 8 卡），PP 把层铺到多机，剩下的卡数给 DP。上下文很长时再加序列并行 / 上下文并行，否则激活先爆。

重计算（activation checkpointing）用算力换激活显存。FlashAttention 降注意力激活。这两项在万亿设定几乎是默认，不是加分项。

## 利用率：面试要能诊断空转

Nsight Systems 上看：GPU 在算、在等通信、还是在等数据。TP 太大，层内同步把 kernel 切太碎，MFU 掉。PP 太深，气泡占比高。DP 太大，optimizer step 的集合通信变重。数据 loader 跟不上时 GPU 空，这和模型并行无关。

Overlap：PP 里 1F1B，TP 里通信与计算重叠，DP 里把梯度通信藏在反向后几层。讲不出 overlap，评委会觉得你只背了并行表。

NVIDIA 岗还可能追：用过 Megatron-LM / NeMo / Transformer Engine 没有、FP8 训练有没有做过、NCCL 拓扑怎么配。没做过就诚实说纸面配置，并承认没有 kernel 级经验。装熟更糟。

## 追问

- **ZeRO-3 能不能替代 TP？** 能把参数打散，但层内大 GEMM 的计算仍要一块完整矩阵。万亿 dense 模型通常仍要 TP 才能把单层算力和显存同时放下。
- **MoE 万亿呢？** 专家并行是第四轴，all-to-all 是新瓶颈，和 dense 万亿不是同一张图。
- **为什么不用流水线就完事？** 纯 PP 在万亿深度下气泡和 bubble 内存都难看，还要把词表和第一层/最后一层的大矩阵单独处理。
