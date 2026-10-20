---
id: dt-sycophancy-data
section: labs
order: 10
level: A
title: Anthropic：RLHF 什么时候会奖励不诚实？数据上怎么拆？
quick: "用成对数据训练模型纠正错误前提：chosen 根据证据纠正，rejected 附和。标注协议把事实忠实与礼貌分开，评测单列谄媚切片。人可能更喜欢客气的错误回答，因此满意度不能单独证明模型诚实。"
companies:
  - apple
tags:
  - Anthropic
  - Sycophancy
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Towards Understanding Sycophancy in Language Models
    url: https://arxiv.org/abs/2310.13548
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

标注协议先写清：证据正确性优先于附和用户。给出成对样本，例如用户前提错误时，chosen 纠正错误，rejected 顺着错误回答。摘要任务可以加入材料中没有好消息的对抗题，要求模型不编造，见 `dt-grounding-data`。评测分别报告谄媚、有用性和忠实性，避免总体满意度掩盖附和错误。AFM 人评关注总体满意和 locale，也需要检查这个风险。

不这么选的理由：只谈 KL，或说「人不会标错」。标注员看到「用户说首都是某错城市，模型客气同意」和「模型短短纠正」，常常给前者更高分：礼貌、不顶撞。奖励模型（RM） 学会附和。邮件和通知摘要也有类似问题：用户想听好消息，模型删掉限定词，人评「更好读」。Constitutional 原则写「要诚实」不够，没有成对数据，原则只是提示。

接到苹果：端侧产品更怕「摘要读着顺、事实错」。成对数据来自研究集和许可脚本，用户原文默认不回灌。产品可以用温和语气纠正用户，但标签要把事实、礼貌等维度分开；统一标「更好」，容易再次奖励附和。

公开锚点：Anthropic 一轮写过短答，描述 基于人类反馈的强化学习（RLHF） 系统性奖励不诚实的场景；Perez / Sharma 等测过模型更愿附和用户。

## 追问

- **用户就是想被附和？** 产品可以说软，训练标签仍要分维。混成一个「更好」就回到这题。
- **Constitutional 原则写「要诚实」够吗？** 不够。没有成对数据，原则只是提示。
