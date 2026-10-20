---
id: fund-score-vs-reparam
section: fundamentals
order: 159
level: A
title: Score-function 和 reparameterization 差在哪？LLM 的 token 为什么只能走高方差那条？
quick: "Score-function 用 $f\\cdot\\nabla\\log\\pi$，不要求可微但方差大；reparam 让梯度穿过 $f$，方差低但要求采样可微。Token 是离散采样，verifier 也不可微，只能走 score-function。"
tags:
  - Policy Gradient
  - Reparameterization
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Auto-Encoding Variational Bayes
    url: https://arxiv.org/abs/1312.6114
    type: primary
  - title: Gradient Estimation Using Stochastic Computation Graphs
    url: https://arxiv.org/abs/1506.05254
    type: primary
  - title: Categorical Reparameterization with Gumbel-Softmax
    url: https://arxiv.org/abs/1611.01144
    type: secondary
---

常见误区是：「策略梯度方差大，换成 VAE 那种 reparam 就好了」。两条是不同的随机计算图，不是同一估计器的两个超参。LLM 的动作是离散 token，验证器、用户和工具等环境对 token 序列不可微，只能走 score-function。

## 两条梯度

目标 $\mathbb{E}_{a\sim\pi_\theta}[f(a)]$。$f$ 可以是回报、优势、或任意下游标量。

Score-function（likelihood ratio / REINFORCE）：

$$
\nabla_\theta\mathbb{E}_{a\sim\pi_\theta}[f(a)]=\mathbb{E}_{a\sim\pi_\theta}\big[f(a)\,\nabla_\theta\log\pi_\theta(a)\big].
$$

不要求 $f$ 可微，不要求 $a$ 连续。代价是 $f$ 的噪声完整乘进梯度，必须靠 baseline / GAE / 组相对降方差，见 `fund-pg-unbiased-ops`。

Reparameterization：若 $a=g(\theta,\varepsilon)$，$\varepsilon$ 与 $\theta$ 无关（如 $\varepsilon\sim\mathcal{N}(0,1)$，$a=\mu+\sigma\varepsilon$），

$$
\nabla_\theta\mathbb{E}_\varepsilon[f(g(\theta,\varepsilon))]=\mathbb{E}_\varepsilon\big[\nabla_a f\cdot\nabla_\theta g\big].
$$

梯度穿过 $f$。$f$ 平滑时，这通常比 score-function 方差小一个数量级，VAE 的编码器走这条。要求：$g$ 对 $\theta$ 可微，且你能把采样写成这种噪声注入。

## 为什么 token 走不了低方差那条

$\mathrm{Categorical}(\mathrm{softmax}(z_\theta))$ 的 `sample` 是 argmax 一条 Gumbel 或从多项式抽取，对 logits 几乎处处不可微。工具返回、代码是否通过、数学填空对错，更没有 $\partial f/\partial y_t$。所以 PPO / GRPO 全部是 score-function：损失长得像 $-\log\pi\cdot\hat A$，看起来像加权交叉熵损失（CE），数学上是 REINFORCE 而不是监督学习。

Gumbel-softmax / straight-through 用连续松弛近似离散采样，梯度能穿过，但松弛分布不是原来的 $\pi$，有偏。温度越低越接近离散、方差越大；温度高更稳、离真正的 token 采样更远。生成式 LLM 强化学习（RL） 几乎不用它当主路径，因为 $f$ 仍不可微（你松弛了采样，没松弛 verifier）。

连续动作控制（机器人扭矩）才是 reparam 的主场。不要把 SAC / DDPG 的「低方差策略梯度」直接许诺给 token RL。

## 追问

- **对 logits 的 CE 不也是可微吗？** 监督微调（SFT） 的 CE 是对已给定 token 的 $\log\pi$，没有对「采样哪个 token」求导。RL 要改的是采样分布下 $f$ 的期望，多了 $\nabla\log\pi\cdot f$ 这一层。
- **直通估计器（STE）无偏吗？** 一般有偏。前向离散、反向当恒等，是启发式。
- **那蒸馏 / OPD 为什么方差小？** 监督在 token 分布上，每步都有稠密 $f$，但仍是对已采样前缀的 $\log\pi$，不是把离散采样 reparam 掉。见 `pt-on-policy-distillation`。
- **score-function 能对连续动作用吗？** 能，只是通常更吵。有 reparam 时没理由不用。
