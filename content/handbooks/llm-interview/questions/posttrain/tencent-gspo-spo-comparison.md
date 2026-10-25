---
id: tencent-gspo-spo-comparison
section: posttrain
order: 105
level: S
title: 腾讯 WXG：GSPO 的优化是什么？腾讯的 SPO 有何不同？
quick: "GSPO 把 importance ratio 和 clipping 提到 sequence 级，主要解决长序列 / MoE 下 token 级比率累积的不稳；腾讯 SPO 去掉了对 group 的依赖，用持续的、KL-adaptive value tracker 加 batch 级归一化，让单条样本也有学习信号。比较时说清 baseline、粒度和吞吐的取舍。"
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

两者改的是不同的地方。GSPO 改的是 importance ratio 和 clip 的粒度，从 token 提到 sequence；腾讯的 Single-stream Policy Optimization（SPO）改的是 baseline，以及要不要依赖 group，让单条采样轨迹（rollout）也有学习信号。比较时讲清基线、优化粒度和吞吐的差别，光说哪篇发得晚没用。还有两个坑要避开，别把不同论文里同名的 SPO 混成一个算法，也别把 GSPO 说成「GRPO 去掉 KL」。

## GSPO：序列级 ratio，稳住长生成和 MoE

GSPO 保留了 group-relative advantage，但把 token likelihood ratio 的优化单位提到完整的 sequence，在 sequence 级做 ratio、clipping 和优化。它针对的问题是，token 级的 $\rho_t$ 在长生成、混合精度或 MoE routing 下会连乘、逐步不稳，个别 token 的极端比值会主导梯度。比如一条很长的推理里，有一个 token 因为路由变了，比值一下子很极端，token 级 clip 下它能左右整段的梯度；换成序列级的 ratio，就看整段轨迹的重要性权重。这不等于不要 KL、不用监控 policy drift，正则仍然比 $\pi$ 和 $\pi_{\mathrm{ref}}$，只是信任域作用在整段轨迹的重要性权重上。

它也要和「序列级 KL」分开。那是 drift 正则的 reduction，GSPO 改的是 $\pi$ 对 $\pi_{\mathrm{old}}$ 的 clip 粒度。

## 腾讯 SPO：去掉 group，单条也有信号

SPO 从另一个方向入手，消除 group 的同步等待和退化 group（全对全错、零梯度）。它用一个持续的、KL-adaptive value tracker 当 baseline，再在 batch 范围内归一化 advantage，这样单个 rollout 也能提供信号。吞吐上不用再等同一输入提示采满 $G$ 条，对长 horizon 更友好。代价是 baseline 从无偏的组均值变成了 tracker，带来 tracker 自己的偏置和方差问题。所以回答「关注了没有」时，要讲到它解决的是 GRPO 的 group 成本和空组问题，别去复述 GSPO 的序列 clip。

## 放在一起比

| 维度 | GSPO | 腾讯 SPO |
| --- | --- | --- |
| baseline | 组内相对 | KL-adaptive tracker + batch 归一 |
| 粒度 | 序列级 ratio/clip | 单流，不依赖 group |
| 吞吐 | 仍要等组 | 单条即可更新 |

现场按项目的痛点选：MoE 或者很长的推理过程里 ratio 出现极端值，选 GSPO；group 等不起、空组多，选 SPO。两者都能和可验证奖励一起用。较早文献里还有别的 SPO（比如某种 self-play），别当成这一篇。

## 追问

**GSPO 还要不要 KL？**
要监控漂移，它没说取消 $\pi_{\mathrm{ref}}$ 约束。

**SPO 还算不用价值评估模型（critic）吗？**
tracker 是一个轻量的基线，算不上完整的 PPO critic，但也已经不是纯粹的组均值了。

**两者能叠在一起用吗？**
序列级 clip 和单流 baseline 是正交的，理论上可以组合，只是实现和调参会更复杂，面试说清它们正交就够了。

**碰到同名的 SPO 怎么办？**
先问论文年份，以及是不是「single-stream」那篇，别把别家的 SPO 背进来。
