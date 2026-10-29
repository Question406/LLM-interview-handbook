---
id: design-mm-assistant
section: design
order: 17
level: A
title: 设计：multimodal 助手的引用区域与视觉 token 预算
quick: >-
  回答要能指回图上的框或屏幕区域，引用对不上就删句，尚未到达的模态不能当证据。视觉 token 按 patch
  占上下文，高分辨率图先粗定位、再裁剪细看；模态延迟状态机见 `design-multimodal-prod`。
tags:
  - Multimodal
  - Apple
  - Google
  - Grounding
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: 'https://arxiv.org/abs/2312.11805'
    type: primary
  - title: Introducing Apple Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Robust Speech Recognition via Large-Scale Weak Supervision
    url: 'https://arxiv.org/abs/2212.04356'
    type: primary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

设计能针对图片、屏幕或视频帧作答的 multimodal 助手，重点是把回答中的视觉证据指向具体区域，并在有限上下文预算内处理高分辨率输入。

### 需要满足的功能

- 接收问题、图像/帧及当前 UI 焦点，返回回答和可点击的视觉引用。
- 处理“这个/刚才那张”等指代、画面变化、图片超时与区域细节不足。
- 根据任务保证必要视觉证据可用，而不是默认输入无限多视觉 token。

### 约束与交付物

引用需带正确 image/frame 标识及区域位置；文字正确但框错也应能被发现。需要说明隐私权限、定位质量、视觉预算、延迟和无证据时的行为。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

用户指着当前截图中的某个按钮问“这个做什么”，回答应引用当前截图的对应区域；不能把上一帧同位置的其他控件当成依据。

## 可以这样回答

multimodal 助手的回答要能指回具体图像区域，同时按查询需要控制视觉 token。比如用户说「这个」时，系统要知道当前 UI 焦点对应哪张图、哪一帧和哪个框，再高亮引用；只说「如图所示」无法检查证据。高分辨率图片先粗定位、再裁剪细看，避免把文本历史挤出上下文。

Apple Intelligence / Siri、Gemini 相机问答、Copilot 看屏都涉及这类问题。Gemini 报告介绍能力，Apple 强调 on-device 和隐私。三路时钟及打断见 `design-multimodal-prod`；语音证据支持见 `apple-siri-grounded`；图文有害见 `align-mm-harm`。

## 技术备查

## 解题思路与参考答案

multimodal 助手的回答要能指回具体图像区域，同时按查询需要控制视觉 token。比如用户说「这个」时，系统要知道当前 UI 焦点对应哪张图、哪一帧和哪个框，再高亮引用；只说「如图所示」无法检查证据。高分辨率图片先粗定位、再裁剪细看，避免把文本历史挤出上下文。

Apple Intelligence / Siri、Gemini 相机问答、Copilot 看屏都涉及这类问题。Gemini 报告介绍能力，Apple 强调 on-device 和隐私。三路时钟及打断见 `design-multimodal-prod`；语音证据支持见 `apple-siri-grounded`；图文有害见 `align-mm-harm`。

## 把回答定位到具体区域

证据 $E$ 里每条视觉记录带：`image_id`、时间戳、可选 `bbox`（normalization $[x_1,y_1,x_2,y_2]$）、OCR 字、权限。生成要输出可点击的引用，UI 把对应区域高亮。评测拆两截：文本是否被该区域支持（蕴含 / 人标），框与 gold labels 区域的 交并比（IoU，即两个区域的交集与并集之比）。文字正确但引用框位置错误，算没有实际证据支持。

用户说「这个」时，焦点是当前帧、上一张图、还是语音刚提到的实体。把 UI 焦点和帧 ID 写进 $E$，口头也说编号。「左上那块」没有坐标就追问，不要猜。多图必须编号；屏上连续帧先 sampling，场景变化才重编码，见 `design-multimodal-prod`。

```python
def grounded_ok(span, bbox, ocr_spans, iou_min=0.5):
    if bbox is None:
        return False
    if not (iou(bbox, span.gold_box) >= iou_min):
        return False
    return span.text in ocr_spans or entailment(span.text, crop(bbox))
```

引用对不上：删句、改口、或拒答。金额、药名、车牌这类槽位，ASR 和 OCR 不一致就问一句，不要默默选一边。高风险动作走确认框，参数不能只来自图上读到的字。

## 按查询分配视觉 token

补丁大小 $P$、图 $H\times W$，粗算 $N_p \approx (H/P)\times(W/P)$。1024 边长、$P=14$ 就是几千 token，再加高分辨率裁剪会把文本历史挤掉。策略：

1. **查询分类。** 「现在几点」不进视觉编码器。「图里牌子」才付 $N_p$。
2. **先粗后细。** 低分辨率全图定位区域，再对引用框做高分辨率裁剪图进第二轮。不要默认 anyres 全开。
3. **屏。** 先 OCR + 可访问性树，视觉只补图标和无字 UI。固定 fps 进 large model 会把电和上下文打光。
4. **打包。** 文本与视觉 token 混排时，损失仍只在文本位置；视觉位置 mask 掉，shape 写 `[B, T_text + T_vis, D]`。

on-device：相册、截屏优先设备编码器；上传要用户可见指示。云端跑重视觉时，引用框在 on-device 裁剪再传裁剪图，比传整张原图更符合隐私叙事。弱网：先到的语音可以确认「图还在处理」，图后到再补一句带引用的纠正，不要两套矛盾答案并存。

失败模式：图没到用 pre-training 知识报品牌；框很大等于没引；OCR 吃掉小数点后下单；为了快用小视觉模型，large model 稍后推翻且不改框。延迟指标：TTFA、各模态等待、视觉超时率、引用点击率（用户有没有去看框；全不点可能是框在瞎画）。

Serving：视觉 encoder 绑在 输入 prefill，同一张图多轮问应走前缀 KV；图一换，视觉段必须失效。连续看屏不要 30 fps 进 large model，场景变化才重编码。和 `design-chat-serving` 同一套连续批，但准入要按 $T_{\mathrm{vis}}$ 估 KV 页，不能只按文本长度。内容安全对图同步轻量审核，见 `design-moderation`。

## 追问

**为什么不把整张图当一个 embedding？**
没法区域引用，也难和「这个」对齐。检索可以全局向量，回答要框。
**IoU 多高算过？**
产品用分层：图标要严，海报上的大段文字可以松；evaluation gate 看虚假高亮率而不是平均 IoU。
**和文本 retrieval-augmented generation (RAG)（RAG） 引用有何不同？**
块 ID 换成空间区域；权限仍走元数据，像素 leakage 同样算事故，见 `design-mm-rag`。
**语音怎么念引用？**
说编号和短标签，不念坐标。屏幕上同时亮框。
