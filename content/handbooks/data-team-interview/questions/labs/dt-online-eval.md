---
id: dt-online-eval
section: labs
order: 56
level: A
title: Perplexity：线上评测记什么、抽什么、怎么 A/B？苹果怎么改口？
quick: "线上评测用于发现失败类型、验证产品收益和成本；不能默认把用户原文回传训练。记录版本、延迟和合法工具行为，按失败类型分层抽查。A/B 尽量只换权重，正确率、安全与延迟分开报告；训练信号通过许可研究集复现或验证合成获得。"
companies:
  - apple
tags:
  - Perplexity
  - Evaluation
  - Privacy
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

线上记录先选必要的元数据：请求 id、模型哈希、提示模板版本、延迟、工具调用是否合法、是否触发拒答。内容能不落盘就不落盘。抽查按失败类型分层，不能只抽点赞请求。

A/B 固定提示模板和解码参数，尽量只更换权重，分别观察正确率、安全和延迟。线上评测的目的是判断产品表现，不是使用 Arena 分数代替护栏。

Perplexity / Cohere 公开题型会问线上评测与发布检查。有些方案默认把生产日志用于下一轮 SFT，但苹果场景中不能默认这条通道成立。线上帮助发现缺口，训练样本通过研究集复现或验证合成获得，见 `dt-data-flywheel`、`dt-privacy-feedback`。

## 产品指标与训练来源分开

opt-in「帮助改进」默认关闭。即使开放了对应通道，也应先按约定汇总失败类型，不能把用户搜索词直接加入预训练。检索产品可以自动检查答案是否得到检索块支持，再按这个错误类型统计。

延迟与正确率分开报。搜索结果正确但慢了 2 秒，产品整体体验仍可能变差。

公开来源包括 Apple Intelligence 训练数据页、Applebot 隐私页；题型参考 Perplexity / Cohere 公开面试指南。

## 追问

- 改写、重试、复制等隐式反馈能当偏好吗？可以在端侧按允许用途服务 adapter；回传原文用于 DPO 不能默认允许，见 `dt-userlog-contrast`。
- 没点击数据怎么办？用自动切片和定期 user study，不要对空日志假设能训练满意度模型。
- A/B 样本太少怎么办？先在固定研究集做配对检验，线上验证方向。小流量上的少量涨分可能只是噪声。
