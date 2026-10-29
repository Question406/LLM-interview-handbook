---
id: afm-web-judge-bias
section: alignment
order: 707
level: S
title: LLM-as-a-Judge：怎样发现 position、verbosity 和 self-preference bias？
quick: >-
  用对照 pairs 分离内容、顺序和长度，结合 blind human labels calibration。 判断稳定且与独立正确性相符，保留
  disagreement 和不确定样本。
companies:
  - apple
tags:
  - Apple
  - AFM 网站参考题
  - AFM Web References 2026-10-27
  - alignment
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 'TechAIInterview — Question bank: LLM judge reliability'
    url: 'https://www.techaiinterview.com/questions/'
    type: reference
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---

## 来源与范围

参考 [TechAIInterview — Question bank: LLM judge reliability](https://www.techaiinterview.com/questions/) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
你准备用 LLM-as-a-judge 为训练样本打 preference labels。如何识别和减轻 bias，并验证这些 labels 值得使用？来源题明确讨论 judge reliability 和 bias；训练接入是 AFM 扩展。

## 技术备查
- Position bias：交换顺序，统计 winner consistency；允许 tie 或 abstention，不强制每题二选一。
- Verbosity bias：构造内容质量相当、长度不同的 pairs，也构造相同长度但正确性不同的 pairs。直接截断答案可能破坏内容，不能作为唯一控制。
- Self-preference：隐藏模型身份，跨生成器与 judge family 分析；风格和模型来源可能混杂，不能只看到相关性就下因果结论。
- Rubric drift：judge、prompt 或 rubric 更新后重跑 calibration。报告与 human labels 的一致性，并结合 human–human agreement 解释上限。

## 面试追问
**两个 judge 多数投票够吗？** 不够，它们可能共享同一种 bias；优先增加独立证据和有针对性的对照。

**要求 judge 给 rationale 就可靠吗？** Rationale 有利于审计，但可能是事后解释；仍需盲评和正确性检查。
