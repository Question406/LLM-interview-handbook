---
id: fund-score-vs-reparam
section: fundamentals
order: 159
level: A
title: Score-function 和 reparameterization 差在哪？LLM 的 token 为什么只能走高方差那条？
quick: "Score-function 用 $f\\cdot\\nabla\\log\\pi$，不要求可微，但方差大；reparam 让梯度穿过 $f$，方差低，但要求采样可微。Token 是离散采样，verifier 也不可微，所以 LLM 只能走 score-function。"
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

LLM 只能走 score-function，因为 reparameterization 要的两个前提都不满足：动作是离散 token，采样对 logits 不可微；奖励来自验证器、用户或工具，对 token 序列也不可微。所以「策略梯度方差大，换成 VAE 那种 reparam 就好了」行不通，这两条对应的是不同的随机计算图，没法当成同一个估计器的两个超参来调。

## 两条梯度

目标是 $\mathbb{E}_{a\sim\pi_\theta}[f(a)]$，$f$ 可以是回报、优势，或任意下游标量。

Score-function（也叫 likelihood ratio / REINFORCE）是

$$
\nabla_\theta\mathbb{E}_{a\sim\pi_\theta}[f(a)]=\mathbb{E}_{a\sim\pi_\theta}\big[f(a)\,\nabla_\theta\log\pi_\theta(a)\big].
$$

它不要求 $f$ 可微，也不要求 $a$ 连续。代价是 $f$ 的噪声完整地乘进梯度，只能靠 baseline、GAE、组相对优势去降方差，见 `fund-pg-unbiased-ops`。

Reparameterization 要求能把采样写成 $a=g(\theta,\varepsilon)$，$\varepsilon$ 与 $\theta$ 无关，比如 $\varepsilon\sim\mathcal{N}(0,1)$、$a=\mu+\sigma\varepsilon$。这时

$$
\nabla_\theta\mathbb{E}_\varepsilon[f(g(\theta,\varepsilon))]=\mathbb{E}_\varepsilon\big[\nabla_a f\cdot\nabla_\theta g\big].
$$

梯度穿过了 $f$。$f$ 平滑时，这通常比 score-function 的方差小一个数量级，VAE 的编码器走的就是这条。条件是 $g$ 对 $\theta$ 可微，并且你能把采样写成这种噪声注入的形式。

## Token 为什么走不了低方差那条

$\mathrm{Categorical}(\mathrm{softmax}(z_\theta))$ 的 `sample` 要么是对 Gumbel 取 argmax，要么从多项式里抽，对 logits 几乎处处不可微。工具返回了什么、代码过没过、数学填空对不对，更没有 $\partial f/\partial y_t$ 可言。比如一道数学题答对给 1、答错给 0，你没法问「把某个 token 的 logit 挪一点，奖励会变多少」。所以 PPO / GRPO 全部是 score-function。损失长得像 $-\log\pi\cdot\hat A$，看起来像加权交叉熵损失（CE），数学上是 REINFORCE，和监督学习是两回事。

Gumbel-softmax / straight-through 用连续松弛来近似离散采样，梯度能穿过去，但松弛后的分布已经不是原来的 $\pi$，所以有偏。温度越低越接近离散，方差越大；温度高更稳，离真正的 token 采样也更远。生成式 LLM 强化学习（RL）几乎不拿它当主路径，因为松弛的只是采样，verifier 那个 $f$ 还是不可微。

连续动作控制，比如机器人扭矩，才是 reparam 的主场。SAC / DDPG 那种「低方差策略梯度」别直接许诺给 token RL。

## 追问

**对 logits 的 CE 不也是可微的吗？**
可微，但求导的对象不一样。监督微调（SFT）的 CE 是对已经给定的 token 求 $\log\pi$，没有对「采样哪个 token」求导。RL 要改的是采样分布下 $f$ 的期望，多了 $\nabla\log\pi\cdot f$ 这一层。

**直通估计器（STE）无偏吗？**
一般有偏。前向离散、反向当恒等，属于启发式。

**那蒸馏 / OPD 为什么方差小？**
因为监督在 token 分布上，每一步都有稠密的 $f$。它仍然是对已采样前缀的 $\log\pi$，并没有把离散采样 reparam 掉，见 `pt-on-policy-distillation`。

**score-function 能用在连续动作上吗？**
能，只是通常更吵。有 reparam 可用时，没理由不用。
