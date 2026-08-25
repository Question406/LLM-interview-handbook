---
id: baichuan-pretrain-parallel
section: systems
order: 166
level: A
title: 百川智能：预训练有哪些并行方式？
quick: >-
  数据并行复制模型切数据；张量并行切矩阵；流水线并行切层；序列 / 上下文并行切序列；MoE 再加专家并行。组合看单卡放不下的是参数、激活还是 batch。
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

百川这题，这块容易只报「DP / MP」两个缩写，或把 ZeRO 和张量并行说成一回事。我会按「哪块显存 / 哪段通信先爆」选切法：复制模型切数据、切矩阵、切层、切序列、MoE 再切专家。没做过千卡预训练也可以按这条诊断链答。原帖候选人只讲了 DP/MP，补上 ZeRO 与 TP 的差别会完整得多。相关卡：`sys-parallel`、`infra-megatron-mlp-tp`、`baichuan-deepspeed`。组合并行时我一般先固定 TP 再加 PP/DP，避免三个维度一起调到不可复现。

## 数据并行与 ZeRO

DDP 每卡一份完整参数，切的是 batch，梯度 all-reduce。模型单卡放得下、要堆吞吐时这是默认。参数和 Adam 状态复制后先爆，再用 ZeRO 分片优化器 / 梯度 / 参数，仍属数据并行家族，但通信模式变成按需 gather。不要把 ZeRO-3 叫成张量并行：它不把 $W$ 按列切开算局部 GEMM，而是分片存储、算前聚合。原帖只讲 DP/MP 时，补一句「MP 在中文面经里常混指 TP」可以避免和面试官用词错位。

## 张量、流水线、序列、专家

Megatron 式张量并行把 GEMM 的 $W$ 按列 / 行切开，MLP 与 attention 内部有固定通信（如一次 all-reduce）。层数极深、单卡放不下整网时加 pipeline，用 micro-batch 填气泡。长序列激活爆了加 context / sequence parallel，沿序列切 activation。MoE 再加 expert parallel，token 走 all-to-all。3D 并行是 DP×TP×PP 的乘积，面试先讲清每一维切的是什么，再提组合，不要一上来画网格。MLP 两层怎么切见 `infra-megatron-mlp-tp`，这里只要能点到列切 / 行切配对。

## 怎么选：看先爆的是什么

参数副本爆 → ZeRO 或 TP；单层矩阵太宽 → TP；深度导致单卡层放不下 → PP；$N$ 太长激活爆 → 序列并行 / 激活检查点；MoE 专家太多 → EP。通信与计算要配得上：TP 太大会让单步延迟受 all-reduce 绑死。面试用「先报切什么、再报一次前向有几次集合通信」比堆框架名更稳。相关细节见 `sys-collectives`。

## 追问

- **TP 和 ZeRO-3 差在哪？** TP 切计算图里的矩阵；ZeRO-3 切存储，计算前要 gather 参数。
- **PP 气泡怎么来的？** 流水线头尾阶段会空等，靠 micro-batch 数量和调度（1F1B）填。
- **推理并行一样吗？** 推理常 TP + 连续 batch；ZeRO 基本不出现。见 `ant-vllm-paged`。PP 在 decode 里气泡更难填，一般不作为默认。
- **没做过预训练怎么答？** 用「显存账：参数 / 优化器 / 激活 / KV」映射到切法，比背框架名更安全。先说自己训过的规模，再类比缺的那一维。
