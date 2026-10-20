---
id: dt-ondevice-distill-data
section: senior
order: 7
level: A
title: Director：端侧蒸馏该蒸哪些数据，为什么不从头蒸 14T？
quick: "AFM 的公开端侧配方先用高质量数据训练 sparse-upcycle MoE 教师，再在 dense 学生最后约 10% 的 token（约 1.4T）上蒸馏，将教师训练成本降低约 90%。数据还要符合学生容量和产品任务，不能把 server 的长 RL 轨迹原样交给 3B 学生。"
companies:
  - apple
tags:
  - Apple
  - Distillation
  - On-device
  - Pre-training
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

按公开配方说明每个阶段使用的数据。端侧约 3B 与 server 使用不同的数据方案；蒸馏集中在高质量训练阶段。教师的推理过程很长、学生无法学会时，不要直接蒸馏整段。

不能只说端侧再抓一批网页，也不能原样蒸馏 server 的长 RL 轨迹，3B 学生未必能学会。教师训练的 1T 数据也必须可靠，否则 logits 中的错误会被学生学到。

## 公开配方里数据在哪

2025：先训 dense 端侧约 14T，再 sparse-upcycle 成 64 expert、隔层 MoE，只用 1T 高质数据。然后用这个教师，对 dense 学生最后 10% 的训练 token（约 1.4T）加蒸馏损失。教师训练成本降约 90%，也不用结构剪枝。Server 从零训约 13.4T，不走这条。

数据上我会守这几条。教师那 1T 必须是高质，垃圾教师 logits 会写进学生。学生被蒸的 1.4T 也该偏高质段：dirty crawl 的 logits 噪声大，3B 容量有限。可学性也卡一道：教师 MoE 的很长的推理过程，3B 复现不了就不要蒸整段，见 `dt-teacher-bias`。产品契约：蒸摘要 / 抽取 / 短工具，不要蒸开放世界闲聊。

QAT 到 2-bit 时他们用同一套训练阶段、更少步数，并加 LoRA 恢复。压缩后恢复能力的数据，也要与底座训练配方一致，不能另换成闲聊数据。

## 追问

- **为什么 continued 段他们发现蒸馏没帮助（2024）？** 2024 写过 on-device continued 不用蒸馏。现场说「core 末段蒸、mid 按任务验证数据」，不要把蒸馏当成每一段的默认。
- **logits 存不下怎么办？** AFM 强调新管道让教师 logits 更好出。面试提在线蒸、只蒸最后一段，不编存储数字。
- **server 轨迹蒸给端侧？** 3B 学生未必能学会很长的工具轨迹和 65K 上下文任务。简短、可验证且符合产品功能的任务，可以考虑蒸馏。
