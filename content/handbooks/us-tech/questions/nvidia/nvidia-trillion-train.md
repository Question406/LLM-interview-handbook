---
id: nvidia-trillion-train
section: nvidia
order: 1
level: S
title: NVIDIA：万亿参数 LLM 怎么分布式训练？并行切在哪？
quick: >-
  先分别估算参数、优化器状态和激活的显存，再组合张量、流水线和数据并行及状态分片。张量并行拆层内矩阵，流水线并行拆层，FSDP/ZeRO
  等分片状态；再用重计算、FlashAttention 和通信重叠控制内存与空转，最后按 GPU 时间线判断瓶颈。
tags:
  - NVIDIA
  - Distributed Training
  - Megatron
  - Parallelism
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: NVIDIA Senior SWE (LLM Applications) Interview Experience (2025)
    url: >-
      https://www.tryexponent.com/experiences/nvidia-senior-software-engineer-interview-5768ad
    type: candidate-first-hand
  - title: >-
      Megatron-LM — Training Multi-Billion Parameter Language Models Using Model
      Parallelism
    url: 'https://arxiv.org/abs/1909.08053'
    type: primary
  - title: >-
      Efficient Large-Scale Language Model Training on GPU Clusters Using
      Megatron-LM
    url: 'https://arxiv.org/abs/2104.04473'
    type: primary
---

## 可以这样回答

我会先算清参数、优化器状态和激活各占多少显存，再组合张量并行、流水线并行和数据并行。万亿参数既有总状态放不下的问题，也有单层计算和跨卡通信的问题，所以配置要说明每个轴解决什么、代价是什么。比如 Adam 的状态已经达到 TB 量级，继续复制整份优化器状态就行不通。

粗算 bf16 参数 $2$ 字节，Adam 还要 fp32 副本 + 一阶二阶矩，优化器状态大约 $12$ 字节/参数量级。$10^{12}$ 参数光优化器就是数 TB，单机甚至单节点放不下。激活还跟 $B\cdot T\cdot L\cdot d$ 走。因此需要同时处理模型状态和激活，复制完整模型的 DDP 会先碰到容量上限。

## 技术备查

## 真题记录

- 公司：NVIDIA
- 岗位：Senior Software Engineer, LLM Applications（2025-10 虚拟 onsite）
- 来源：Exponent 候选人报告
- 题面：Design a distributed training environment for a trillion-parameter language model
- 评委追：具体用过哪些工具、并行配置、以及 GPU 为什么没吃满

我会先算清参数、优化器状态和激活各占多少显存，再组合张量并行、流水线并行和数据并行。万亿参数既有总状态放不下的问题，也有单层计算和跨卡通信的问题，所以配置要说明每个轴解决什么、代价是什么。比如 Adam 的状态已经达到 TB 量级，继续复制整份优化器状态就行不通。

## 先算状态，再选切分

粗算 bf16 参数 $2$ 字节，Adam 还要 fp32 副本 + 一阶二阶矩，优化器状态大约 $12$ 字节/参数量级。$10^{12}$ 参数光优化器就是数 TB，单机甚至单节点放不下。激活还跟 $B\cdot T\cdot L\cdot d$ 走。因此需要同时处理模型状态和激活，复制完整模型的 DDP 会先碰到容量上限。

切分可以按下面三条轴组合：

| 轴 | 切什么 | 通信 |
| --- | --- | --- |
| 张量并行 (TP) | 层内 GEMM 的列/行 | 每层 all-gather / all-reduce，延迟敏感，通常限在 NVLink 域 |
| 流水线并行 (PP) | 层分成 stage | 点对点传激活，要 microbatch 填气泡 |
| 数据并行 (DP/FSDP/ZeRO) | 样本，以及分片的参数/梯度/状态 | 梯度 reduce-scatter / all-gather |

万亿常见是 TP × PP × DP。TP 取 $8$ 或 $4$（一台 8 卡），PP 把层铺到多机，剩下的卡数给 DP。上下文很长时再加序列并行 / 上下文并行，否则激活先爆。

重计算（activation checkpointing）通过多算一次前向减少激活存储，FlashAttention 则减少 attention 激活，两者在万亿规模通常都会考虑。

## 利用率：面试要能诊断空转

我会先用 Nsight Systems 把 GPU 时间分成计算、等待通信和等待数据。TP 太大时，层内同步可能把计算切成许多小 kernel，降低 MFU；PP 太深会扩大气泡；DP 太大则使 optimizer step 的集合通信更重。若空转来自 loader 跟不上，就先修数据供给。

减少空转要给出具体的重叠安排：PP 用 1F1B，TP 尝试重叠通信与计算，DP 把梯度通信放进反向后几层仍在计算的时间里。

还要准备说明自己用过 Megatron-LM、NeMo、Transformer Engine 中的哪些工具，是否做过 FP8，以及怎样配置 NCCL 拓扑。纸面方案与实际运行过的配置分清楚，kernel 层未做过就如实说明。

## 追问

**ZeRO-3 能不能替代 TP？**
不能直接替代。ZeRO-3 分片保存参数，执行层内大 GEMM 时仍需组装对应矩阵；TP 则进一步把计算分给多卡。万亿 dense 模型通常仍要 TP 才能把单层算力和显存同时放下。
**MoE 万亿呢？**
MoE 还要加入专家并行这个第四轴，路由带来 all-to-all 通信瓶颈，需要在 dense 的并行图上另加这一层。
**为什么不用流水线就完事？**
纯 PP 在万亿深度下仍有气泡和在途激活内存问题，vocabulary 以及第一层、最后一层的大矩阵也要单独安排，单靠按层切分解决不了这些负担。
