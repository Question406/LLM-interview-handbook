---
id: fund-three-clips
section: fundamentals
order: 161
level: A
title: Gradient clip、Advantage clip、Ratio clip 分别偏了什么？
quick: >-
  先分清裁剪的对象是 $g$、$\hat A$ 还是 $\rho$。Gradient clip
  限制这一步的梯度更新，裁剪前的估计器仍可能无偏；Advantage 或 reward clip 改变回报系数；PPO 的 ratio clip 使部分越界
  token 的梯度为 0，是有偏的 policy gradient 近似。
tags:
  - PPO
  - Gradient Clipping
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary
  - title: On the difficulty of training Recurrent Neural Networks
    url: 'https://arxiv.org/abs/1211.5065'
    type: secondary
  - title: MiniMax-M1 (CISPO)
    url: 'https://arxiv.org/abs/2506.13585'
    type: secondary
---

三种 clip 都能让训练更稳，但截的是三个不同的量，偏差出现的位置也不同：gradient clip 截的是 backpropagation 后的梯度 $g$，advantage clip 截的是乘在 $\nabla\log\pi$ 上的系数 $\hat A$，ratio clip 截的是重要性比 $\rho$ 在目标函数里的取值。`clip_grad_norm_`、`adv.clamp`、PPO 的 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$ 经常被笼统说成「为了稳定」，面试里要能分开讲。PPO 目标本身见 `pt-ppo-clip`。

## 三种 clip 各截了什么

Gradient clip 是 backpropagation 之后，如果 $\|\hat g\|\gt \tau$，就缩放到 $\tau$。$\hat g$ 作为 $\nabla J$ 的估计，在 clip 之前可以仍是无偏的；clip 之后，这一步更新就不再是沿那个无偏方向走任意步长了。它既不改 $\hat A$，也不改 $\rho$，是 RNN 和大模型防梯度爆炸的工程组件，见 `fund-gradclip`。所以别说「grad clip 让 policy gradient 有偏」，有偏的是被截断后的那一步 $\Delta\theta$，你在用的 advantage 公式没变。

Advantage / return / 奖励分数（reward）clip，比如 $\hat A\leftarrow\mathrm{clip}(\hat A,-c,c)$，或者把 reward model（RM）的分数限制在 $[-1,1]$。它直接改了乘在 $\nabla\log\pi$ 上的系数，期望变成 $\mathbb{E}[\nabla\log\pi\cdot\mathrm{clip}(A)]$，相对原来的 $J$ 有偏，换来的是不被极端轨迹主导。Reward normalization、除 $\sigma$ 也属于这一类「改系数」，见 `fund-adv-norm-bias`。

Ratio clip 出现在 PPO / GRPO 的 surrogate 里：

$$
\min\big(\rho_t\hat A_t,\;\mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\hat A_t\big).
$$

它截的是重要性比在目标函数里的取值。$A\gt 0$ 且 $\rho\gt 1+\varepsilon$ 时（负侧对称），这一项对 $\theta$ 的梯度为 0，这个 token 的这一项本轮不提供梯度。这是对 on-policy 梯度的有偏近似，用来限制一步走得太远，见 `baidu-ppo-clip-sign`。CISPO 改成截 $\rho$ 再 detach，越界 token 仍然有 $\nabla\log\pi$，偏的是权重，梯度并没有被关掉，见 `pt-cispo`。

## 叠在一起时别全截成 0

三层可以同时开，但有效更新可能被削弱好几次：ratio clip 已经把大部分 token 打成 0，advantage 再夹紧，最后 grad clip 再砍一刀。监控要对着看 clip fraction（ratio）、advantage 分位数、grad norm 触顶率。Ratio clip fraction 接近 1 时，先减 epoch、更频繁地 sampling 新轨迹（rollout），把 grad clip 再拧紧没用。

还有第四个，PPO 里的 value clip，它把 $V$ 的 target 相对旧 $V$ 夹紧，偏的是价值评估模型（critic）的回归目标，不直接改 policy 的 $\nabla\log\pi$，但下一轮 GAE 会吃进被夹过的 $V$。别把它和 ratio clip 混在一起报成「PPO 的 clip」。

## 追问

**Grad clip 会不会让 unbiased estimate 变有偏？**
看问的是哪一层。作为 $\mathbb{E}[\hat g]$ 的一步实现，会；作为「我用的 $\hat A$ 公式」，不会。

**Advantage clip 和 Huber 损失像吗？**
像，都在压极端系数。Huber 更常用在 critic loss 上；对 $\hat A$ 做硬 clip 更粗。

**只开 ratio clip 够不够？**
不够。在长 chain of thought（CoT，即分步推理过程）上，$\rho$ 连乘仍可能让少量 token 主导，见 `fund-token-is-var`。Ratio clip 管的是信任域，管不了回报的方差。

**GRPO 还要 grad clip 吗？**
要。组优势再漂亮，偶发的极大 $\nabla\log\pi$ 仍可能造成梯度爆炸，这两层互不替代。
