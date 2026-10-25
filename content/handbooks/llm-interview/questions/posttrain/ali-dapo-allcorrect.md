---
id: ali-dapo-allcorrect
section: posttrain
order: 10
level: A
title: Group 里样本全对或全错时 GRPO 会怎样？DAPO 怎么处理？
quick: "全对或全错时组内得分相同，$\\text{advantage}\\approx 0$，任务奖励给不出区分样本的梯度。DAPO 用动态采样过滤掉这类 group、补进有得分差异的组，再用非对称裁剪扩大概率上调的空间。"
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

全对或全错时，组内 $r_i$ 是常数，$\sigma\approx 0$，$\hat{A}_i\approx 0$，这一批就是空梯度。DAPO 的处理是动态采样，把这类组过滤掉、补进有得分差异的组，再用非对称裁剪扩大概率上调的空间。

直觉上会觉得「全对就该学得更快」，可 GRPO 的 $A$ 来自组内相对差异：

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\varepsilon}.
$$

$r_1=\cdots=r_G$ 时分子为零。这是 reasoning 强化学习（RL）的经典失败情形，难题全错、简单题全对，相对优势都学不到东西。阿里国际面常从这里接着问 DAPO / GSPO，组内标准化公式见 `ali-grpo-advantage`。

这不是「没学好」，是信号的定义本来如此。PPO 的 Critic 这时还可能给出非零的 $A$，只是不一定对；GRPO 没有 $V_\psi$，空组就是空更新。所以监控要报无效 group 的比例，平均 reward 很高，可能全是简单题全对。实践上可以按难度做 curriculum、保证 group 多样性、加大 $G$、换更细的过程分；硬给全对组加噪声会毁掉格式。

DAPO（Decoupled Clip and Dynamic Sampling Policy Optimization）就是针对这类塌缩的。动态采样把 accuracy 为 $0$ 或 $1$ 的输入提示（prompt）过滤掉，直到 batch 里有能分出高下的组；Clip-Higher 把上下 clip 解开，$\varepsilon_{\mathrm{high}}\gt\varepsilon_{\mathrm{low}}$，让概率上调的空间更大，缓解熵崩。它还常用 token 级 loss 平均，对过长回复做软惩罚，空组就不拿来硬训了。Dr.GRPO 从另一侧改，去掉组内 $\sigma$ 归一，减轻「低方差题被放大」的偏置。面试时我一般按这个顺序讲：GRPO 依赖组内相对差异，全对 / 全错让 $A$ 塌缩，DAPO / Dr.GRPO 在采样、裁剪、标准化上做修正，最后落到监控空 group 比例。

阿里方向还会对一下 GSPO。Qwen GSPO（Group Sequence Policy Optimization，[arXiv:2507.18071](https://arxiv.org/abs/2507.18071)）把重要性比从 token 级改到序列级，对整段似然比做长度归一再 clip，不再每个 token 一个 $\rho_t$。和 token-level GRPO 对照着讲，组内优势是同一套，差在重要性采样的粒度。空 group 的问题 GSPO 一样有，序列级 $\rho$ 救不了零方差的 $A$。选型还是看任务：可验证、组内能分出对错，才值得上 on-policy；不然先改题目难度，或回到 SFT/DPO（`ali-grpo-vs-sft`）。

## 追问

**过滤空组会不会让题越来越偏？**
会。动态采样偏向「半对半错」的中等题，过难、过易的都被丢掉了，要用 curriculum 和 held-out 把两端覆盖住。

**加大 $G$ 能救全错吗？**
能提高「至少一条对」的概率，但题目远超能力时 $G$ 再大也全是零，应该降难度或者加过程分。

**和直接偏好优化（DPO）之后分布变尖有什么关系？**
是同一回事：组方差塌了，GRPO 就没有信号，见 `ali-multineg-then-grpo`。
