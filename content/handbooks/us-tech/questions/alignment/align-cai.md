---
id: align-cai
section: alignment
order: 3
level: S
title: 对齐：Constitutional AI 人从偏好标注挪到原则+抽查
quick: "Constitutional AI 用人写的原则生成批评、改写与 AI 偏好，再做监督学习和 RLAIF。人主要负责写规则、处理冲突和抽查失败模式，仍然参与对齐；原流程也保留偏好模型与 RL，helpfulness 还可继续使用人类偏好。"
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
  - title: Constitutional AI — Harmlessness from AI Feedback (Anthropic)
    url: https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
    type: primary
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
---

Constitutional AI 把人的工作从逐条比较回答，转向制定原则和检查原则失效的地方。模型按 constitution 批评、改写回答，再生成 AI 偏好用于训练，人仍要决定规则和处理冲突。

HH-RLHF 需要标注员反复看有害内容，在 helpful 与 harmless 之间做比较，成本高，也给标注员带来负担。CAI 让人维护一份可版本化的原则，包括人权、非歧视、合法、避免 over-refusal 和不 sycophancy，再抽查模型仍然失败的案例，回头改条款。这是 Anthropic harmlessness 的公开背景，可与 InstructGPT 对照；分层实现见 `anthropic-constitutional-ai`，RLAIF 隔离见 `align-rlaif`。

例如“避免有害内容”与“尽量帮助用户”会冲突，诚实也可能与不提供犯罪细节冲突。通常优先无害，同时明确约束 over-refusal，否则正常医疗、新闻、虚构暴力请求也可能被改成拒答，见 `align-over-refuse`。只写“尊重用户”而不管 sycophancy，又可能鼓励同意用户的错误观点，见 `align-sycophancy`。所以要按失败模式抽查，随机看 100 条聊天不一定能发现这些漏洞。

## 训练如何使用原则

监督阶段先让模型对有害或越界回答按条款批评，再改写，用这些版本做 SL，得到更 harmless、尽量仍 helpful 的策略。RL 阶段再让模型，最好有另一套模型，按原则比较两条回答，生成偏好、训练偏好模型，再 PPO。这就是 RLAIF：人提供原则，AI 提供逐条反馈，原流程仍有 RM 与 RL。

| | RLHF (InstructGPT / HH) | CAI |
| --- | --- | --- |
| 偏好来源 | 人标 chosen/rejected | 模型按条款比较 |
| 人的工作 | 持续标注 | 写 / 改条款，抽查失败 case |
| 主要风险 | 标注员偏好、讨好 | 模型自我强化偏见、条款漏洞、over-refusal |
| 规模 | 标注 throughput 限制 | 原则写好后反馈更便宜 |

Helpfulness 仍常使用人类偏好，harmlessness 使用 CAI，两条目标分开训练、混合 sampling 更方便控制。它主要降低有害内容的人工标注负担，没有替换全部 RLHF，也没有变成无监督学习。

Constitution 是可供人审阅的规则。Claude 后来公开 constitution，可以用来说明原则的可审计性。仅把规则贴进推理期 system prompt，只约束这一轮 sampling，不会生成新的训练数据或偏好分布，不能算 CAI，也无法据此声称预训练里的有害倾向已经改变。

## 追问

**和 RLHF 能一起用吗？**
能。Helpfulness 可由人类偏好提供，harmlessness 由 CAI 提供，保留人抽查。

**人还负责什么？**
写原则、修订冲突条款，检查 over-refusal、sycophancy 和条款被曲解等失败模式。

**为什么 harmless 比 helpful 更适合？**
有害内容的人工标注负担大，也更容易写成可检查的禁区；helpful 更依赖任务成功，人类偏好仍难完全替代。

**写进 system prompt 就够吗？**
不够。CAI 用原则生成监督数据和 AI 偏好，推理提示没有完成这段训练。

## 相关题

- [[anthropic-hh-rlhf]]：helpful 与 harmless 都由人逐条标的流程和两轴冲突。
- [[anthropic-pref-collect]]：人工偏好采集协议。
- [[align-llm-judge]]：AI 裁判的位置、长度、自偏好偏差也会进入 RLAIF。
