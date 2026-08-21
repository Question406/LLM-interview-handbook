---
id: company-sensetime
section: companies
order: 18
level: A
title: 商汤多模态：25/26 实习/校招准备什么？
quick: >-
  多模态数据清洗与准确性、OCR/文档理解、可验证反思纠错、GRPO 奖励、Agent
  模块划分与 benchmark。手撕常为链表等中等数据结构，但主战场是项目可验证性。
tags:
  - SenseTime
  - Multimodal
  - 真题导航
  - 2025-2026
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 商汤 多模态大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/bc02d116feb54a46a8b85a46f620f9e6
    type: candidate-first-hand
  - title: 商汤大模型算法应用实习面经（已offer）
    url: https://www.nowcoder.com/feed/main/detail/2762070c2c52472da06bf9ee59518d79
    type: candidate-first-hand
  - title: 商汤大模型算法实习二面（已oc）
    url: https://www.nowcoder.com/feed/main/detail/363fb9aab5dc4507a5bfca6efb049fbf
    type: candidate-first-hand
---

商汤多模态的陷阱是把项目讲成「调了 VL API」。面试要一条能证明**不是只调 API** 的链路：数据从哪来、如何防 OCR 过拟合、反思步骤如何自动打分、上线困难是什么。应用岗二面还会开放设计家庭安防，并对比固定「感知-推理-校验」与动态多 Agent。手撕多为链表中等题，主战场仍是可验证性；GRPO 只保留一张奖励卡即可，不要把整章 post-training 背完。

## 准备主线

1. **数据与 OCR**：来源、清洗、准确性（`sensetime-data-clean`）；OCR 过拟合表现与可验证纠错（`sensetime-ocr-overfit`）；CoT 是否过度设计（`sensetime-cot-overdesign`）。
2. **奖励与 Agent**：OCR / 反思场景的 GRPO 奖励（`sensetime-grpo-ocr-reward`）；三个模块谁最重要、何时不训练（`sensetime-agent-three-modules`）；感知-校验 vs 动态多 Agent（`sensetime-perceive-vs-dynamic`）。
3. **系统与产品**：视频场景路由与全挂兜底（`sensetime-model-route-fallback`）；家庭安防渐进响应（`sensetime-home-security`）；多轮（`sensetime-multiturn`）；LoRA 挂哪（`sensetime-lora-where`）；刷了哪些 benchmark（`sensetime-benchmarks`）。
4. **手撕**：`sensetime-linked-list-reverse`。

## 本手册真题卡

点击下面每条即可跳到对应题。

- `sensetime-data-clean` / `sensetime-ocr-overfit` / `sensetime-cot-overdesign`
- `sensetime-grpo-ocr-reward` / `sensetime-agent-three-modules` / `sensetime-perceive-vs-dynamic`
- `sensetime-model-route-fallback` / `sensetime-home-security` / `sensetime-multiturn`
- `sensetime-lora-where` / `sensetime-benchmarks` / `sensetime-linked-list-reverse`

## 追问

- **OCR 过拟合长什么样？** 训练字体 / 版式准、换扫描件就崩；要跨源 holdout 和扰动，而不是再堆同分布图。
- **反思步骤怎么自动打分？** 用可执行核对（字段、校验和、二次 OCR），不要只让模型自评。
- **为什么有时不用训练？** 模块边界清楚、规则 / 检索已够时，训练引入不可审计漂移。按 id 讲实验，不背「多模态很重要」。
