---
id: ali-dapo-allcorrect
section: alibaba
order: 10
level: A
title: Group 里样本全对或全错时 GRPO 会怎样？DAPO 怎么处理？
quick: 组内无相对差异 → $\text{advantage}\approx 0$，梯度信号消失。DAPO 等通过动态采样、非对称裁剪、或过滤无效 group 等机制保证仍有有效更新。
tags:
  - Alibaba
  - DAPO
  - GSPO
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
  - title: ↗ Qwen GSPO paper
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
---

这块容易直接答成「全对就该学得更快」。GRPO 的 $A$ 来自组内相对差异；全对或全错时 $r_i$ 常数，$\sigma\approx 0$，$\hat{A}_i\approx 0$，这一批是空梯度。这是 reasoning RL 的经典 failure mode：难题全错、简单题全对，相对优势学不到东西。阿里国际面常从这里接到 DAPO / GSPO。组内标准化公式见 `ali-grpo-advantage`。

## 空 group：不是「没学好」，是信号定义如此

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\varepsilon}.
$$

$r_1=\cdots=r_G$ 时分子为零。PPO 的 critic 此时仍可能给出非零 $A$，只是不一定对；GRPO 没有 $V_\psi$，空组就是空更新。监控要报无效 group 比例，而不是只看平均 reward。reward 很高可能全是简单题全对。实践：按难度 curriculum、保证 group 多样性、加大 $G$、换更细过程分。硬给全对组加噪声会毁格式。

## DAPO：过滤空组 + 非对称 clip

DAPO（Decoupled Clip and Dynamic Sampling Policy Optimization）针对这类塌缩：动态采样过滤 accuracy 为 $0$ 或 $1$ 的 prompt，直到 batch 里有可分的组；Clip-Higher 把上下 clip 解开，$\varepsilon_{\mathrm{high}}\gt\varepsilon_{\mathrm{low}}$，让概率上调空间更大，缓解熵崩。它还常用 token 级 loss 平均、对过长回复做软惩罚，而不是把空组拿来硬训。Dr.GRPO 从另一侧改：去掉组内 $\sigma$ 归一，减轻「低方差题被放大」的偏置。面试我一般先解释 GRPO 依赖组内相对差异，再说全对/全错导致 $A$ 塌缩，再引出 DAPO/Dr.GRPO 对采样、裁剪、标准化的修正，最后落到监控空 group 比例。

## 阿里方向再对一下 GSPO

Qwen **GSPO**（Group Sequence Policy Optimization，[arXiv:2507.18071](https://arxiv.org/abs/2507.18071)）把重要性比从 token 级改到序列级：对整段似然比做长度归一再 clip，而不是每个 token 一个 $\rho_t$。和 token-level GRPO 对照着讲：同一套组内优势，差在重要性采样的粒度。空 group 问题 GSPO 同样存在。序列级 $\rho$ 救的不是零方差 $A$。选型仍看任务：可验证、组内能分出对错，才值得上 on-policy；否则先改题难度或回到 SFT/DPO（`ali-grpo-vs-sft`）。

## 追问

- **过滤空组会不会让题越来越偏？** 会。动态采样偏向「半对半错」的中等题，过难/过易被丢掉。要用 curriculum 和 held-out 覆盖两端。
- **加大 $G$ 能否救全错？** 能提高「至少一条对」的概率，但题远超能力时 $G$ 再大也全零，应降难度或加过程分。
- **和 DPO 后分布变尖的关系？** 同构：组方差塌了 GRPO 没信号。见 `ali-multineg-then-grpo`。
