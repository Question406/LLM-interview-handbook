---
id: tencent-gspo-spo-comparison
section: posttrain
order: 105
level: S
title: 腾讯 WXG：GSPO 的优化是什么？腾讯的 SPO 有何不同？
quick: >-
  GSPO 将 importance ratio 与 clipping 提升到 sequence 级，主要解决长序列 / MoE 下 token-level 比率累积的不稳；腾讯 SPO 则去掉
  group 依赖，用持续的、KL-adaptive value tracker 和 batch 级归一化给单条样本学习信号。比较时要说清 baseline、粒度和吞吐 trade-off。
tags:
  - Tencent
  - WXG
  - GSPO
  - SPO
  - Reasoning RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 秋招面经-腾讯WXG NLP算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/0bdb10f282b541bda9ae11db203a40eb
    type: candidate-first-hand
  - title: 'GSPO: Towards Scalable Reinforcement Learning for Language Models'
    url: https://arxiv.org/abs/2507.18071
    type: primary-paper
  - title: Single-stream Policy Optimization
    url: https://arxiv.org/abs/2509.13232
    type: primary-paper
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：WXG；NLP 算法
- 届别 / 流程：秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-02
- 来源类型与可信度：牛客候选人原帖，B（公司、团队、流程和轮次明确；届别未披露）
- 原始措辞：**“介绍GSPO的优化，腾讯最近出的SPO有关注吗”**

不要把不同论文里同名的 SPO 混成一个算法，也不要把 GSPO 说成「GRPO 去掉 KL」。GSPO 改的是 **importance ratio / clip 的粒度**：从 token 提到 sequence。腾讯 Single-stream Policy Optimization（SPO）改的是 **baseline 与是否依赖 group**：单条 采样轨迹（rollout） 也要有学习信号。比较应说明基线、优化粒度和吞吐的差别，而不是只看发布时间。

## GSPO：序列级 ratio，稳住长生成 / MoE

GSPO 保留 group-relative advantage，但把 token likelihood ratio 的优化单位提升为完整 sequence，在 sequence 级做 ratio、clipping 与优化。针对的是 token-level $\rho_t$ 在长生成、混合精度或 MoE routing 下连乘 / 逐步不稳定：个别 token 的极端比会主导梯度。它并不等价于「没有 KL 或不需要监控 policy drift」，正则仍看 $\pi$ vs $\pi_{\mathrm{ref}}$，只是信任域作用在整段轨迹的重要性权重上。

和「序列级 KL」也要分开：那是 drift 正则的 reduction；GSPO 是 $\pi$ vs $\pi_{\mathrm{old}}$ 的 clip 粒度。

## 腾讯 SPO：去掉 group，单条也有信号

SPO 从另一路径消除 group 的同步等待和退化 group（全对全错零梯度）。它用持续的、KL-adaptive value tracker 作为 baseline，并在 batch 范围归一化 advantage，使单个 rollout 也能提供信号。吞吐上不再等同一输入提示 采满 $G$ 条，长 horizon 更友好；代价是 baseline 变成 tracker 的偏置 / 方差问题，而不再是无偏的组均值。

「关注了没有」应答到：它解决 GRPO 的 group 成本与空组，而不是复述 GSPO 的序列 clip。

## 怎么比：三列就够

| 维度 | GSPO | 腾讯 SPO |
| --- | --- | --- |
| baseline | 组内相对 | KL-adaptive tracker + batch 归一 |
| 粒度 | 序列级 ratio/clip | 单流，不依赖 group |
| 吞吐 | 仍要等组 | 单条即可更新 |

现场按项目痛点选：MoE / 很长的推理过程 ratio 出现极端值 → GSPO；group 等不起、空组多 → SPO。两者都可以和可验证奖励一起用。不要把较早文献里其它 SPO（如某种 self-play）当成这一篇。

## 追问

- **GSPO 还要不要 KL？** 要监控漂移。它没宣称取消 $\pi_{\mathrm{ref}}$ 约束。
- **SPO 还是无 价值评估模型（critic） 吗？** tracker 是轻量基线，不是完整 PPO critic，但已不是纯组均值。
- **能叠在一起吗？** 序列级 clip 与单流 baseline 正交，理论上可组合，但实现和调参会变复杂，面试说清正交即可。
- **同名 SPO？** 先问论文年份与「single-stream」；不要把别家 SPO 背进来。
