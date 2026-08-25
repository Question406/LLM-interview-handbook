---
id: amazon-nova-mm
section: amazon
order: 15
level: A
title: Amazon：Nova 多模态（公开）和 Bedrock 路由怎么接？
quick: >-
  Lite / Pro / Premier 吃图、视频、文档；Micro 是文本。族内智能路由不要把带图请求打到 Micro。评的是文档页、截图 OCR、短视频理解加路由后悔率，不是把
  MMLU 和 Arena 焊一张表。嵌入仍常走 Titan 或 Nova 多模态嵌入，别和聊天模型混发版。
tags:
  - Amazon
  - Nova
  - Multimodal
  - Bedrock
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: What is Amazon Nova
    url: https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html
    type: primary
  - title: Amazon Nova
    url: https://aws.amazon.com/ai/generative-ai/nova/
    type: primary
  - title: Intelligent prompt routing in Amazon Bedrock
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html
    type: primary
  - title: Amazon Nova vision understanding prompting
    url: https://docs.aws.amazon.com/nova/latest/userguide/prompting-video-understanding.html
    type: primary
---

Bedrock 应用岗在 `amazon-nova` 之后会追问「那张图打哪一档」。公开用户指南：Micro 文本；Lite / Pro / Premier 文本 + 图 + 视频，文档类型以当时表为准。Intelligent Prompt Routing 仍在 **同一族** 里预测质量再 fallback。跨模态请求不是「更长的 prompt」，是另一条能力面。不是逐字真题。

## 路由先看模态，再看难度

我会在白板上加一列模态，避免只按字数路由：

- **纯文本短分类 / 抽槽。** Micro 或路由到 Lite。和 `amazon-nova` 里简单 FAQ 走小模型同一句。
- **图、截图、PDF 页、短视频。** 默认 Lite 起。路由器若只能看见文本长度，会把「这张发票多少钱」打到 Micro 然后静默失败。应用层要在调用前看 content block：有 `image` / `video` / `document` 就禁止 Micro。
- **多图对照、长视频、密表。** Pro / Premier。视频公开有采样上限：长片 FPS 会降，高运动细节会丢。面试讲「先抽关键帧或切段，再选档」，不要承诺「随便丢 1 GB 进 Converse」。
- **检索。** 生成用 Nova，嵌入用 Titan Text 或 Nova 多模态嵌入（以当时文档为准）。换 embedding = 全库重编，见 `amazon-titan-embed`、`amazon-bedrock-rag`。

族内路由的质量差阈值对多模态要单独标定。文本上「小模型够用」推不过发票 OCR。后悔率、升级率仍按 `amazon-nova` 那张表报，但要按模态切片。

Token 账：图和视频会变成一大段视觉 token，TTFT 和 E2E 都涨，见 `amazon-p99-stream`。SLO 按「有无媒体」分桶，混在一个 InvocationLatency 里你不知道是 decode 慢还是 4K 图 prefill。

## 评测和护栏

门禁沿用 `amazon-titan-eval` 四层，加视觉切片：

- 文档：字段级准确，金额 / 日期单独计，不要 BLEU。
- 截图 UI：能不能指到正确控件或读对按钮字。
- 视频：时间戳定位 vs 摘要流畅。摘要漂亮但事件错了算失败。
- 安全：公开表里部分 Nova 档的 Guardrails 标注为 text only。图上的违规、截图里的 PII，不能假设输入护栏已经看过像素。要嘛预处理 OCR 再拦，要嘛下游策略，见 `amazon-guardrails`。

错法：用 Arena 文风分给 Nova Lite 视觉发版；智能路由完全交给 Bedrock、应用不检查模态；把 PDF 当纯文本 RAG 又同时整页当图，重复计费还双份幻觉。图 / PDF 检索见 `amazon-mm-rag`。

## 我会怎么收设计题

先钉输入契约（最大边长、页数、视频秒数）和是否必须引用页码。再选默认档，最后加同族路由。知识库、工具、护栏绑应用不绑死 model id，方便 Lite 换 Pro。离线可以全打 Pro 当上限，线上用后悔率证明带图请求没被降到 Micro。护栏和工具绑应用层，换档不换契约。

护栏和工具绑应用层，换档不换契约。离线全打 Pro 当上限，线上用后悔率证明带图请求没落到 Micro。

## 追问

- **为什么不全部 Premier？** 配额和 TTFT。大量「读这张缩略图标签」用 Lite。Highest Standards 指字段对，不是每张图都用最大模型。
- **路由特征和文本一样吗？** 不够。至少要有模态、页数、是否要定位。短问句配一张密表很难。
- **和 Claude / GPT 视觉怎么比？** 跨厂用你的应用集，不要减三家 VQA 总分。Bedrock 智能路由不做跨族。
- **视频超时？** 同步 Converse 要加大 SDK 超时；更长的走切段 + 批处理，见 `amazon-batch-infer`。
