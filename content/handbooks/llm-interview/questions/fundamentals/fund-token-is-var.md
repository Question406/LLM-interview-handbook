---
id: fund-token-is-var
section: fundamentals
order: 152
level: S
title: Token 级 importance ratio 连乘为什么方差会指数爆？
quick: "因为序列比是 $T$ 个逐步比率的连乘。即使每步 $\\mathbb{E}[\\rho_t]=1$，只要 $\\mathbb{E}[\\rho_t^2]=1+\\varepsilon$，二阶矩就约为 $(1+\\varepsilon)^T$，随长度指数增长。"
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

因为序列的重要性比是 $T$ 个逐步比率的连乘，每一步哪怕只多出一点二阶矩，乘 $T$ 次之后也会按 $(1+\varepsilon)^T$ 指数增长。完整的无偏校正就是整段似然比；PPO 里逐 token 的 $\rho_t$ 已经是为了躲开连乘做的工程近似，别把它说成「完整轨迹 IS」。基础见 `fund-is`：proposal 一旦在目标的重要区域偏薄，$w=p/q$ 就没有好的二阶矩，序列把这件事乘了 $T$ 次。

## 为什么是指数，不是加几个噪声

一条回复 $y_{1:T}$，

$$
\rho_{1:T}=\prod_{t=1}^T\rho_t,\qquad\rho_t=\frac{\pi_\theta(y_t\mid x,y_{\lt t})}{\pi_{\mathrm{old}}(y_t\mid x,y_{\lt t})}.
$$

若各步近似独立且 $\mathbb{E}[\rho_t]=1$、$\mathbb{E}[\rho_t^2]=1+\varepsilon$，$\varepsilon\gt 0$，则

$$
\mathbb{E}[\rho_{1:T}^2]\approx(1+\varepsilon)^T,
$$

方差随长度指数涨。$\varepsilon$ 不必大：每个 token 只偏 1%，几百步就足以让少数样本的权重主导整个 batch。LLM 的 $T$ 是数百到数千，比控制任务里的短轨迹苛刻得多，所以通常要用当前策略重新采样轨迹，见 `fund-onoff`。

MoE、量化、混合精度还会给单步 $\rho_t$ 再加噪声：路由不一致，或者 FP8 的 logp 差了千分位，clip 区间又窄，看起来在训，梯度其实被极端比率主导。在训练图里重算 logp 解决的是数值图的问题，解决不了真正 off-policy 的连乘；后者要减少轨迹滞后，或者换估计器。

## 三条工程出路，三条都有偏

| 做法 | 对连乘做了什么 | 偏在哪 |
| --- | --- | --- |
| Token 级 $\rho_t$ + PPO clip | 不写 $\prod\rho$，逐步 surrogate | 越界 token 梯度为 0 |
| GSPO 序列几何平均 | $\rho^{1/T}=\exp(\frac1T\sum\log\rho_t)$ | 粒度变成整段；局部极端被平均掉 |
| CISPO / V-trace / TIS | 把 $\rho$ 截断后仍更新 | $\mathbb{E}[\mathrm{clip}(\rho)f]\neq\mathbb{E}_\pi[f]$ |

PPO 论文允许在同一批采样轨迹（rollout）上跑多个 epoch，靠的是 $\rho_t$ 靠近 1 再加 clip。epoch 多了、actor 更新快了，$(1+\varepsilon)^T$ 里的 $\varepsilon$ 就变大，clip fraction 飙升，这时要先怀疑 IS 方差已经过大，别全归到学习率头上。GSPO 把 clip 对象改成序列 likelihood ratio，针对的就是超长 CoT 上 token 级 $\rho$ 被拉爆，见 `tencent-gspo-spo-comparison`。CISPO 不扔掉越界 token，只给系数封顶，见 `pt-cispo`。V-trace 用 $\prod c_i$ 且 $c_i\le 1$ 挡住回传，见 `fund-vtrace`。

也别说「所以应该永远用序列 IS」。序列比仍是一个数，整段出现极端情况，比如格式崩了、突然换了套路，照样会数值异常，只是不再被单个虚词主导。怎么选看 $T$ 和数据有多 stale：短、够新鲜，token 级加小 clip 就够；长思维链或异步队列，要用序列粒度或截断权重，并报 ESS 和 $\rho$ 分位数，光报奖励分数（reward）不够。

## 追问

**逐步 $\rho_t$ 还无偏吗？**
只在 $\theta=\theta_{\mathrm{old}}$ 处一阶等于 on-policy 梯度，离远了既有偏又高方差。这是 PPO 的局部近似，和轨迹 IS 定理是两回事。

**在对数空间求和能救方差吗？**
救不了。$\sum\log\rho_t$ 数值上稳定，可 $\exp(\sum\log\rho_t)$ 仍是那个乘积。GSPO 除以 $T$ 之后，矩的增长方式才变了。

**温度、top-p 要算进 $\mu$ 吗？**
要算。采样侧的 truncation 是另一个 proposal。训练图如果按满 softmax 算 $\pi$，generate 却走 top-p，其实已经在做一次没声明的 IS。要么在 $\mu$ 里写上截断，要么接受这个偏差。

**把 clip 的 $\varepsilon$ 放大能代替 fresh 吗？**
能拖一会儿，等于承认 surrogate 在更远处仍可信。通常应该先减 epoch、更勤地同步，别把区间开到 2。
