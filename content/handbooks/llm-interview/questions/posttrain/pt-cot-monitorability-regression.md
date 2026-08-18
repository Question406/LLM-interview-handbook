---
id: pt-cot-monitorability-regression
section: posttrain
order: 40
level: S
title: 强化 Reasoning 后，如何判断 CoT 仍然可被监督，而不是更难审计？
quick: 将 monitorability 当作 post-training regression gate：比较只看答案/动作与能看 CoT 的监控器在关键风险任务上的检出差，固定监控预算并做对抗集。准确率上升不能自动推出可监督性也更好。
tags:
  - Chain of Thought
  - Monitoring
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OpenAI — Evaluating Chain-of-Thought Monitorability
    url: https://openai.com/index/evaluating-chain-of-thought-monitorability/
    type: primary
---

可监控性要有具体任务：例如发现 reward hacking、工具滥用、隐藏目标或不安全计划。分别训练/运行只看最终答案的 monitor 与可看 CoT 的 monitor，在相同 token、时间和人工复核预算下比较 risk detection。

评测集必须有普通失败和刻意伪装失败，且模型不能知道具体监控规则。还要测 CoT 是否越来越简略、编码化、与最终 action 脱钩，避免只凭“看起来有解释”判断透明度。

若 post-training 后主任务质量上升而 CoT 对 monitor 的边际信息下降，应作为发布门槛而非事后解释；必要时重做数据、reward 或工具权限设计。
