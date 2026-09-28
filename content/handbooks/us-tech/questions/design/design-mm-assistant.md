---
id: design-mm-assistant
section: design
order: 17
level: A
title: 设计：多模态助手的引用区域与视觉 token 预算
quick: >-
  图 / 屏 / 语音到达时间差一个数量级，没到的模态不当证据。答案要能指回图上的框或屏上的区域，引用对不上就删句。
  视觉 token 按补丁进上下文，高分辨率不能默认全图进大模型。延迟状态机见 `design-multimodal-prod`。
tags:
  - Multimodal
  - Apple
  - Google
  - Grounding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: primary
  - title: Introducing Apple Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Robust Speech Recognition via Large-Scale Weak Supervision
    url: https://arxiv.org/abs/2212.04356
    type: primary
---

Apple Intelligence / Siri、Gemini 相机问答、Copilot 看屏都会问「你指的是图上哪一块」。Gemini 报告讲能力；Apple 讲端侧和隐私。三路时钟和打断见 `design-multimodal-prod`；本题把引用区域和 patch token 预算讲透。语音接地专项见 `apple-siri-grounded`。图文有害见 `align-mm-harm`。

## 引用是框，不是一句「如图所示」

证据 $E$ 里每条视觉记录带：`image_id`、时间戳、可选 `bbox`（归一化 $[x_1,y_1,x_2,y_2]$）、OCR 字、权限。生成要输出可点击的引用，UI 把对应区域高亮。评测拆两截：文本是否被该区域支持（蕴含 / 人标），框与金标区域的 IoU。只有文字对、框飘走，算没接地。

用户说「这个」时，焦点是当前帧、上一张图、还是语音刚提到的实体。把 UI 焦点和帧 ID 写进 $E$，口头也说编号。「左上那块」没有坐标就追问，不要猜。多图必须编号；屏上连续帧先采样，场景变化才重编码，见 `design-multimodal-prod`。

```python
def grounded_ok(span, bbox, ocr_spans, iou_min=0.5):
    if bbox is None:
        return False
    if not (iou(bbox, span.gold_box) >= iou_min):
        return False
    return span.text in ocr_spans or entailment(span.text, crop(bbox))
```

引用对不上：删句、改口、或拒答。金额、药名、车牌这类槽位，ASR 和 OCR 不一致就问一句，不要默默选一边。高风险动作走确认框，参数不能只来自图上读到的字。

## 视觉 token 是一等公民预算

补丁大小 $P$、图 $H\times W$，粗算 $N_p \approx (H/P)\times(W/P)$。1024 边长、$P=14$ 就是几千 token，再加高分辨率裁剪会把文本历史挤掉。策略：

1. **查询分类。** 「现在几点」不进视觉编码器。「图里牌子」才付 $N_p$。
2. **先粗后细。** 低分辨率全图定位区域，再对引用框做高分辨率作物进第二轮。不要默认 anyres 全开。
3. **屏。** 先 OCR + 可访问性树，视觉只补图标和无字 UI。固定 fps 进大模型会把电和上下文打光。
4. **打包。** 文本与视觉 token 混排时，损失仍只在文本位置；视觉位置 mask 掉，shape 写 `[B, T_text + T_vis, D]`。

端侧：相册、截屏优先设备编码器；上传要用户可见指示。云端跑重视觉时，引用框在端上裁剪再传作物，比传整张原图更符合隐私叙事。弱网：先到的语音可以确认「图还在处理」，图后到再补一句带引用的纠正，不要两套矛盾答案并存。

失败模式：图没到用预训练知识报品牌；框很大等于没引；OCR 吃掉小数点后下单；为了快用小视觉模型，大模型稍后推翻且不改框。延迟指标：TTFA、各模态等待、视觉超时率、引用点击率（用户有没有去看框；全不点可能是框在瞎画）。

Serving：视觉 encoder 绑在 prefill，同一张图多轮问应走前缀 KV；图一换，视觉段必须失效。连续看屏不要 30 fps 进大模型，场景变化才重编码。和 `design-chat-serving` 同一套连续批，但准入要按 $T_{\mathrm{vis}}$ 估 KV 页，不能只按文本长度。内容安全对图同步轻量审核，见 `design-moderation`。

## 追问

- **为什么不把整张图当一个 embedding？** 没法区域引用，也难和「这个」对齐。检索可以全局向量，回答要框。
- **IoU 多高算过？** 产品用分层：图标要严，海报上的大段文字可以松；门禁看虚假高亮率而不是平均 IoU。
- **和文本 RAG 引用有何不同？** 块 ID 换成空间区域；权限仍走元数据，像素泄漏同样算事故，见 `design-mm-rag`。
- **语音怎么念引用？** 说编号和短标签，不念坐标。屏幕上同时亮框。
