---
id: anthropic-constitutional-ai
section: anthropic
order: 3
level: S
title: Anthropic：Constitutional AI 和 RLHF 差在哪？监督从哪来？
quick: >-
  RLHF 的偏好来自人；CAI 用一份书面 constitution，让模型自己批评 / 改写，再对 AI 反馈做 RL（RLAIF）。人从逐条打偏好，改成写原则和抽查。它不取消人，也不等于「没有奖励模型」。
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

Anthropic 研究 / 对齐岗会把这篇当背景，不一定照读论文提问。和 OpenAI InstructGPT 对照着讲最清楚：人都在环里，但人做的事从「每条偏好」变成「原则 + 抽查」。RLHF 细节见 `openai-instructgpt-kl` 和 `pt-rlhf-why-reverse-kl`。

## 两段：SL 批评改写，再 RLAIF

论文流程：

1. **监督阶段。** 有害或越界的回答，模型按 constitution 条款批评自己，再改写成更无害的版本。用这些改写做 SL，得到更无害但仍有用的策略。
2. **RL 阶段。** 用模型（可另有一套）按同一套原则比较两条回答，产生偏好，训偏好模型，再 PPO。这就是 RLAIF：反馈来自 AI，原则来自人。

Constitution 是可版本化的规则列表（人权、非歧视、避免过度拒绝、尊重法律等），不是一句「要无害」。条款会冲突：无害 vs 有帮助。面试要能举一条冲突并说怎么打破：通常无害优先，但过度拒绝要单独写条款压回去。Claude 公开 constitution 就是给人审的，不是隐藏 system prompt。

## 和 RLHF 比

| | RLHF (InstructGPT) | CAI |
| --- | --- | --- |
| 偏好来源 | 人标 chosen/rejected | 模型按条款比较 |
| 人的工作 | 持续标注 | 写 / 改条款，抽查失败 case |
| 主要风险 | 标注员偏好、讨好 | 模型自嗨、条款漏洞、过度拒绝 |
| 规模 | 标注吞吐限制 | 原则一旦写好，反馈更便宜 |

CAI 仍然有偏好模型和 RL。换成「完全没有 RM」就答偏了。它解决的是 harmlessness 标注贵、人也不愿反复看有害内容，不是把对齐变成无监督。

Sycophancy、reward hacking 在 RLAIF 里照样在。评委若用「模型自己给自己打分会不会崩溃」，答：批评模型和被训模型要隔离版本，条款要有反例测试，人抽查的是原则失败模式而不是全量偏好。self-rewarding 的隔离见 `pt-self-rewarding-idpo`。

## 追问

- **和 RLHF 能叠吗？** 能。常见是 helpfulness 仍走人类偏好，harmlessness 走 CAI。不要说 CAI 替换了全部 RLHF。
- **constitution 写进 system prompt 算 CAI 吗？** 只是推理期约束。CAI 指用条款生成训练数据。prompt alone 没有新偏好分布。
- **computer use 的确认框算 constitution 吗？** 不算。那是产品层权限，见 `cu-sensitive-action-confirm`。条款约束的是语言 / 决策倾向，不能替代 OS 级确认。
