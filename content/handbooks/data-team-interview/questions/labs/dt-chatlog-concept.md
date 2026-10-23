---
id: dt-chatlog-concept
section: labs
order: 42
level: A
title: OpenAI：从聊天日志里怎么挖新概念的代表图？
quick: "分两步：先从聊天日志和评测失败里找出新出现的概念，再从有许可的图库和验证过的合成图片描述里给它挑代表图。挑图先过质量门，再看新颖度，最后保证多样性，因为离群的图很多只是损坏或带水印。人工优先看质量合格、又和已有类别差得远的图。"
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

分两步做：先找出新出现的概念，再给每个概念挑代表图。概念的种子来自聊天日志里突然冒出来的实体，以及冻结评测里模型答错的概念；候选图来自有许可的图库和验证过的合成图片描述。挑图时先挡坏图，再看新颖度。

原题给的例子是 Cybertruck。它刚出来那阵，日志里突然有很多人提到它，这就是一个候选的新概念。题目出自 AceOffer 的 OpenAI 系统设计目录，叫「Image Extraction from Chat Logs for New Concepts」，报到过 2025 年 12 月，要求从 ChatGPT 聊天日志里抽取新出现的真实世界概念的代表图。

挑图的顺序要讲究。只凭「少见」判断一张图有价值，会把损坏、有水印或不安全的离群图选进来。所以先过质量门，用 CLIP 分、分辨率、PII 人脸把坏图挡掉；再用 embedding 算图片和已有训练数据的距离，当作新颖分；最后用最大边际的方式做 Diversify，免得选出一堆差不多的图。人工优先看差异大、质量也合格的候选。整体骨架和 `dt-novel-bootstrap` 一样，只是模态换成了图。

新概念的图要进图文训练混合，之前还要过许可和污染扫描。作为参照，AFM 报告公开的图文混合里，合成 caption 超过 50 亿对，去重后的图文对超过 100 亿。

## 追问

**日志里的用户原话和附件能直接用吗？**
要先按数据政策确认能用到什么程度，这些内容涉及隐私。

**没有聊天日志，新词从哪来？**
新闻许可源、产品发布页、评测里突然出现的实体。词先进文本侧，再按 CLIP 去图库召回图片。

**人标预算怎么花？**
优先标不确定、又远离已有正例的簇，比随机抽省预算，见 `dt-human-budget`。

**合成图能当代表图吗？**
可以当增强，当不了「真实世界出现过」的证据。门禁用许可的实拍图。
