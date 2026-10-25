---
id: ant-rm-vs-critic
section: posttrain
order: 140
level: S
title: 蚂蚁：有了 Reward Model 为什么还需要 Critic？
quick: "奖励模型（RM）回答「这条轨迹好不好」，给整段或可验证结果一个标量奖励，不估计状态价值；Critic 回答「在这个前缀状态下还值多少」，预测 $V(s)$ 给 GAE 当基线来降方差。没有 Critic，PPO 也能跑，但优势估计更噪，长轨迹尤其不稳。"
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

因为两者回答的不是同一个问题。奖励模型（RM）或规则验证器回答「这条轨迹好不好」，输出标量 $r(x,y)$；critic 回答「在这个前缀状态下，当前策略的期望回报是多少」，给 PPO 算优势时当基线。没有基线，优势就只剩高方差的 Monte Carlo 回报，长思维链上尤其不稳。

举个例子，一道数学题的回复写到一半，RM 没法告诉你此刻这条回复「还值多少」，它只在整段写完后给一个分。PPO 更新要的是每个位置的优势 $A_t$，这个位置上的基线得由价值评估模型（critic）给。有人会说「RM 已经会估价值，所以不需要 critic」，把两个模型混成一个「打分模型」来讲，追问一下就露馅了。

两个模型的标签、更新频率和故障模式都不同。RM 吃偏好对或结果标签，拟合 $r(x,y)$，训练时策略可以冻结，甚至可以整个换成可执行的 verifier。它给的是轨迹级或结果级的标量，通常不条件于中间前缀，也不会因为 $\pi$ 漂移就重新定义什么叫好。Critic 拟合 $V_\psi(s_t)\approx\mathbb{E}[G_t\mid s_t]$，标签来自当前策略的回报，策略一变，$V$ 的目标跟着变，所以必须和 actor 一起更新。出错的方式也不一样：RM 错了是奖励偏差，比如被 hack、拍马屁、泄漏测试；critic 错了是方差和偏差的权衡问题，GAE 的 $\lambda$ 就是调这根轴的。

白板上写 TD 残差和 GAE：

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),\qquad
\hat A_t^{\mathrm{GAE}}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

没有 $V$，就退回 $\hat A_t=G_t-\bar G$。LLM 一条回复几十到上百 token，MC 噪声会淹没稀疏的终局奖励。PPO 没有 critic 也能跑，只是优势更噪，clip 更容易被噪声驱动。反向 KL 锚的是 $\pi_\theta$ 相对 $\pi_{\mathrm{ref}}$ 的偏离，见 `fund-kl-directions`，它替代不了价值估计。

那什么时候可以弱化 critic？任务可验证、同一个输入提示能采到对错混合时，GRPO 用组内相对奖励当 baseline：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}
$$

这样省掉一张和 actor 同规模的 value 网。前提是 $n\gt 1$；整组同奖励时优势为 0，这一步没有方向，见 `sys-rl-group-n`。GRPO 用组均值代替学出来的 $V$，那是另一种估计器，不能反过来说 PPO 里的 RM 已经包含了 critic。要做复杂的连续权衡、奖励稀疏到组内对照不出来，或者必须把过程价值估出来时，还是要 critic。别把「R1 用了 GRPO」说成「PPO 里 RM 已经够了」，那是换了算法，RM 并没有兼任 $V$。金融场景把合规失败写进 RM 或硬门；critic 只负责降方差，不负责审计。

## 追问

**RM 能不能直接当 $V$ 用？**
不能。RM 不条件于前缀，也不随 $\pi$ 变，它给的是「好不好」，不是「还值多少」。

**$\lambda$ 和 critic 质量有什么关系？**
critic 准，可以把 $\lambda$ 调小、多信 1-step；不准就把 $\lambda$ 往 1 调，更接近 MC，见 `baidu-gae-lambda`。

**没有 critic 的 PPO 还要 clip 吗？**
要。clip 管的是 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，和 baseline 是两回事；CISPO 则是改了 clip 的对象，见 `pt-cispo`。

**金融场景里 critic 管合规吗？**
不管。规则失败进 RM 或硬门；critic 估错只会让更新更噪，不会自己学会拒答。

**过程 RM 算不算 critic？**
不算。过程奖励仍然是 $r_t$，不是 $V(s)$。两者可以同时存在，训练目标不同。
