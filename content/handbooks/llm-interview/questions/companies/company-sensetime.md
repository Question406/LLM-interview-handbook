---
id: company-sensetime
section: companies
order: 18
level: A
title: 商汤多模态：25/26 实习/校招准备什么？
quick: "商汤多模态的主战场是项目能不能验证：多模态数据清洗和准确性、OCR/文档理解、可验证的反思纠错、GRPO 奖励、Agent 模块划分和 benchmark。手撕常是链表这类中等数据结构题。"
tags:
  - SenseTime
  - Multimodal
  - 真题导航
  - 2025-2026
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
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

商汤多模态面试，光说「调了 VL API」过不了。我会把整个流程讲具体：数据从哪来，怎么防 OCR 过拟合，反思步骤怎么自动打分，上线难在哪。

应用岗二面还会给开放设计题，比如家庭安防，并让你对比固定的「感知-推理-校验」和动态多 Agent。手撕多是链表中等题，重点仍是项目结果能不能验证。GRPO 准备一张奖励卡就够了，用不着把整章 post-training 背完。

## 准备主线

1. 数据和 OCR 看来源、清洗和准确性（`sensetime-data-clean`），OCR 过拟合的表现和可验证纠错（`sensetime-ocr-overfit`），思维链（CoT，即分步推理过程）是不是过度设计（`sensetime-cot-overdesign`）。
2. 奖励和 Agent 看 OCR / 反思场景的 GRPO 奖励（`sensetime-grpo-ocr-reward`），三个模块谁最重要、什么时候不训练（`sensetime-agent-three-modules`），以及感知-校验和动态多 Agent 的对比（`sensetime-perceive-vs-dynamic`）。
3. 系统和产品看视频场景的路由和全挂兜底（`sensetime-model-route-fallback`）、家庭安防渐进响应（`sensetime-home-security`）、多轮（`sensetime-multiturn`）、LoRA 挂哪（`sensetime-lora-where`）、刷了哪些 benchmark（`sensetime-benchmarks`）。
4. 手撕见 `sensetime-linked-list-reverse`。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `sensetime-data-clean` / `sensetime-ocr-overfit` / `sensetime-cot-overdesign`
- `sensetime-grpo-ocr-reward` / `sensetime-agent-three-modules` / `sensetime-perceive-vs-dynamic`
- `sensetime-model-route-fallback` / `sensetime-home-security` / `sensetime-multiturn`
- `sensetime-lora-where` / `sensetime-benchmarks` / `sensetime-linked-list-reverse`

## 追问

**OCR 过拟合长什么样？**
训练用的字体、版式上很准，换成扫描件准确率就明显下降。要做跨源 holdout 和扰动测试，再堆同分布的图没用。

**反思步骤怎么自动打分？**
用可执行的核对，比如字段、校验和、二次 OCR，别只让模型自评。

**为什么有时候不训练？**
模块边界清楚、规则或检索已经够用时，训练会带来没法审计的漂移。按 id 讲实验。
