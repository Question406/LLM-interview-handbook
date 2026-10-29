---
id: dt-ondevice-distill-data
section: senior
order: 7
level: A
title: Director：on-device distillation 该蒸哪些数据，为什么不从头蒸 14T？
quick: >-
  AFM 公开的 on-device 配方没有从头蒸：先用 1T 高质量数据把 dense on-device 模型 sparse-upcycle 成 MoE
  teacher，再只在 dense student 最后约 10% 的 token（约 1.4T）上加 distillation 损失，teacher
  训练成本因此降了约 90%。蒸什么还要看 3B student 学不学得会、对不对得上产品任务，server 的长 RL trajectories
  不宜原样蒸。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

不从头蒸，是因为 AFM 的公开配方把 distillation 集中在高质量的那一段：teacher 只用 1T 高质量数据 upcycle 出来，distillation 只加在 student 最后约 1.4T token 上。选 distillation 数据时我看三件事：质量够不够高，约 3B 的 student 学不学得会，是不是 on-device 的产品任务。

流程是这样的。2025 年先训一个约 14T token 的 dense on-device 模型，再把它 sparse-upcycle 成 64 个 expert、隔层 MoE 的 teacher，这一步只用 1T 高质量数据。然后用这个 teacher，在 dense student 最后 10% 的训练 token，也就是约 1.4T 上加 distillation 损失。teacher 训练成本降了约 90%，也不需要结构剪枝。server 走的是另一套数据方案，从零训约 13.4T，不走这条路。

数据为什么要挑高质量的？teacher logits 里的错误会被 student 学走，所以 teacher 那 1T 必须是高质量数据。student 被蒸的 1.4T 也应该偏向高质量段，dirty crawl 上的 logits 噪声大，3B 的容量又有限。learnability 要单独卡一道，比如 teacher MoE 的推理过程很长、3B 复现不了，就别蒸整段，见 `dt-teacher-bias`。任务按产品契约挑，蒸摘要、抽取、短 tool calls，不蒸开放世界闲聊。

压缩之后还有一步恢复。QAT 到 2-bit 时，他们用同一套训练阶段、更少的步数，再加 LoRA 把能力补回来，恢复用的数据也沿用 base model 的 training recipe。

## 追问

**为什么 2024 年发现 continued 段 distillation 没帮助？**
2024 报告写过 on-device continued 阶段不用 distillation。现场可以说「core 末段 distillation，mid 按任务验证数据」，别把 distillation 当成每一段的默认做法。

**logits 存不下怎么办？**
AFM 强调新管道让 teacher logits 更容易产出。面试里可以提在线 distillation、只蒸最后一段，别编存储数字。

**server 的 trajectories 能蒸给 on-device 吗？**
不一定。3B student 未必学得会很长的 tool-use trajectories 和 65K 上下文任务，简短、可验证、符合产品功能的任务可以考虑 distillation。

**distillation 数据里能混网页粗数据吗？**
尽量别。dirty crawl 上的 teacher logits 噪声大，3B student 容量有限，学到的多半是噪声，所以 distillation 段偏向高质量数据。
