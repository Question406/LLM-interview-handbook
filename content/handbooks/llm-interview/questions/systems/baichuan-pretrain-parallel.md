---
id: baichuan-pretrain-parallel
section: systems
order: 166
level: A
title: 百川智能：预训练有哪些并行方式？
quick: "预训练常用五种切法：数据并行复制模型、切数据；张量并行切矩阵；流水线并行切层；序列 / 上下文并行切序列；MoE 再加专家并行。怎么组合，看单卡先放不下的是参数、激活还是 batch。"
tags:
  - Baichuan
  - Parallelism
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3
    type: candidate-first-hand
  - title: Megatron-LM
    url: https://arxiv.org/abs/1909.08053
    type: primary-paper
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“你知道预训练的一些并行方式吗？”**

预训练的并行就是按不同维度切：数据并行复制模型、切数据，张量并行切矩阵，流水线并行切层，序列或上下文并行切序列，MoE 再切专家。选哪种，看哪块显存、哪段通信先爆。原帖的候选人只讲了 DP 和 MP 两个缩写，如果再补上 ZeRO 和张量并行的区别，答案会完整得多。没做过千卡预训练也没关系，按这条诊断链答就行。

## 数据并行与 ZeRO

DDP 每张卡一份完整参数，切的是 batch，梯度做 all-reduce。模型单卡放得下、要堆 throughput 时，这是默认选择。参数和 Adam 状态被复制好几份，最先爆掉，这时用 ZeRO 把优化器状态、梯度、参数分片。ZeRO 仍然属于数据并行这一家，只是通信变成了按需 gather。别把 ZeRO-3 叫成张量并行：它不会把 $W$ 按列切开去算局部 GEMM，它做的是分片存储、算之前再聚合。中文面经里的「MP」常常混指 TP，回答时补一句，免得和面试官用词错位。

## 张量、流水线、序列、专家

Megatron 式的张量并行把 GEMM 的 $W$ 按列或按行切开，MLP 和 attention 内部有固定的通信，比如一次 all-reduce。MLP 两层具体怎么切见 `infra-megatron-mlp-tp`，这里能说出列切和行切配对就够了。层数很深、单卡放不下整个网络时加 pipeline，用 micro-batch 填气泡。长序列让激活爆了，就加 context / sequence parallel，沿序列维度切 activation。MoE 再加专家并行，token 通过 all-to-all 送到对应的专家。3D 并行是 DP×TP×PP 的乘积，面试时先讲清每一维切的是什么，再讲组合，别一上来就画网格。组合的时候一般先固定 TP，再加 PP 和 DP，免得三个维度一起调到没法复现。

怎么选就看先爆的是什么。参数副本爆了，用 ZeRO 或 TP；单层矩阵太宽，用 TP；网络太深、单卡放不下这些层，用 PP；$N$ 太长、激活爆了，用序列并行或激活检查点；MoE 专家太多，用 EP。通信和计算也要配得上，TP 开太大，单步延迟会被 all-reduce 卡住。面试里先说切什么、再说一次前向有几次集合通信，比堆框架名更稳，细节见 `sys-collectives`。

## 追问

**TP 和 ZeRO-3 差在哪？**
TP 切的是计算图里的矩阵；ZeRO-3 切的是存储，计算前要把参数 gather 回来。

**PP 的气泡是怎么来的？**
流水线开头和结尾的阶段会空等，要靠 micro-batch 数量和调度（1F1B）去填。

**推理的并行也一样吗？**
推理常用 TP 加连续 batch，ZeRO 基本不出现，见 `ant-vllm-paged`。PP 在逐 token 生成（decode）里气泡更难填，一般不作为默认。

**没做过预训练怎么答？**
用显存账，参数、优化器、激活、KV 各占多少，映射到对应的切法，比背框架名安全。先说自己训过的规模，再类比缺的那一维。

相关：`sys-parallel`、`infra-megatron-mlp-tp`、`baichuan-deepspeed`
