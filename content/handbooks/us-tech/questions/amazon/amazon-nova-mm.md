---
id: amazon-nova-mm
section: amazon
order: 15
level: A
title: Amazon：Nova 多模态（公开）和 Bedrock 路由怎么接？
quick: "先按模态选模型，再判断任务难度：Micro 接文本，Lite / Pro / Premier 接图像、视频和文档。带图请求在应用层排除 Micro，并按文档字段、截图定位和视频理解分别评测路由后悔率。嵌入与聊天模型各自管理版本。"
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

带图请求先排除 Micro，再在支持该模态的 Nova 档位里按难度路由。比如「这张发票多少钱」只有几个字，但需要视觉能力，按文本长度把它送到 Micro 就会失败。公开指南列出 Micro 处理文本，Lite / Pro / Premier 支持文本、图、视频，具体文档类型仍要核对用户指南。

## 先确定输入能力，再优化档位

应用在调用前检查 content block，有 `image` / `video` / `document` 就禁止 Micro。纯文本短分类和抽槽可用 Micro 或 Lite；图、截图、PDF 页和短视频从 Lite 起。多图对照、长视频和密表再考虑 Pro / Premier。视频有采样上限，长片 FPS 下降会丢高运动细节，可以先抽关键帧或切段，不能承诺 1 GB 内容直接进 Converse。

Bedrock Intelligent Prompt Routing 在同族中预测质量再 fallback。多模态的质量差阈值要单独标定，文本上小模型够用，并不说明发票 OCR 也够用。按模态分别报 `amazon-nova` 中的后悔率和升级率。跨厂比较 Claude / GPT 时要用同一应用集，Bedrock 的智能路由不负责跨族路由。

生成可以用 Nova，嵌入则用 Titan Text 或 Nova 多模态嵌入，以文档支持范围为准。更换 embedding 要重嵌全库，生命周期与聊天模型分开管理，见 `amazon-titan-embed`、`amazon-bedrock-rag`。

图和视频会转成大量视觉 token，同时增加 TTFT 和 E2E。SLO 按有无媒体分组，才能分清是 4K 图像 prefill 慢还是 decode 慢，见 `amazon-p99-stream`。

## 验收看实际视觉任务

沿用 `amazon-titan-eval` 的门禁，再加视觉切片：文档看字段准确率，金额和日期单独计；截图 UI 看是否读对按钮、指到正确控件；视频看时间戳定位与事件正确性。MMLU、Arena 或 VQA 总分只能提供背景，不能替代这些应用验收。

安全也要核对模态覆盖。公开表中部分 Nova 档的 Guardrails 标为 text only，因此不能假设图上的违规内容和截图 PII 已被输入侧看过。可以 OCR 后检查文字，或增加下游策略，见 `amazon-guardrails`。PDF 同时当纯文本 RAG 又整页当图，会重复计费并增加出错机会；图文检索分工见 `amazon-mm-rag`。

落设计时，先定最大边长、页数、视频秒数和页码引用要求，选默认档位，再增加同族路由。知识库、工具和护栏由应用管理，便于 Lite 换 Pro。离线全打 Pro 可作质量上限，线上用后悔率验证带图请求没有被错误降档。

## 追问

**为什么不全用 Premier？**
配额和 TTFT 都有限。读缩略图标签这类任务可先用 Lite，验收仍以字段正确为准。

**路由特征需要加什么？**
至少加模态、页数和是否需要定位。短问句配密表也可能很难，字数不足以判断。

**视频超时怎么办？**
同步 Converse 增加 SDK 超时，更长内容切段加批处理，见 `amazon-batch-infer`。
