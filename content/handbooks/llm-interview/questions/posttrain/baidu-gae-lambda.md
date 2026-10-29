---
id: baidu-gae-lambda
section: posttrain
order: 204
level: A
title: 百度文心后训练：GAE 中 $\lambda$ 的作用，与偏差/方差如何权衡？
quick: >-
  $\lambda$ 决定 GAE 怎么在多步 TD 回报之间做指数加权混合：$\lambda\to 0$ 偏向
  1-step，偏置高、方差低；$\lambda\to 1$ 更接近 Monte Carlo，方差高、偏差低。PPO 里常取 $0.9$ 到
  $0.99$，要结合轨迹长度和价值估计的质量来调。
tags:
  - Baidu
  - GAE
  - PPO
  - '2026'
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百度 大模型后训练 一面（候选人原帖）
    url: 'https://www.nowcoder.com/discuss/863890669662674944'
    type: candidate-first-hand
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: 'https://arxiv.org/abs/1506.02438'
    type: primary
---

## 真题记录

- 公司：百度 · 文心一言
- 岗位：大模型 RL 后训练；2026-03-18 一面
- 原始措辞：**“generalized advantage estimation 是怎么计算？GAE 中 lambda 的作用，该值大小和 GAE 方差/偏差的关系”**

$\lambda$ 决定 GAE 怎么在多步 TD 回报之间做指数加权混合：$\lambda=0$ 只信 1-step TD，偏差大、方差小；$\lambda=1$ 退回 Monte Carlo，偏差小、方差大。它和折扣因子 $\gamma$ 是两件事，$\gamma$ 决定回报看多远，$\lambda$ 决定多步 TD 之间怎么混合。

白板我按这个顺序写：先定义 TD 残差 $\delta_t$，再写 $(\gamma\lambda)^l$ 的指数和，最后才讲 $0$ 和 $1$ 两个端点。只背「$\lambda$ 大方差大」不写公式，下一问「那 $\gamma$ 呢」就答不上来；把 $\lambda$ 说成学习率就更偏了。

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),\qquad
\hat A_t^{\mathrm{GAE}(\gamma,\lambda)}=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}.
$$

$\lambda=0$ 时 $\hat A_t=\delta_t$，完全相信当前的 $V$，偏差大、方差小，就是 1-step TD。$\lambda=1$ 时退回折扣回报减基线的 Monte Carlo 优势，偏差小、方差大。中间值在两者之间折中。PPO 里常取 $0.95$ 到 $0.99$，但这不是定理，要随轨迹长度和 critic 质量改。这里的 $V$ 来自价值评估模型（critic），不是 reward model（RM）：RM 给标量 $r$，critic 给基线，见 `ant-rm-vs-critic`。把 RM 分数直接当 $V$ 代进 GAE，公式左右就不是同一类量了。也正因为这样，没有 critic 就没有这根轴，GRPO 用组均值代替 $V(s)$，根本不算 GAE，见 `sys-rl-group-n`。

放到 LLM 上，token 级 RL 的轨迹极长。比如一道数学题，奖励只在最后判对错，前面大部分 $r_t=0$。$\lambda$ 小，优势压在最后几个 token 附近，chain of thought 中间几乎没有梯度；$V$ 还不准的话，早期 token 会系统性地偏，过程步骤学不动。$\lambda$ 大，终局奖励能往回传，但末端噪声也会沿 $(\gamma\lambda)^l$ 传回每一个思维 token，信号被淹没，方差按长度涨，长 CoT 上更明显。reverse KL 管的是相对 $\pi_{\mathrm{ref}}$ 的偏离，见 `fund-kl-directions`，它替代不了 $\lambda$。

所以要结合奖励稀疏度和算法来调。value network 跟不上策略的时候，宁可把 $\lambda$ 推向 1、偏 MC，也别把错误的 $V$ 当真理去降方差。如果任务能对同一题采 $n$ 条、奖励可验证，直接换 GRPO，$\lambda$ 和 critic 都绕开了。PPO clip 和 CISPO 管的是 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，和 GAE 是两回事，见 `pt-cispo`：优势估得再准，越界的 token 照样可能被 clip 掉。

## 追问

**$\gamma$ 和 $\lambda$ 哪个管方差？**
都管。$\gamma$ 砍远期回报，$(\gamma\lambda)^l$ 一起衰减多步混合。面试时要分开定义，别说「差不多」。

**没有 $V$ 能算 GAE 吗？**
不能，那就是 MC 了。GRPO 是另一种 baseline，别把组均值叫成 $\lambda$。

**长 CoT 上 $\lambda$ 怎么选？**
先查 critic 跟不跟得上，看 value 损失（loss）和解释方差。跟不上就加大 $\lambda$ 或者换组相对，别先加学习率。

**$\lambda=1$ 还要 clip 吗？**
要。advantage estimation 和信任域是两件事，MC 优势更噪，更需要 clip 或 CISPO。

**有过程奖励了还要 GAE 吗？**
要，但 $\lambda$ 可以更小，因为 $r_t$ 已经不稀疏了。这时过程奖励本身被 hack，比 $\lambda$ 选错更要命。
