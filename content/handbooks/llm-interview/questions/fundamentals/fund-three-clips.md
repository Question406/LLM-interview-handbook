---
id: fund-three-clips
section: fundamentals
order: 161
level: A
title: Gradient clip、Advantage clip、Ratio clip 分别偏了什么？
quick: "先区分裁剪对象是 $g$、$\\hat A$ 还是 $\\rho$。Gradient clip 限制梯度更新，裁剪前的估计器仍可能无偏；Advantage 或 reward clip 改变回报系数；PPO 的 ratio clip 使部分越界 token 的梯度为 0，是有偏的策略梯度近似。"
tags:
  - PPO
  - Gradient Clipping
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: On the difficulty of training Recurrent Neural Networks
    url: https://arxiv.org/abs/1211.5065
    type: secondary
  - title: MiniMax-M1 (CISPO)
    url: https://arxiv.org/abs/2506.13585
    type: secondary
---

常见误区是：把 `clip_grad_norm_`、`adv.clamp`、PPO 的 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$ 说成同一种「为了稳定」。三者都能稳定训练，但引入偏差的位置不同。PPO 目标本身见 `pt-ppo-clip`；本题只做对照表。

## 截的是谁

Gradient clip。反传之后若 $\|\hat g\|\gt \tau$，缩放到 $\tau$。$\hat g$ 作为 $\nabla J$ 的估计，在 clip 之前可以仍无偏；clip 之后这一步更新不再是那个无偏方向上的任意步长。它不改 $\hat A$，也不改 $\rho$。RNN / 大模型防爆炸的工程件，见 `fund-gradclip`。不要说「所以策略梯度有偏」，有偏的是被截断后的一步 $\Delta\theta$，不是你在用的 advantage 公式。

Advantage / return / 奖励分数（reward） clip。如 $\hat A\leftarrow\mathrm{clip}(\hat A,-c,c)$，或把奖励模型（RM）的分数限制在 $[-1,1]$。这直接改乘在 $\nabla\log\pi$ 上的系数，期望变成 $\mathbb{E}[\nabla\log\pi\cdot\mathrm{clip}(A)]$，相对原 $J$ 有偏。换来的是不被极端轨迹主导。Reward normalization / 除 $\sigma$ 是同一族的「改系数」，见 `fund-adv-norm-bias`。

Ratio clip（PPO / GRPO surrogate）。

$$
\min\big(\rho_t\hat A_t,\;\mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\hat A_t\big).
$$

截的是重要性比在目标函数里的取值。$A\gt 0$ 且 $\rho\gt 1+\varepsilon$（或对称的负侧）时该项对 $\theta$ 的梯度为 0：这个 token 的该项本轮不提供梯度。这是对 on-policy 梯度的有偏近似，用来限制一步走太远，见 `baidu-ppo-clip-sign`。CISPO 改成截 $\rho$ 再 detach，越界仍有 $\nabla\log\pi$，偏的是权重而不是「有没有梯度」，见 `pt-cispo`。

## 怎么选，不要叠到全是 0

三层可以同时开，有效更新可能被多次削弱：ratio 已经把大部分 token 打成 0，advantage 再夹紧，最后 grad clip 再砍一步。监控应对着看 clip fraction（ratio）、advantage 分位数、grad norm 触顶率。Ratio clip fraction 接近 1，先减 epoch / 更频繁地采样新轨迹（rollout），而不是把 grad clip 再拧紧。

Value clip（PPO 里对 $V$ target 相对旧 $V$ 的夹紧）是第四个：偏的是 价值评估模型（critic）的回归目标，不直接改 policy 的 $\nabla\log\pi$，但下一轮 GAE 会吃进被夹过的 $V$。不要和 ratio clip 混报成「PPO 的 clip」。

## 追问

- **Grad clip 会不会让无偏估计变有偏？** 作为 $\mathbb{E}[\hat g]$ 的一步实现，会；作为「我用的 $\hat A$ 公式」，不会。先问对方问的是哪一层。
- **Advantage clip 和 Huber 损失像吗？** 都在压极端系数。Huber 在 critic loss 上更常见；对 $\hat A$ 硬 clip 更粗。
- **只开 ratio clip 够不够？** 长思维链（CoT，即分步推理过程）上 $\rho$ 连乘仍可能让少量 token 主导，见 `fund-token-is-var`。Ratio clip 是信任域，不是回报方差公式。
- **GRPO 还要 grad clip 吗？** 要。组优势再漂亮，偶发极大的 $\nabla\log\pi$ 仍可能造成梯度爆炸。两层正交。
