---
id: arl-offline-policy-evaluation
section: agentrl
order: 191
level: S
title: 只有日志轨迹时，如何做 Agent 策略的离线评估（OPE）？
quick: 记录行为策略倾向分数，用 IS/DR/加权 IS 估计新策略价值，并报告置信区间与支撑不足区域；高偏差时回到交互式评测。
tags:
  - Offline Policy Evaluation
  - Importance Sampling
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Offline Reinforcement Learning tutorial (OPE)
    url: https://arxiv.org/abs/1909.03623
    type: primary
---

错法：拿新策略 $\pi_e$ 在旧日志上的平均回报当分数。日志来自行为策略 $\pi_b$，直接平均有偏：$\pi_e$ 爱走的动作若日志里没覆盖，你看到的是 $\pi_b$ 的世界。`data-offline-online-metric-gap` 讲的是偏好 AUC 与线上效用不是一回事；本题更窄：在已记录的 Agent 轨迹上估计 $V^{\pi_e}$，并且诚实报告支撑不足。OPE 教程把 IPS / DR 当反事实工具，前提是倾向分数可估、覆盖够。

## 重要性采样能用，但长工具链方差会炸

逐步 IS：

$$
w_{1:T}=\prod_{t=1}^{T}\frac{\pi_e(a_t\mid s_t)}{\pi_b(a_t\mid s_t)},\quad \hat V_{\mathrm{IS}}=\mathbb{E}_{\tau\sim\pi_b}[w_{1:T}R(\tau)]
$$

$T$ 一大，$w$ 要么爆炸要么全是 $0$。必须逐步截断（$w$ clamp）、加权 IS（自归一化）或 Doubly Robust：用 $Q$ 当控制变量，倾向只修正残差。报告置信区间，以及「有效样本量」过小的切片。那些切片的点估计不能当上线依据。逐步截断后估计有偏，这是用稳定性换无偏；面试里要主动说偏，不要假装 IPS 仍是无偏的黄金标准。

Agent 特有难点：开放文本动作的 $\pi(a\mid s)$ 几乎估不准；工具环境不可复现，同一 $(s,a)$ 再执行结果会变。实践上把动作拆开：对结构化 tool-call 头（工具名、离散参数）记 logprob / 行为策略倾向；对自由生成段不要硬做 IPS，改人工抽检或模拟器评测。日志必须在采集时写下 $\pi_b$ 的倾向，事后用另一模型拟合 $\hat\pi_b$ 会再加一层偏。长 horizon 可按子目标分段做 OPE，避免一条 $T\gt 40$ 的轨迹把所有权重打成零。

## OPE 只能做筛选，不能替代交互

覆盖差时 IS 方差爆炸，DR 的 $Q$ 也会在 OOD 上瞎编。协议：OPE 过门（下界 $\gt$ 基线且 CI 不跨零）→ 影子流量 / 小流量交互评测 → 才谈上线。支撑不足的意图、工具、长 horizon 切片标 `unsupported`，不要平均进总榜。对照 `data-offline-online-metric-gap`：那边是标签定义与效用；这边即使标签就是任务成功，只要策略覆盖差，OPE 仍然不可信。日志策略若几乎是确定性 greedy，新策略的探索动作会全部零覆盖，OPE 只能说「没法证伪」，不能说「新策略更好」。

没有 $\pi_b$ 倾向就没有 OPE；长轨迹要截断或 DR；文本动作别硬 IPS。OPE 筛掉明显更差的策略，筛不掉「日志里没走过的那条成功路径」。把 OPE 当 A/B 替代，是这题最常见的现场翻车。

## 追问

- **和离线/线上指标缺口那题？** 那题是代理指标 $\neq$ 线上效用。本题假设回报定义已对齐，问的是从 $\pi_b$ 日志估计 $\pi_e$ 的价值。
- **没有存 logprob 怎么办？** 先补采集。用另一策略拟合倾向，覆盖差时偏差很难诊断，只能当粗筛。
- **对话 Agent 能信 IPS 吗？** 动作空间巨大时通常不能。把 IPS 留给离散 tool 头，开放生成走成功率抽检。倾向分数还要按工具、意图分层看有效样本量，全局一个数会把无覆盖切片藏过去。
- **方差已经爆炸还刷 OPE？** 停。截断、缩短 horizon、或回到交互式评测。把爆炸权重平均进去会得到很自信的错数。加权 IS 能降方差，但在覆盖极差时会把估计钉在行为策略附近，看起来稳定、其实不敏感。
