---
id: sec-multimodal-ocr-vs-adversarial-image
section: multimodal
order: 24
level: S
title: "OCR text injection 与 adversarial image 是同一种攻击吗？"
quick: "我会先看恶意信息通过哪条路径进入模型。OCR injection 可能就是正常可读文字被当成指令；adversarial image 则可能依赖像素级优化和特定视觉表示。它们在权限、可见性和 transfer 上差别很大。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "Image Hijacks: Adversarial Images can Control Generative Models at Runtime"
    url: "https://arxiv.org/abs/2309.00236"
    type: primary
  - title: "WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks"
    url: "https://arxiv.org/abs/2504.18575"
    type: primary
---

## 题目描述

截图里可读的一段文字改变了 agent 目标；另一张人眼看不出特殊指令的图像也使 VLM 行为变化。

需要讨论：分别写出 attacker control、模型 access 与 transfer 假设，避免混用成功率。

## 回答思路

> **Situation：** 截图里可读的一段文字改变了 agent 目标；另一张人眼看不出特殊指令的图像也使 VLM 行为变化。  
> **Task：** 分别写出 attacker control、模型 access 与 transfer 假设，避免混用成功率。  
> **Approach / Why：** 把可读内容注入、视觉扰动和 observation extraction 三条路径分开实验。  
> **Result / Check：** 比较 OCR-only、image-only 与融合输入，报告各设置的有效攻击比例。

## 可以这样回答

我会先看恶意信息通过哪条路径进入模型。OCR injection 可能就是正常可读文字被当成指令；adversarial image 则可能依赖像素级优化和特定视觉表示。它们在权限、可见性和 transfer 上差别很大。

我会给同一目标分别提供 OCR 文本、原图和两者融合，检查是文本语义起作用，还是视觉特征本身改变行为。图像压缩、缩放和重新截图也能帮助定位机制。

如果攻击只在一个可访问 gradients 的旧 VLM 上有效，就不该直接说今天所有 computer-use agents 都同样脆弱。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 分别构造可读 benign/attacker text 图像和受控 adversarial perturbations，保留 clean image。
- **Baselines / Ablations：** 比较 OCR extraction、vision encoder、融合 observation，以及压缩/缩放 transforms。
- **Metrics 与判读：** 报告 task-level ASR、perceptual/format constraints、跨模型 transfer 与正常视觉任务准确率。

## 追问与容易误判的地方

做视觉变换时要保持原任务仍可完成；把页面破坏得不可读会降低攻击成功，也会降低一切能力。

## 论文依据与适用范围

- [Image Hijacks: Adversarial Images can Control Generative Models at Runtime](https://arxiv.org/abs/2309.00236) · 2023 · research paper。
- [WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks](https://arxiv.org/abs/2504.18575) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
