---
id: arl-offline-policy-evaluation
section: agentrl
order: 191
level: S
title: 只有日志轨迹时，如何做 Agent 策略的离线评估（OPE）？
quick: >-
  能做，前提是采集日志时记下行为策略选动作的概率，再用 IS、加权 IS 或 DR 估新策略回报，并报 confidence interval
  和有效样本量。长工具链会让权重爆炸，要截断或分段；新策略的动作在日志里缺少覆盖时估计不可靠，OPE 只能做筛选，最后还要回到交互评测。
tags:
  - Offline Policy Evaluation
  - Importance Sampling
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Offline Reinforcement Learning tutorial (OPE)
    url: 'https://arxiv.org/abs/1909.03623'
    type: primary
---

能做，但前提是采集日志时记下了行为策略选每个动作的概率。有了它，就用 IS、加权 IS 或 DR 估新策略的回报，同时报 confidence interval 和有效样本量；新策略爱走的动作在日志里没覆盖到时，估计就不可靠，要回到交互评测。

最常见的错，是拿新策略 $\pi_e$ 在旧日志上的平均回报当分数。日志来自行为策略 $\pi_b$，直接平均是有偏的。比如旧策略几乎总是先调搜索工具，新策略喜欢先问用户澄清，那日志里几乎没有「先澄清」之后会发生什么，你看到的还是 $\pi_b$ 的世界。OPE 教程把 IPS / DR 当成反事实工具，前提就是倾向分数能估、覆盖够。

## 长工具链会放大 importance sampling 的方差

逐步 IS 是这样算的：

$$
w_{1:T}=\prod_{t=1}^{T}\frac{\pi_e(a_t\mid s_t)}{\pi_b(a_t\mid s_t)},\quad \hat V_{\mathrm{IS}}=\mathbb{E}_{\tau\sim\pi_b}[w_{1:T}R(\tau)]
$$

$T$ 一大，$w$ 要么爆炸，要么全是 $0$。所以要逐步截断（$w$ clamp）、用加权 IS（self-normalization），或者用 Doubly Robust：拿 $Q$ 当控制变量，倾向只修正残差。截断后估计是有偏的，这是拿稳定性换无偏，面试里要主动说出来，别把 IPS 讲成仍然无偏的黄金标准。有效样本量过小的切片要单独报出来，那些切片的 point estimate 不能当上线依据。

Agent 还有两个特有的难点：开放文本动作的 $\pi(a\mid s)$ 几乎估不准；工具环境不可复现，同一个 $(s,a)$ 再执行一次结果会变。实践上把动作拆开，对结构化的 tool-call 头（工具名、离散参数）记 logprob 或行为策略倾向；自由生成段别硬做 IPS，改成人工抽检或模拟器评测。倾向要在采集时就写下来，事后用另一个模型拟合 $\hat\pi_b$ 会再多一层偏。长 horizon 可以按子目标分段做 OPE，免得一条 $T\gt 40$ 的轨迹把所有权重打成零。

## OPE 只能做筛选，代替不了交互

覆盖差时 IS 方差爆炸，DR 的 $Q$ 也会在 out-of-distribution 数据（OOD，即与训练数据明显不同的数据）上凭空生成。我的流程是先满足 OPE acceptance criteria（下界 $\gt$ 基线且 CI 不跨零），再上影子流量或小流量交互评测，最后才谈上线。支撑不足的意图、工具、长 horizon 切片标成 `unsupported`，别平均进总榜。日志策略要是几乎是确定性的 greedy，新策略的探索动作全都零覆盖，OPE 只能说「没法证伪」，说不了「新策略更好」。它能筛掉明显更差的策略，筛不掉日志里没走过的那条成功路径；把 OPE 当成 A/B 的替代品，是这题现场最常见的翻车。

## 追问

**和离线 / 线上指标缺口那题有什么区别？**
`data-offline-online-metric-gap` 讲的是代理指标 $\neq$ 线上效用，比如偏好 AUC 和线上效用是两回事。这题假设回报定义已经对齐，问的是从 $\pi_b$ 的日志估 $\pi_e$ 的价值 $V^{\pi_e}$，并且诚实报告支撑不足；就算标签就是任务成功，只要策略覆盖差，OPE 照样不可信。

**没有存 logprob 怎么办？**
先补采集。用另一个策略去拟合倾向，覆盖差时偏差很难诊断，只能当粗筛。

**对话 Agent 能信 IPS 吗？**
动作空间巨大时通常不能。IPS 留给离散的 tool 头，开放生成走成功率抽检。倾向分数还要按工具、意图分层看有效样本量，全局一个数会把没覆盖的切片藏起来。

**方差已经爆炸了，还要接着刷 OPE 吗？**
停下来。截断、缩短 horizon，或者回到交互式评测；把爆炸的权重平均进去，会得到一个很自信的错数。加权 IS 能降方差，但覆盖极差时会把估计钉在行为策略附近，看起来稳定，其实不敏感。
