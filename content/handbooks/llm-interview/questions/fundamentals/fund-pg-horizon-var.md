---
id: fund-pg-horizon-var
section: fundamentals
order: 155
level: S
title: 即使 on-policy，REINFORCE 的方差为什么仍随长度和稀疏奖励涨？
quick: "只有终局奖励时，每个 token 的 $\\nabla\\log\\pi$ 都乘同一个随机的 $r_T$，这份噪声被复制到整段。$T$ 个高度相关的项相加，方差随长度涨，和 IS 连乘无关，on-policy 也躲不掉。"
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

因为稀疏的终局奖励被复制到了每个 token 上。一条长 CoT 只在句末给 $0/1$，前面几百个 $\nabla\log\pi$ 乘的是同一个伯努利噪声，长度越长，乘进这份噪声的项越多，方差就越大。这是回报估计自己的方差，fresh、on-policy 的 REINFORCE 照样会训不动，把「方差大」全推给 off-policy 的 $\rho$ 是不对的。IS 连乘是另一件事，见 `fund-token-is-var`。

## 同一个 $r_T$ 被复制到每个 token

做了 reward-to-go 之后估计仍然无偏，见 `fund-reward-to-go`。若中间 $r_t=0$、只有 $r_T\in\{0,1\}$，

$$
G_t=\gamma^{T-t}r_T,\qquad
\nabla_\theta\hat J=\sum_{t=0}^T\nabla_\theta\log\pi_\theta(y_t\mid x,y_{\lt t})\,\gamma^{T-t}r_T.
$$

$r_T$ 是整条轨迹共享的一个随机变量。成功一次，整段思考都被加强；失败一次，整段都被打压，和哪个 token 真正有功没关系。比如一段推理前面都对、最后一步算错，前面那些正确的步骤也跟着被压下去。这既是 credit assignment 问题，也是方差问题：$\mathrm{Var}(r_T)=p(1-p)$ 在 $p=0.5$ 时最大，见 `fund-bernoulli-adv-var`。长度 $T$ 越大，乘进同一份噪声的 score 项越多，和的方差就涨；这些项彼此高度相关，不会像独立样本那样按 $\sqrt{T}$ 平均掉。

$\gamma\lt 1$ 会把终局奖励在早期 token 上打折，早期的方差下来了，可早期也几乎分不到信号。它改的是目标，算不上免费降噪，见 `fund-gamma-vs-lambda`。

## 和 IS 方差、组方差分开看

| 来源 | 什么在涨 | 典型对策 |
| --- | --- | --- |
| 轨迹回报（本题） | $T$、稀疏 $r_T$、环境随机性 | baseline / GAE / 组相对、过程奖、缩短 horizon |
| 重要性比 | $\prod\rho_t$ 或逐步 $\rho$ 偏离 1 | 用当前策略新 sampling 的轨迹、clip、TIS、序列 ratio |
| 组统计 | 小 $G$、零方差组 | 加大 $G$、动态 sampling、RLOO |

把学习率加大，三条轴会一起变吵。监控也要对着看：回报标准差和成功轨迹占比对应本题，$\rho$ 分位数 / ESS / clip fraction 对应 IS，零方差组比例对应 GRPO。只看平均 reward，会把「偶然全对的长回复」当成能力。

对策上，过程奖励和 GAE 把 $r_T$ 沿 $(\gamma\lambda)^l$ 往回分摊，是在分配各步的贡献，同时引入 bootstrap 偏差。组相对优势不摊到逐步的 state，只减掉「这道题的平均分」，对稀疏 $0/1$ 奖励有效的前提是组里既有 0 又有 1。提高探索温度能增加撞到成功的概率，但成功之后那份噪声的幅度不会变小，见 `fund-entropy-temp`、`arl-sparse-reward-exploration`。

## 追问

**折扣能当降方差的办法吗？**
不能。小 $\gamma$ 会让 $J$ 变短视。要降方差，先减 baseline，再考虑 $\lambda$，最后才动 $\gamma$。

**多 sampling 平均能把方差降到 0 吗？**
降不到，独立轨迹平均按 $1/\sqrt{N}$ 降。$N$ 是 prompt 数 × 组大小，一条回复里的 token 数不算。把 $T$ 个 token 当成 $T$ 个独立样本，会严重低估方差。

**有价值评估模型（critic）就不用管 $T$ 了吗？**
要看 $V$ 准不准。$V$ 准，GAE 能砍掉未来的噪声；$V$ 不准，小 $\lambda$ 只是换了一种偏差。长 chain of thought 上 critic 往往跟不上，这也是有 GRPO 的原因。

**回报噪声和 $\rho$ 连乘，哪个先爆？**
同一批数据、轻度 off-policy 时，往往回报噪声先到；异步 stale、$T$ 到数千时，IS 先到。两条轴都要报。
