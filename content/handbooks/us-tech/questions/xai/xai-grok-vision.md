---
id: xai-grok-vision
section: xai
order: 16
level: A
title: xAI：Grok 视觉公开口径能讲什么，不要编编码器？
quick: "我会只引用公开的图像 API 约定：jpg/png、单图约 20MiB、支持多图和图文交错，具体模型以相应文档为准。编码器、patch 和视觉 token 精确数没有公开依据；工程上按视觉输入占用窗口来算预算，并用像素核对答案，处理下载失败和缓存变化。"
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

我会按公开 API 约定解释 Grok 的图像输入，再讨论延迟、证据和失败处理，编码器细节没有依据就不推测。例如用户问图里的数字，答案要能和像素对上，下载失败就要报告错误。模型名从 `grok-vision-beta`、`grok-2-vision-1212` 到后来的聊天视觉模型会变化；Grok-1 开源快照没有视觉塔，Grok-3 博文也没有公布视觉编码器，预训练口径见 `xai-grok-pretrain`。

## 公开输入约定能说明什么

文档层可以讲的：

- 输入：`jpg` / `png`（以当时模型表为准），单图大约 20MiB，张数文档写过「无硬顶」，产品上仍要自己限张数。
- 内容块：文本和图可交错，顺序任意。
- 搜索工具里的 `enable_image_understanding` 是另一条：让 agent 看搜索到的图，不是把预训练变成实时视觉。

不要讲：具体 ViT 尺寸、patch、是否 Q-Former、视觉 token 精确个数、训练图来自哪。那些没有技术报告。面试用通用形状：图被编成 $N_{\mathrm{vis}}$ 个前缀 token，和文本抢同一条上下文和 KV。$N_{\mathrm{vis}}$ 随分辨率涨。多图近线性加。这和 `msft-llava` 同一笔账，只是你不能声称 Grok 用了哪套网格。

延迟：视觉 输入预填充（prefill，即处理输入并建立缓存） 会打 首个 token 的等待时间（TTFT）。产品要限边长、限张数、长截图先裁。评测切开：自然图描述、截图 OCR、图表读数、拒答（图里没有的实体）。Arena 文风分不能当视觉发版，见 `xai-lmarena`。

核对证据时，用户问「图里的数字是多少」，就把答案对回像素，不能靠参数记忆补。搜索来的图更要当不可信输入，见 `xai-search-agent`。

常见误区是：把 Grok-1 314B MoE 说成视觉模型；假设实时 X 图片已经在预训练里（搜索是推理期工具）；为视觉另开绕过鉴权的管理员接口。

## 宿主如何处理输入与失败

即使内部编码器未知，宿主仍要：

- 压缩 / 缩放到上限，失败要结构化错误，不要让模型编「我看见了」。
- 外链图由 xAI 侧拉取时，主机可能拒爬，文档和第三方都遇到过 `image_download_error`。生产偏 base64。
- 视觉 token 进 输入提示（prompt） cache 前缀要稳定，见 `xai-prompt-cache`。图字节一变，缓存整段失效。

因此发版仍按 OCR、图表和拒答切片验收，并由产品限制多图张数。

## 追问

**Grok-2-vision 和后来的 grok-4 聊天视觉是不是同一个塔？**
公开没说。答「以当时模型表为准，合同是图像块，不是架构」。

**视频？**
生成视频和理解视频是不同产品。理解侧以文档为准，不要把 Imagine 视频生成说成视觉 LLM。

**为什么不猜 CLIP-L？**
猜对了也没法验证，猜错减分。把时间用来解释输入预算、如何核对证据和如何处理失败。

**和工具一起用？**
可以。图是输入，搜索是工具。执行域不同，见 `xai-tool-use`。

本卡依据公开材料整理，标记为 `realInterview: false`。
