---
id: anthropic-vision
section: anthropic
order: 26
level: A
title: Anthropic：Claude vision 图怎么编码、多图怎么喂，截图 agent 卡在哪？
quick: >-
  图按 28 像素一块切成视觉 token，数量跟分辨率走，不跟「一张图」走。超长边会先缩小；computer use 的
  tool_result 截图例外，超限直接拒，要你自己缩。多图当有序块，先标 Image 1。截图 agent 的坐标必须对上缩小后的图。
tags:
  - Anthropic
  - Vision
  - Computer use
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Vision (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/vision
    type: primary
  - title: Computer use tool (Claude Docs)
    url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
    type: primary
---

研究 / serving 岗会问 Claude 到底怎么「看图」，不是让你背「我们是多模态的」。公开文档把图当成 content block：base64、URL 或 Files API 的 `file_id`。题来自产品和 computer use，不是某一场隐藏面经。我会把编码、多图、截图 agent 三件事拆开讲。

## 视觉 token：按块计，不按张计

Claude 看的是 patch，不是原图像素。一块 $28\times 28$，视觉 token 数大约

$$T_{\mathrm{vis}}=\lceil W/28\rceil \times \lceil H/28\rceil$$

账单记在输入 token 里，格式（JPEG / PNG / GIF / WebP）几乎不影响 $T_{\mathrm{vis}}$。官方有两档原生上限：多数模型长边约 1568 px、视觉 token 约 1568；更高分辨率档长边约 2576 px、视觉 token 约 4784。超限的普通图会**按比例缩小**再编码，长边预算被封顶。口算用公式，对账用 `count_tokens`，不要拿文件字节数当 token。

例外：交给 computer use / browser use 的 `tool_result` 截图，API **拒绝缩小**，超限直接校验错误。宿主必须自己缩，并且把点击坐标从「模型看见的图」映射回真屏。坐标工作流必须禁止静默缩小，否则模型和你各看一张尺寸。

Shape 口头报：文本 $[B, T_{\mathrm{txt}}, D]$，视觉 $[B, T_{\mathrm{vis}}, D]$，在序列维拼成 $[B, T_{\mathrm{txt}}+T_{\mathrm{vis}}, D]$。一张高清 UI 截图可以吃掉一篇短文的窗口。多图线性加。不要说「一张图等于 1 个视觉 token」。

## 多图：有序列、有标签、有条数墙

单条 user 消息里可以放多块 `image`。模型按块顺序联合看，适合对比、翻页、前后截图。官方建议每张前面加短文本 `Image 1:`、`Image 2:`，后轮才能用名字指回去。不要把十张图糊成一块 base64。

条数墙（会变，面试报数量级并说查文档）：claude.ai 一条约 20 张；API 在 200k 窗口上大约 100 张/请求，更长窗口可以到几百。整请求还有字节上限。超过约 20 张 `image`（含历史回放、嵌在 `tool_result` 里的截图；Bedrock / GCP 上 PDF 页图也计入）时，每张还有更严的边长限制，文档建议任一边不超过约 2000 px，否则 many-image 校验失败。多页 PDF 不要靠自己拆成一百张图硬塞，走 `anthropic-pdf` 的 document 块。

多轮别反复打 base64：历史越长，payload 和 TTFT 一起涨。Files API 上传一次，后面只传 `file_id`。静态系统提示仍可打 `anthropic-prompt-cache`；图字节本身每次变就 miss，不要指望「同一张截图换了 JPEG 质量还能命中」。文档还写：Claude **不读 EXIF / 元数据**，朝向、拍摄时间要你自己转正后再送。URL 源适合 CDN；内网图不要把带签名的 URL 写进会进日志的请求体。

## 截图 agent：分辨率、坐标、历史

Computer use 的观察是翻拍式截图，不是视频。Anthropic 研究文写过：模型要会数像素才能点准。产品循环是：截屏 → 模型出 `click` / `type` → 宿主执行 → 再截。要点：

1. **先缩再送。** 模型坐标系是缩小后的图。点击 $(x, y)$ 要乘缩放比映回 OS。你自己乱缩、不告诉模型真实屏宽，点会漂。
2. **指令文本放在图前面。** Computer use 文档写：同一 user 数组里，目标描述放截图前，点击更准。
3. **历史截图要丢。** 每步一张约 1568 token 的图，二十步就三万视觉 token。只留最近 1–2 张，旧的改成「已执行 click at …」的文本。这会改消息前缀，缓存点只能钉在 tools / system，见 `anthropic-tool-roundtrip`。
4. **屏幕是不可信输入。** 像素里的字能当注入，见 `anthropic-mm-harm` 和 `anthropic-prompt-injection`。敏感动作仍要产品层确认，见 `anthropic-computer-use`。

口算例子：1920×1080 在标准档会先缩到大约 1456×819，再按 28 切，大约 52×30 块，接近 1560 视觉 token。同一张图在高分辨率档可以到两千多。agent 循环里这是每一步的固定税，比「再加一句 system」贵得多。

坐标映射：$x_{\mathrm{os}}=x_{\mathrm{model}}\cdot W_{\mathrm{os}}/W_{\mathrm{model}}$，宽高分别乘，不要假设正方形缩放。缩完再送、点完再截图回读，比信一次 bbox 稳。Files API 的 `file_id` 只省传输，不省 $T_{\mathrm{vis}}$。

错法：把 4K 桌面原样塞进每一步；用缩略图点图标；多图不编号导致「左边那张」指错；用 URL 拉内网截图却把签名 URL 泄漏进日志。和 `anthropic-tool-use` 同一句：模型提议点击，宿主按缩小后的坐标系执行，执行权不在像素里。

## 追问

- **GIF 能动吗？** 文档：动画不支持，只用第一帧。时间线任务自己抽帧当多图，并标明次序。
- **和 PDF 谁贵？** 原生 PDF 是「每页一张图 + 文本层」，见 `anthropic-pdf`。纯截图书页没有文本层，引用落不了句。
- **坐标能当接地真值吗？** 不能。官方说空间输出是近似。点按钮要截图回读，不要信一次框。
- **人像识别？** 可接受使用政策：不能用来指认照片里的人。产品要拒，不是靠模型「看起来像不会」。
