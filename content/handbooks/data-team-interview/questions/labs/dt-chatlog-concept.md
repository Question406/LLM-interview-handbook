---
id: dt-chatlog-concept
section: labs
order: 42
level: A
title: OpenAI：从聊天日志里挖新概念的代表图，苹果怎么改口？
quick: "用于苹果场景时，我会从评测失败和有许可的图库中找种子。新颖图片应该与已有训练数据不同，同时质量合格；不能把损坏图片当新概念。人工标注优先看质量高、又不同于已有类别的图片。"
companies:
  - apple
tags:
  - OpenAI
  - Active Learning
  - Multimodal
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: OpenAI System Design Interview Questions (AceOffer catalog)
    url: https://aceoffer.app/interviews/openai/system-design-questions
    type: secondary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会从冻结评测里失败的概念、有许可的产品图片和 Applebot 公开页面中找种子。候选池使用许可图库，以及已经验证的合成图片描述。用 embedding 衡量图片与已有训练数据的距离，再结合质量和多样性筛选；人工优先检查差异大、质量也合格的候选。

不这么选的理由：AceOffer 记过 OpenAI 系统设计：从 ChatGPT 聊天日志里抽新出现的真实世界概念的代表图，例子是 Cybertruck。原样搬过来，通道就不成立。用户附件默认不进基础模型。

用于苹果场景时，保留筛选流程，把来源换成许可数据。离群图片可能只是损坏、有水印或不安全，不能只凭少见就判断有价值。先质量门（CLIP 分、分辨率、PII 人脸），再新颖分，再最大边际选 Diversify。AFM 公开写过合成 caption 超 50 亿对、去重后超 100 亿图文对；新概念要进那套 mix，先过许可和污染扫描。和 `dt-novel-bootstrap` 同一骨架，模态换成图。

公开锚点：AceOffer 系统设计目录里有「Image Extraction from Chat Logs for New Concepts」，报到过 2025 年 12 月。

## 追问

- **没有聊天日志，新词从哪来？** 新闻许可源、产品发布页、评测里突然出现的实体。词先入文本侧，图再按 CLIP 去图库召回。
- **人标预算怎么花？** 不确定且远离已有正例的簇，不要随机抽。见 `dt-human-budget`。
- **合成图能当代表图吗？** 能当增强，不能当「真实世界出现过」的证据。门禁用许可实拍。
