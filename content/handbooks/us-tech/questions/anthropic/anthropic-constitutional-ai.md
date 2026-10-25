---
id: anthropic-constitutional-ai
section: anthropic
order: 3
level: S
title: Anthropic：Constitutional AI 和 RLHF 差在哪？监督从哪来？
quick: "RLHF 通常由人给回答偏好；CAI 让模型按人写的 constitution 批评、改写，再用 AI 比较产生偏好，训练偏好模型并做 RLAIF。人的工作转向原则设计、反例和抽查，偏好模型与强化学习仍然存在。"
tags:
  - Anthropic
  - Constitutional AI
  - RLAIF
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: Claude's Constitution
    url: https://www.anthropic.com/news/claudes-constitution
    type: primary
---

CAI 与 RLHF 的主要区别在反馈从哪里来。RLHF 由人逐条比较回答，CAI 由人先写原则，再让 AI 按原则批评、改写和比较。比如一条回答太容易拒绝，constitution 就需要包含避免过度拒答的要求，反馈模型也要据此判断。

## 原则怎样变成训练信号

论文先做监督阶段：模型读一条有害或越界回答，按 constitution 批评，再改写，用这些改写结果做 SL，让策略更无害且仍然有用。然后进入 RL 阶段，由模型按原则比较两条回答，产生偏好数据，训练偏好模型，再用 PPO 更新策略，这一阶段就是 RLAIF。

Constitution 是可版本化的条款列表，包括人权、非歧视、尊重法律、避免过度拒绝等。原则会冲突，例如有帮助与无害，通常优先无害，同时用单独条款限制过度拒绝。公开 constitution 也供人审查，区别于隐藏的 system prompt。

| | RLHF (InstructGPT) | CAI |
| --- | --- | --- |
| 偏好来源 | 人标 chosen/rejected | 模型按条款比较 |
| 人的工作 | 持续标注 | 写 / 改条款，抽查失败 case |
| 主要风险 | 标注员偏好、讨好 | 模型自嗨、条款漏洞、过度拒绝 |
| 规模 | 标注吞吐限制 | 原则一旦写好，反馈更便宜 |

CAI 降低了 harmlessness 标注的成本，也减少人反复查看有害内容的负担。它仍使用偏好模型和 RL，监督来自人制定的原则。InstructGPT 与 KL 的相关解释见 `openai-instructgpt-kl`、`pt-rlhf-why-reverse-kl`。

## 反馈更便宜后，仍要查偏差

RLAIF 也会出现 sycophancy 和钻奖励规则的空子。批评模型与训练模型要隔离版本，条款要配反例，人重点抽查原则失败模式；self-rewarding 的隔离问题见 `pt-self-rewarding-idpo`。

## 追问

**CAI 能和 RLHF 一起用吗？**
能。Helpfulness 可继续用人类偏好，harmlessness 使用 CAI，具体任务分开验证。

**把 constitution 放进 system prompt 就算 CAI 吗？**
那只是推理期约束。CAI 还要用条款生成批评、改写或偏好训练数据。

**computer use 确认框属于 constitution 吗？**
不属于。确认框是产品权限，见 `cu-sensitive-action-confirm`。条款影响语言和决策倾向，执行前的 OS 级权限仍由宿主管理。
