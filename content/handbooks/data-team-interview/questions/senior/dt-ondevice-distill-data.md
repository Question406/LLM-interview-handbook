---
id: dt-ondevice-distill-data
section: senior
order: 7
level: A
title: Director：端侧蒸馏该蒸哪些数据，为什么不从头蒸 14T？
quick: "AFM 公开的端侧配方没有从头蒸：先用 1T 高质量数据把 dense 端侧模型 sparse-upcycle 成 MoE 教师，再只在 dense 学生最后约 10% 的 token（约 1.4T）上加蒸馏损失，教师训练成本因此降了约 90%。蒸什么还要看 3B 学生学不学得会、对不对得上产品任务，server 的长 RL 轨迹不宜原样蒸。"
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

不从头蒸，是因为 AFM 的公开配方把蒸馏集中在高质量的那一段：教师只用 1T 高质量数据 upcycle 出来，蒸馏只加在学生最后约 1.4T token 上。选蒸馏数据时我看三件事：质量够不够高，约 3B 的学生学不学得会，是不是端侧的产品任务。

流程是这样的。2025 年先训一个约 14T token 的 dense 端侧模型，再把它 sparse-upcycle 成 64 个 expert、隔层 MoE 的教师，这一步只用 1T 高质量数据。然后用这个教师，在 dense 学生最后 10% 的训练 token，也就是约 1.4T 上加蒸馏损失。教师训练成本降了约 90%，也不需要结构剪枝。server 走的是另一套数据方案，从零训约 13.4T，不走这条路。

数据为什么要挑高质量的？教师 logits 里的错误会被学生学走，所以教师那 1T 必须是高质量数据。学生被蒸的 1.4T 也应该偏向高质量段，dirty crawl 上的 logits 噪声大，3B 的容量又有限。可学性要单独卡一道，比如教师 MoE 的推理过程很长、3B 复现不了，就别蒸整段，见 `dt-teacher-bias`。任务按产品契约挑，蒸摘要、抽取、短工具调用，不蒸开放世界闲聊。

压缩之后还有一步恢复。QAT 到 2-bit 时，他们用同一套训练阶段、更少的步数，再加 LoRA 把能力补回来，恢复用的数据也沿用底座的训练配方。

## 追问

**为什么 2024 年发现 continued 段蒸馏没帮助？**
2024 报告写过端侧 continued 阶段不用蒸馏。现场可以说「core 末段蒸馏，mid 按任务验证数据」，别把蒸馏当成每一段的默认做法。

**logits 存不下怎么办？**
AFM 强调新管道让教师 logits 更容易产出。面试里可以提在线蒸馏、只蒸最后一段，别编存储数字。

**server 的轨迹能蒸给端侧吗？**
不一定。3B 学生未必学得会很长的工具轨迹和 65K 上下文任务，简短、可验证、符合产品功能的任务可以考虑蒸馏。

**蒸馏数据里能混网页粗数据吗？**
尽量别。dirty crawl 上的教师 logits 噪声大，3B 学生容量有限，学到的多半是噪声，所以蒸馏段偏向高质量数据。
