---
id: fund-bernoulli-adv-var
section: fundamentals
order: 160
level: A
title: 0-1 奖励的方差何时最大？这对 GRPO 有效组意味着什么？
quick: >-
  $r\sim\mathrm{Bernoulli}(p)$ 时 $\mathrm{Var}(r)=p(1-p)$，在 $p=0.5$ 最大、两端为
  0。GRPO 组内相对优势靠组内同时有对有错；全 0 / 全 1 时方差为 0，优势为 0。最有信息的题在当前策略的能力边界，但不要做成「永远只训
  50%」的教条，$p$ 随政策变，还要覆盖。
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

常见误区是：「方差大」一律是坏事。对组相对算法，组内奖励方差是信号：没有方差就没有相对优势。全对 / 全错的机制见 `pt-grpo-variance`；本题补 $0/1$ 奖励的概率课，以及它跟策略梯度无偏性不是一回事。

## Bernoulli 方差：$p(1-p)$

$$
\mathbb{E}[r]=p,\qquad\mathrm{Var}(r)=p(1-p).
$$

$p=0$ 或 $1$ 时方差为 0：没有不确定性，也没有「相对更好」。$p=0.5$ 时方差取到 $1/4$，组内最容易同时抽到 0 和 1。MC 优势 $r-b$ 的尺度跟这根抛物线走；再除组 $\sigma$ 会把两端微弱分差放大，见 `fund-adv-norm-bias`。

这与无偏性正交。$r$ 是 0-1，REINFORCE 仍然无偏，只是有效信噪比随 $p$ 变。$p\to 0$ 时很少撞到成功，梯度几乎全是「再压一遍已经错的」，探索问题见 `arl-sparse-reward-exploration`；$p\to 1$ 时组相对没有方向，只能做保持或改目标（更短、更稳）。

## 对 GRPO：有效组 = 组内方差非零

$G$ 条 i.i.d. Bernoulli，组内全同的概率是 $p^G+(1-p)^G$。$p=0.5,G=8$ 时已经很小；$p=0.05$ 时全 0 很常见，这步白算。所以：

- 加大 $G$：降低空组概率，baseline 也更稳，成本线性，见 `pt-grpo-group-size`。
- 动态采样：丢掉 $\mathrm{std}=0$ 的组再采，见 `pt-dapo`。这不引入「对 $\nabla J$ 的公式偏差」，但改变了 看见哪些 输入提示（prompt） 的分布。难题若长期全 0，会被课程隐式删掉，这是数据偏倚。
- 不要把 $p=0.5$ 做成静态题库。政策变强后昨天的边界题变成 $p\approx 1$，空组会回来。Difficulty 是 policy-dependent。

连续奖励（奖励模型（RM） 分）组内几乎总有方差，空组少，但方差可能来自长度或文风，信号未必是「更好」。规则 $0/1$ 更干净，也更苛刻：没有中间分，就要在边界上采样。

## 追问

- **$p=0.5$ 的题方差最大，是否该只训这些？** 当前训练更容易获得区分信号，但覆盖和新域往往 $p$ 很低。战略上保留，用课程或演示先把 $p$ 抬到能出组信号。
- **除 $\sigma$ 之后 $p=0.5$ 和 $p=0.1$ 一样大？** 组内标准化会把不同 $p$ 的题拉到相近幅度，等于忽略「这题本来就更吵 / 更难」。这是改权重，见 Dr.GRPO。
- **这是 bias 还是 variance？** $p(1-p)$ 是奖励的方差。空组让当次 $\hat A=0$，是零信号，不是把 $\nabla J$ 估偏到另一个方向。动态采样改的是 prompt 分布，那一层才可能偏。
- **过程分把 Bernoulli 拆开了吗？** 拆开则逐步 $r_t$ 不再是同一个 $p$，方差结构变了，组相对仍可做，但「$p=0.5$ 信号最强」不再直接成立。
