---
id: fund-bernoulli-adv-var
section: fundamentals
order: 160
level: A
title: 0-1 奖励的方差何时最大？这对 GRPO 有效组意味着什么？
quick: >-
  $r\sim\mathrm{Bernoulli}(p)$ 时 $\mathrm{Var}(r)=p(1-p)$，在 $p=0.5$ 最大、两端为 0。GRPO 的组内相对优势要靠组里同时有对有错，全 0 / 全 1 的组方差为 0、优势为 0，所以最有信息的题落在当前策略的能力边界上。别把它做成「永远只训 50%」的教条，$p$ 随策略变，覆盖也要保留。
tags:
  - GRPO
  - Sparse Reward
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: DAPO — Decoupled Clip and Dynamic sAmpling Policy Optimization
    url: https://arxiv.org/abs/2503.14476
    type: primary
---
0-1 奖励的方差是 $p(1-p)$，在 $p=0.5$ 时最大，$p=0$ 或 $1$ 时为 0。对 GRPO 这类组相对算法，组内奖励方差就是信号来源：一组里没有方差，就没有相对优势，这一步白算。所以「方差大」在这里一点也不坏。全对 / 全错的机制见 `pt-grpo-variance`，这张卡补的是 $0/1$ 奖励的概率部分，以及它和策略梯度无偏性的区别。

举个例子，一道题模型现在只有 5% 的概率做对，采 8 条大概率全是 0，组内优势全是 0；另一道题对错各半，8 条里几乎一定既有对也有错，每条都能拿到正或负的优势。

## Bernoulli 方差：$p(1-p)$

$$
\mathbb{E}[r]=p,\qquad\mathrm{Var}(r)=p(1-p).
$$

$p=0$ 或 $1$ 时方差为 0，结果没有不确定性，也谈不上谁「相对更好」。$p=0.5$ 时方差取到最大值 $1/4$，组内最容易同时抽到 0 和 1。MC 优势 $r-b$ 的尺度跟着这条抛物线走；如果再除以组 $\sigma$，两端那点微弱分差会被放大，见 `fund-adv-norm-bias`。

这件事和无偏性是正交的。$r$ 是 0-1，REINFORCE 照样无偏，只是有效信噪比随 $p$ 变化。$p\to 0$ 时很少撞到成功，梯度几乎全在「把已经错的再压一遍」，这属于探索问题，见 `arl-sparse-reward-exploration`；$p\to 1$ 时组相对给不出方向，只能做保持，或者换目标（更短、更稳）。

## 对 GRPO：组内方差非零的才是有效组

$G$ 条 i.i.d. Bernoulli，组内全部相同的概率是 $p^G+(1-p)^G$。$p=0.5,G=8$ 时这个概率已经很小；$p=0.05$ 时全 0 很常见。对应有几种处理。

加大 $G$ 能降低空组概率，baseline 也更稳，代价是成本线性增长，见 `pt-grpo-group-size`。

动态采样是丢掉 $\mathrm{std}=0$ 的组再采，见 `pt-dapo`。它不会给 $\nabla J$ 的公式引入偏差，但会改变模型看见哪些输入提示（prompt）的分布：难题如果长期全 0，就会被课程隐式删掉，这是数据层面的偏倚。

也别把 $p=0.5$ 的题做成静态题库。策略变强以后，昨天的边界题变成 $p\approx 1$，空组又回来了。难度（difficulty）是随策略变化的。

连续奖励（奖励模型（RM）打分）组内几乎总有方差，空组少，但方差可能来自长度或文风，这个信号未必代表「更好」。规则判定的 $0/1$ 奖励更干净，也更苛刻：没有中间分，就只能在能力边界上采样。

## 追问

**$p=0.5$ 的题方差最大，是不是只训这些就行？**
当下确实更容易拿到区分信号，但要覆盖的范围和新领域里，题目的 $p$ 往往很低。这些题要保留，用课程或演示先把 $p$ 抬到能产生组信号的程度。

**除了 $\sigma$ 之后，$p=0.5$ 和 $p=0.1$ 的题幅度一样大吗？**
组内标准化会把不同 $p$ 的题拉到相近的幅度，等于忽略了「这题本来就更吵 / 更难」。这一步是在改权重，见 Dr.GRPO。

**空组是 bias 还是 variance 的问题？**
$p(1-p)$ 是奖励的方差。空组让当次 $\hat A=0$，是零信号，没有把 $\nabla J$ 估偏到别的方向。动态采样改的是 prompt 分布，偏差只可能出在那一层。

**过程分把 Bernoulli 拆开以后，结论还成立吗？**
拆开以后逐步的 $r_t$ 不再共用同一个 $p$，方差结构变了。组相对照样能做，但「$p=0.5$ 信号最强」不再直接成立。
