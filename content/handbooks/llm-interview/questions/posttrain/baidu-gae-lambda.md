---
id: baidu-gae-lambda
section: posttrain
order: 204
level: A
title: 百度文心后训练：GAE 中 $\lambda$ 的作用，与偏差/方差如何权衡？
quick: >-
  $\lambda$ 在多步 TD 回报之间做指数加权混合：$\lambda\to 0$ 偏置高、方差低（偏 1-step）；$\lambda\to 1$
  更接近蒙特卡洛，方差高、偏差低。PPO 里常取 $0.9$ 到 $0.99$，要结合轨迹长度和价值估计质量调。
tags:
  - Baidu
  - GAE
  - PPO
  - "2026"
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度 大模型后训练 一面（候选人原帖）
    url: https://www.nowcoder.com/discuss/863890669662674944
    type: candidate-first-hand
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
---

## 真题记录

- 公司：百度 · 文心一言
- 岗位：大模型 强化学习（RL） 后训练；2026-03-18 一面
- 原始措辞：**“广义优势估计是怎么计算？GAE中lambda的作用，该值大小和GAE 方差/偏差的关系”**

这块容易把 $\lambda$ 说成学习率，或和折扣因子 $\gamma$ 混成一个数。$\gamma$ 决定回报看多远；$\lambda$ 决定多步 TD 之间怎么混合。没有 价值评估模型（critic） 就没有这根轴，GRPO 用组均值代替 $V(s)$，根本不算 GAE，见 `sys-rl-group-n`。白板顺序：先定义 TD 残差 $\delta_t$，再写 $(\gamma\lambda)^l$ 的指数和，最后才谈 $0$ 和 $1$ 两个端点。只背「$\lambda$ 大方差大」而不写公式，下一问「那 $\gamma$ 呢」会答空。

## 公式：从 TD 残差到 GAE

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),\qquad
\hat A_t^{\mathrm{GAE}(\gamma,\lambda)}=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}.
$$

$\lambda=0$ 时 $\hat A_t=\delta_t$，完全相信当前 $V$，偏差大、方差小，是 1-step TD。$\lambda=1$ 时退回折扣回报减基线的 Monte Carlo 优势，偏差小、方差大。中间值在偏差与方差之间折中。PPO 里常取 $0.95$ 到 $0.99$，但这不是定理，要随轨迹长度和 critic 质量改。$V$ 来自 critic，不是 奖励模型（RM）：RM 给标量 $r$，critic 给基线，见 `ant-rm-vs-critic`。把 RM 分数直接当成 $V$ 代入 GAE，公式左右就不是同一类量。

LLM token 级 RL 轨迹极长。$\lambda$ 过大时，末端噪声会沿 $(\gamma\lambda)^l$ 传回每一个思维 token，信号被淹没；$\lambda$ 过小且 $V$ 不准时，早期 token 会系统性偏，过程步骤学不动。反向 KL 管的是对 $\pi_{\mathrm{ref}}$ 的偏离，见 `fund-kl-directions`，它不替代 $\lambda$。

## 结合奖励稀疏度和算法选型调整

稀疏终局奖（对/错、单测过/不过）时，前面大部分 $r_t=0$。小 $\lambda$ 把优势压在最后几个 token 附近，思维链中间几乎没梯度；大 $\lambda$ 把终局奖往回传，方差按长度涨，长 CoT 上更明显。价值网络跟不上政策时，宁可把 $\lambda$ 推向 1 偏 MC，也不要把错误的 $V$ 当成真理去降方差。若任务可对同一题采 $n$ 条、奖励可验证，直接换 GRPO，绕开 $\lambda$ 和 critic。PPO clip 与 CISPO 管的是 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，和 GAE 正交，见 `pt-cispo`：优势再准，越界 token 仍可能被 clip 掉。

## 追问

- **$\gamma$ 和 $\lambda$ 谁管方差？** 都管。$\gamma$ 砍远期回报，$(\gamma\lambda)^l$ 一起衰减多步混合。面试必须分开定义，不能说「差不多」。
- **没有 $V$ 能算 GAE 吗？** 不能。那是 MC。GRPO 是另一条 baseline，不要把组均值叫做 $\lambda$。
- **长 CoT 怎么选？** 先查 critic 是否跟得上（value 损失（loss）、解释方差）。跟不上就加大 $\lambda$ 或换组相对，不要先加学习率。
- **$\lambda=1$ 还要 clip 吗？** 要。优势估计和信任域是两件事。MC 优势更噪，反而更需要 clip 或 CISPO。
- **过程奖励还要 GAE 吗？** 要，但 $\lambda$ 可以更小，因为 $r_t$ 已经不稀疏。过程奖本身的 hack 比 $\lambda$ 更致命。
