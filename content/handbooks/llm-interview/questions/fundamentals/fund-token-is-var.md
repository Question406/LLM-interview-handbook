---
id: fund-token-is-var
section: fundamentals
order: 152
level: S
title: Token 级 importance ratio 连乘为什么方差会指数爆？
quick: >-
  序列比 $\rho_{1:T}=\prod_t\pi_\theta(y_t\mid\cdot)/\pi_{\mathrm{old}}(y_t\mid\cdot)$。即使每步
  $\mathbb{E}[\rho_t]=1$，乘积的二阶矩随 $T$ 走指数。长 CoT 上少数极端 token 就能让整段 $\rho$
  爆炸或塌到 0。工程上用逐步 $\rho_t$+clip、序列几何平均（GSPO）、或截断权重（CISPO / V-trace），都是用偏差换掉这条指数。
tags:
  - Importance Sampling
  - GSPO
  - PPO
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: GSPO — Group Sequence Policy Optimization
    url: https://arxiv.org/abs/2507.18071
    type: primary
  - title: IMPALA / V-trace
    url: https://arxiv.org/abs/1802.01561
    type: secondary
---

错法：把 PPO 的 $\rho_t$ 说成「完整轨迹 IS」。完整无偏校正是整段似然比；token 级 surrogate 已经是为了躲开连乘 的工程近似。基础见 `fund-is`：proposal 一旦在目标重要区域偏薄，$w=p/q$ 没有好的二阶矩。序列把这件事乘 $T$ 次。

## 为什么是指数，不是加几个噪声

一条回复 $y_{1:T}$，

$$
\rho_{1:T}=\prod_{t=1}^T\rho_t,\qquad\rho_t=\frac{\pi_\theta(y_t\mid x,y_{\lt t})}{\pi_{\mathrm{old}}(y_t\mid x,y_{\lt t})}.
$$

若各步近似独立且 $\mathbb{E}[\rho_t]=1$、$\mathbb{E}[\rho_t^2]=1+\varepsilon$，$\varepsilon\gt 0$，则

$$
\mathbb{E}[\rho_{1:T}^2]\approx(1+\varepsilon)^T,
$$

方差随长度指数涨。$\varepsilon$ 不必大：每个 token 只偏 1%，几百步就够让少数样本的权重吃掉整个 batch。这就是「horizon 一长，IS 先死」。LLM 的 $T$ 是数百到数千，比控制里的短轨迹苛刻得多，所以 fresh rollout 从可选变成默认纪律，见 `fund-onoff`。

MoE / 量化 / 混合精度会再给单步 $\rho_t$ 加噪声：路由不一致或 FP8 logp 差千分位，clip 区间又窄，看起来在训、梯度其实被极端比主导。训练图重算 logp 解决的是数值图，解决不了「真的 off-policy 连乘」；后者要缩短 stale 或改估计器。

## 三条工程出路，三条都有偏

| 做法 | 对连乘做了什么 | 偏在哪 |
| --- | --- | --- |
| Token 级 $\rho_t$ + PPO clip | 不写 $\prod\rho$，逐步 surrogate | 越界 token 梯度为 0 |
| GSPO 序列几何平均 | $\rho^{1/T}=\exp(\frac1T\sum\log\rho_t)$ | 粒度变成整段；局部极端被平均掉 |
| CISPO / V-trace / TIS | 把 $\rho$ 截断后仍更新 | $\mathbb{E}[\mathrm{clip}(\rho)f]\neq\mathbb{E}_\pi[f]$ |

PPO 论文允许同一批 rollout 上多个 epoch，靠 $\rho_t$ 靠近 1 加 clip。Epoch 多了、actor 更新快了，$(1+\varepsilon)^T$ 里的 $\varepsilon$ 变大，clip fraction 飙升，不是学习率 magically 不合适，是 IS 方差已经不可用。GSPO 把 clip 对象改成序列 likelihood ratio，针对的就是超长 CoT 上 token 级 $\rho$ 拉爆，见 `tencent-gspo-spo-comparison`。CISPO 不扔掉越界 token，只封顶系数，见 `pt-cispo`。V-trace 用 $\prod c_i$ 且 $c_i\le 1$ 挡住回传，见 `fund-vtrace`。

不要说「所以应该永远用序列 IS」。序列比仍是一个数，极端整段（格式崩了、突然换套路）还是会炸，只是不再被单个虚词主导。选择看 $T$ 和 stale：短、够新鲜，token 级 + 小 clip 够用；长思维链 / 异步队列，要序列粒度或截断权重，并报 ESS、$\rho$ 分位数，而不是只报 reward。

## 追问

- **逐步 $\rho_t$ 还无偏吗？** 在 $\theta=\theta_{\mathrm{old}}$ 处一阶等于 on-policy 梯度；离远了既偏也高方差。这是 PPO 的局部近似，不是轨迹 IS 定理。
- **对数空间求和能救方差吗？** $\sum\log\rho_t$ 数值稳定，但$\exp(\sum\log\rho_t)$ 仍是那个乘积。GSPO 除以 $T$ 才改变矩的增长方式。
- **温度、top-p 算进 $\mu$ 吗？** 算。采样侧的 truncation 是另一个 proposal。训练图若按满 softmax 算 $\pi$，而 generate 走 top-p，已经在做未声明的 IS。要么在 $\mu$ 里写上截断，要么接受偏差。
- **加长 clip $\varepsilon$ 能代替 fresh 吗？** 能拖一会儿，等于承认 surrogate 在更远处仍可信。通常先减 epoch、更勤同步，而不是把区间开到 2。
