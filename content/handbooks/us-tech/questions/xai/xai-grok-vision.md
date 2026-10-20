---
id: xai-grok-vision
section: xai
order: 16
level: A
title: xAI：Grok 视觉公开口径能讲什么，不要编编码器？
quick: "能明确固定下来的是 API 合同：jpg / png、单图大约 20MiB、多图、文本和图顺序任意。历史上有 grok-2-vision，后来聊天模型也吃图。不要编 CLIP 变体、token 数或 Tesla 摄像头数据。工程上仍按视觉前缀占上下文来谈延迟和有实际证据支持。"
tags:
  - xAI
  - Grok
  - Vision
  - Public Claims
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: xAI models
    url: https://docs.x.ai/developers/models
    type: primary
  - title: xAI release notes (grok-2-vision-1212)
    url: https://docs.x.ai/developers/release-notes
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: Open Release of Grok-1
    url: https://x.ai/news/grok-os
    type: primary
---

## 题怎么来的

xAI 多模态 / 应用岗会问 Grok 怎么看图。评委要听你分得清公开合同和猜测。能核对的是文档：支持的图像类型、大小上限、模型名随时间变（早期 `grok-vision-beta` / `grok-2-vision-1212`，后续聊天模型也标视觉）。Grok-1 开源快照没有视觉塔可讲。Grok-3 博文讲推理 agent 和搜索，没有公布视觉编码器。本题不写 Tesla 数据引擎。`realInterview: false`。预训练口径见 `xai-grok-pretrain`。

## 公开合同，不编架构

文档层可以讲的：

- 输入：`jpg` / `png`（以当时模型表为准），单图大约 20MiB，张数文档写过「无硬顶」，产品上仍要自己限张数。
- 内容块：文本和图可交错，顺序任意。
- 搜索工具里的 `enable_image_understanding` 是另一条：让 agent 看搜索到的图，不是把预训练变成实时视觉。

不要讲：具体 ViT 尺寸、patch、是否 Q-Former、视觉 token 精确个数、训练图来自哪。那些没有技术报告。面试用通用形状：图被编成 $N_{\mathrm{vis}}$ 个前缀 token，和文本抢同一条上下文和 KV。$N_{\mathrm{vis}}$ 随分辨率涨。多图近线性加。这和 `msft-llava` 同一笔账，只是你不能声称 Grok 用了哪套网格。

延迟：视觉 输入预填充（prefill，即处理输入并建立缓存） 会打 首个 token 的等待时间（TTFT）。产品要限边长、限张数、长截图先裁。评测切开：自然图描述、截图 OCR、图表读数、拒答（图里没有的实体）。Arena 文风分不能当视觉发版，见 `xai-lmarena`。

有实际证据支持：用户问「图里的数字是多少」，答案要对回像素，不能靠参数记忆补。搜索来的图更要当不可信输入，见 `xai-search-agent`。

常见误区是：把 Grok-1 314B MoE 说成视觉模型；假设实时 X 图片已经在预训练里（搜索是推理期工具）；为视觉另开绕过鉴权的管理员接口。

## 工程约束仍要能写

即使内部编码器未知，宿主仍要：

- 压缩 / 缩放到上限，失败要结构化错误，不要让模型编「我看见了」。
- 外链图由 xAI 侧拉取时，主机可能拒爬，文档和第三方都遇到过 `image_download_error`。生产偏 base64。
- 视觉 token 进 输入提示（prompt） cache 前缀要稳定，见 `xai-prompt-cache`。图字节一变，缓存整段失效。

发版仍看 OCR / 图表 / 拒答切片，不要用 Arena 文风分替代视觉合同。多图要自己限张数，文档「无硬顶」不是产品无限。失败模式比产品名词更值得展开。

## 追问

- **Grok-2-vision 和后来的 grok-4 聊天视觉是不是同一个塔？** 公开没说。答「以当时模型表为准，合同是图像块，不是架构」。
- **视频？** 生成视频和理解视频是不同产品。理解侧以文档为准，不要把 Imagine 视频生成说成视觉 LLM。
- **为什么不猜 CLIP-L？** 猜对了也没法验证，猜错减分。把时间花在预算、有实际证据支持、失败模式。
- **和工具一起用？** 可以。图是输入，搜索是工具。执行域不同，见 `xai-tool-use`。
