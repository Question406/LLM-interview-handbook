---
id: align-cai
section: alignment
order: 3
level: S
title: 对齐：Constitutional AI 人从偏好标注挪到原则+抽查
quick: >-
  RLHF 的偏好来自人逐条标 chosen/rejected。CAI 用书面 constitution 让模型批评 / 改写，再对 AI 反馈做
  RL（RLAIF）。人改成写原则、改条款、抽查失败模式。不取消人，也不等于没有奖励模型。
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

Anthropic 研究 / 对齐岗把这篇当 harmlessness 背景，不一定照读提问。和 InstructGPT 对照最清楚：人都在环里，但人做的事从「每条偏好」变成「原则 + 抽查」。HH-RLHF 已经写过 helpful 和 harmless 会打架；CAI 是他们把 harmless 标注从人手里挪走的一条工程路径。分层实现见 `anthropic-constitutional-ai`。RLAIF 的隔离和反例见 `align-rlaif`。

## 人挪到哪去了

HH-RLHF 要标注员反复看有害内容、在 helpful vs harmless 上做两两比较，贵、慢、对标注员也不好。CAI 把这份劳动换成：

1. 写一份可版本化的 constitution（人权、非歧视、合法、避免过度拒绝、不谄媚等）。
2. 抽查模型按条款改写 / 比较之后仍然失败的 case，回头改条款，而不是加一百万条偏好。

人没有退出。人从高吞吐标注员变成原则作者和红队抽查。面试说「CAI 没人了」直接偏题。条款会冲突：无害 vs 有帮助、诚实 vs 不提供犯罪细节。要能举一条冲突并说打破规则：通常无害优先，但过度拒绝必须单独写条款压回去，否则模型学会凡是沾边就拒，见 `align-over-refuse`。

Constitution 是给人审的规则列表，不是藏起来的 system prompt。Claude 后来公开 constitution，面试可以当「原则要可审计」的例子，不必背条款全文。

## 两段训练，别合成一句「自己训自己」

论文流程：

1. **监督阶段。** 对有害或越界回答，模型按条款批评自己，再改写成更无害的版本。用改写做 SL，得到更 harmless、尽量还 helpful 的策略。
2. **RL 阶段。** 用模型（最好另有一套）按同一套原则比较两条回答，产生偏好，训偏好模型，再 PPO。这就是 RLAIF：反馈来自 AI，原则来自人。

仍然有偏好模型和 RL。答成「完全没有 RM」就偏了。它解决的是 harmlessness 标注贵、人不愿反复看有害内容，不是把对齐变成无监督。

和 InstructGPT 对照：

| | RLHF (InstructGPT / HH) | CAI |
| --- | --- | --- |
| 偏好来源 | 人标 chosen/rejected | 模型按条款比较 |
| 人的工作 | 持续标注 | 写 / 改条款，抽查失败 case |
| 主要风险 | 标注员偏好、讨好 | 模型自嗨、条款漏洞、过度拒绝 |
| 规模 | 标注吞吐限制 | 原则写好后反馈更便宜 |

Helpfulness 仍常走人偏好，harmlessness 走 CAI。不要说 CAI 替换了全部 RLHF。两条目标分开训、再混合采样，比塞进一个标量更可控。

## 现场怎么讲失败模式

条款写「要无害」但没有「不要拒答合法请求」，SL 改写会把正常医疗、新闻、虚构暴力场景全部改成拒绝。条款写「尊重用户」但没有反谄媚，RL 阶段会把同意用户错误观点当 helpful，见 `align-sycophancy`。所以抽查集必须按失败模式切片，不是随机抽 100 条聊天。

把 constitution 贴进推理期 system prompt **不算** CAI。那只是推理约束，没有新的训练分布。CAI 指用条款生成监督数据和 AI 偏好。单靠 prompt 改不了预训练里的有害峰，只改你这轮采样到的表面。

## 追问

- **和 RLHF 能叠吗？** 能。常见是 helpfulness 人类偏好，harmlessness 走 CAI。不要说 CAI 替换了全部 RLHF。
- **constitution 写进 system prompt 算 CAI 吗？** 不算。CAI 是用条款造训练数据。prompt 没有新偏好分布。
- **人还干什么？** 写条款、改冲突条款、抽查原则失败（过度拒绝、谄媚、条款被模型曲解），不是全量偏好。
- **为什么 harmless 比 helpful 更适合 CAI？** 有害内容对人标注不友好，原则更容易写成可检查的禁区；helpful 更依赖任务成功，人偏好仍难替代。
