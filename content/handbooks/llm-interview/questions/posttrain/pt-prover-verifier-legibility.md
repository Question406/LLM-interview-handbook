---
id: pt-prover-verifier-legibility
section: posttrain
order: 36
level: S
title: 强 Prover 怎样在不牺牲正确性的前提下，生成弱 Verifier 也能检查的推理？
quick: 把“正确”与“可检查、可说服”分开优化。先用可信 correctness gate 排除错解，再训练 prover 产生 verifier 能检查的证据；不能直接以说服弱 judge 的分数为 reward，否则会激励伪装而非真正确。
tags:
  - Verifier
  - Legibility
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OpenAI — Prover-Verifier Games Improve Legibility
    url: https://openai.com/index/prover-verifier-games-improve-legibility/
    type: primary
---

prover 比 verifier 强时，单看最终答案会丢掉过程信息，单让 prover 追求“让 verifier 相信”又会出现 sneaky proof。安全的训练顺序是先验证答案/证明是否正确，再在正确集合内优化简洁、引用充分、步骤可检查等 legibility 指标。

verifier 需要有明确能力边界：它检查哪些局部事实、能否调用工具、是否看完整过程。训练时可让 prover 与多个 verifier 对抗或合作，避免只适配一个 judge 的语言习惯。

评估包含 correctness、verifier acceptance、人工可审计性和 adversarial persuasion gap。若 acceptance 上升而 correctness 下降，说明 reward 已被“说服技巧”劫持。
