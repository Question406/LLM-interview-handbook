---
id: ant-rm-vs-critic
section: posttrain
order: 140
level: S
title: 蚂蚁：有了 Reward Model 为什么还需要 Critic？
quick: >-
  RM 给整段或可验证结果打标量奖励，不估计状态价值；Critic / value 预测 $V(s)$，给 GAE 做基线以降方差。没有
  Critic，PPO 仍能跑，但优势估计更噪，长轨迹尤其不稳。
tags:
  - Ant Group
  - PPO
  - Reward Model
  - Critic
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
  - title: 26秋招蚂蚁金服大模型算法一面
    url: https://www.nowcoder.com/feed/main/detail/e2585943c7874b3081b0878b646b6f01
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“为什么有了reward model还需要critic model？critic model作用是什么？”**

错法：「RM 已经会估价值，所以不需要 critic」。RM（或规则 verifier）回答的是「这条轨迹好不好」，输出标量 $r(x,y)$；它不回答「在这个前缀状态下，当前策略的期望回报是多少」。PPO 更新用的是优势 $A_t$，没有基线就只剩高方差的 Monte Carlo 回报，长思维链尤其不稳。GRPO 用同题组均值代替 learned $V$，那是另一条估计器，不能反过来说 PPO 里的 RM 已经包含 critic，见 `sys-rl-group-n`。两个模型的标签、更新频率和故障模式都不同，混成一个「打分模型」当场穿帮。

## 两个模型，两种标签

RM 吃偏好对或结果标签，拟合 $r(x,y)$，训练时策略可以冻结，甚至可以完全换成可执行 verifier。它给的是轨迹级或结果级的标量，通常不条件于中间前缀，也不随 $\pi$ 漂移而重新定义「好」。Critic 拟合 $V_\psi(s_t)\approx\mathbb{E}[G_t\mid s_t]$，标签来自当前策略的回报，政策一变，$V$ 的目标就变，必须跟 actor 一起更新。故障也不同：RM 错是奖励偏差，hack、拍马、泄漏测试；Critic 错是方差与偏差的权衡，GAE 的 $\lambda$ 就是这根轴。

白板写 TD 残差和 GAE：

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),\qquad
\hat A_t^{\mathrm{GAE}}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

没有 $V$，就退回 $\hat A_t=G_t-\bar G$。LLM 一条回复几十到上百 token，MC 噪声会淹没稀疏的终局奖。PPO 没有 critic 仍能跑，只是优势更噪、clip 更容易被噪声驱动。反向 KL 锚的是 $\pi_\theta$ 对 $\pi_{\mathrm{ref}}$，见 `fund-kl-directions`，它不替代价值估计。

## 谁可以弱化 Critic

可验证、同一 prompt 能采到对错混合时，GRPO 用

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}
$$

当 baseline，省一张和 actor 同规模的 value 网。前提是 $n\gt 1$；整组同奖励则优势为 0，这一步没有方向。复杂连续权衡、奖励稀疏到无法在组内对照、或必须把过程价值估出来时，仍要 critic。不要把「R1 用了 GRPO」说成「PPO 里 RM 已经够了」：那是换了算法，不是 RM 兼任了 $V$。金融场景把合规失败写成 RM / 硬门；critic 只负责降方差，不负责审计。

## 追问

- **RM 能不能当 $V$？** 不能。RM 不条件于前缀，也不随 $\pi$ 变，给的是「好不好」不是「还值多少」。
- **$\lambda$ 和 critic 质量？** critic 准可以把 $\lambda$ 调小、信 1-step；不准时把 $\lambda$ 调向 1，更接近 MC，见 `baidu-gae-lambda`。
- **没有 critic 的 PPO clip 还要吗？** 要。Clip 管的是 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，和 baseline 正交；CISPO 则改 clip 对象，见 `pt-cispo`。
- **金融场景 critic 管合规吗？** 不管。规则失败进 RM 或硬门；critic 估错只会让更新更噪，不会自动学会拒答。
- **过程 RM 是不是 critic？** 不是。过程奖励仍是 $r_t$，不是 $V(s)$。可以同时存在，但训练目标不同。
