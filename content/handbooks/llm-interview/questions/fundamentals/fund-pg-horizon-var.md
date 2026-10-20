---
id: fund-pg-horizon-var
section: fundamentals
order: 155
level: S
title: 即使 on-policy，REINFORCE 的方差为什么仍随长度和稀疏奖励涨？
quick: "只有终局奖励时，每个 token 都乘同一个随机的 $r_T$，噪声被复制到整段。$T$ 个高度相关的 $\\nabla\\log\\pi$ 相加，方差随长度涨，和 IS 连乘无关。"
tags:
  - REINFORCE
  - Bias-Variance
  - Sparse Reward
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning
    url: https://link.springer.com/article/10.1007/BF00992696
    type: primary
---

常见误区是：把「方差大」全部推给 off-policy 的 $\rho$。Fresh、on-policy 的 REINFORCE 照样可以训不动：一条长 CoT 只在句末给 $0/1$，前面几百个 $\nabla\log\pi$ 乘的是同一个伯努利噪声。IS 连乘见 `fund-token-is-var`；本题是回报估计自己的方差。

## 稀疏终局：同一个 $r_T$ 被复制到每个 token

Reward-to-go 之后仍无偏，见 `fund-reward-to-go`。若中间 $r_t=0$、只有 $r_T\in\{0,1\}$，

$$
G_t=\gamma^{T-t}r_T,\qquad
\nabla_\theta\hat J=\sum_{t=0}^T\nabla_\theta\log\pi_\theta(y_t\mid x,y_{\lt t})\,\gamma^{T-t}r_T.
$$

$r_T$ 是整条轨迹共享的一个随机变量。成功一次，整段思考都被加强；失败一次，整段都被打压。对错与「哪个 token 有功」无关，这是 credit assignment，也是方差：$\mathrm{Var}(r_T)=p(1-p)$ 在 $p=0.5$ 时最大，见 `fund-bernoulli-adv-var`。长度 $T$ 越大，同一噪声乘进的 score 项越多，和的方差涨（项与项高度相关，不是 $\sqrt{T}$ 那种独立平均）。

$\gamma\lt 1$ 会把终局奖在早期 token 上打折，早期方差下来，但早期几乎分不到信号。那是改了目标，不是免费降噪，见 `fund-gamma-vs-lambda`。

## 和 IS 方差、组方差不要拧成一根

| 来源 | 什么在涨 | 典型对策 |
| --- | --- | --- |
| 轨迹回报（本题） | $T$、稀疏 $r_T$、环境随机性 | baseline / GAE / 组相对、过程奖、缩短 horizon |
| 重要性比 | $\prod\rho_t$ 或逐步 $\rho$ 偏离 1 | 用当前策略新采样的轨迹、clip、TIS、序列 ratio |
| 组统计 | 小 $G$、零方差组 | 加大 $G$、动态采样、RLOO |

把学习率加大，三根轴一起更吵。监控应对着看：回报标准差和成功轨迹占比（本题）；$\rho$ 分位数 / ESS / clip fraction（IS）；零方差组比例（GRPO）。只看平均 reward，会把「偶然全对的长回复」当成能力。

过程奖励、GAE 把 $r_T$ 沿 $(\gamma\lambda)^l$ 往回涂，是在分配各步贡献，同时引入 bootstrap 偏差。组相对不摊到逐步 state，只减「这道题的平均分」，对稀疏 $0/1$ 有效的前提是组里既有 0 又有 1。探索温度能提高撞到成功的概率，但不降低成功之后那条噪声的幅度，见 `fund-entropy-temp`、`arl-sparse-reward-exploration`。

## 追问

- **折扣能当方差公式吗？** 不能。小 $\gamma$ 让 $J$ 变短视。要降方差先减 baseline，再考虑 $\lambda$，最后才动 $\gamma$。
- **多采样平均能降到 0 吗？** 独立轨迹平均按 $1/\sqrt{N}$ 降。$N$ 是 prompt 数 × 组大小，不是一条里的 token 数。把 $T$ 个 token 当 $T$ 个独立样本会严重低估方差。
- **有 价值评估模型（critic） 就不用管 $T$ 了吗？** $V$ 准则 GAE 能砍掉未来噪声；$V$ 不准，小 $\lambda$ 只是换一种偏差。长思维链上 critic 往往跟不上，这才有 GRPO。
- **和 $\rho$ 连乘哪个先爆？** 同批数据、轻度 off-policy 时往往回报噪声先到；异步 stale、$T$ 到数千时 IS 先到。两根轴都要报。
