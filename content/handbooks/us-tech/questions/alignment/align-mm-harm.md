---
id: align-mm-harm
section: alignment
order: 24
level: S
title: 对齐：图文有害——截图越狱与隐写指令
quick: "图里的文字也能携带越狱指令，纯文本过滤器看不到这条通道。我会把图片作为不可信数据，用 OCR、文本审核和图像分类一起检查；支付、发信等高风险动作还要由用户明确授权。"
tags:
  - OpenAI
  - Google
  - Anthropic
  - Multimodal
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FigStep — Jailbreaking Large Vision-language Models via Typographic Visual Prompts
    url: https://arxiv.org/abs/2311.05608
    type: primary
  - title: Jailbreak in Pieces — Compositional Adversarial Attacks on Multi-Modal Language Models
    url: https://arxiv.org/abs/2307.02483
    type: primary
  - title: Red Teaming Language Models to Reduce Harms
    url: https://arxiv.org/abs/2209.07858
    type: primary
---

图像也要按不可信输入处理，因为模型能读懂像素里的指令，纯文本过滤器却看不到它。比如用户只写「请描述这张图」，图片中却放了有害请求，文本日志看起来正常，视觉模型仍可能照着执行。FigStep 展示了图中文字这条通道，Jailbreak in Pieces 则展示了图文组合攻击。

## 为什么会漏过审核

对齐后的 VLM 可能拒绝文本越狱，却把图片内容当成用户给的证据读进上下文。跨模态绕过有几种情况：

截图越狱会把本应拦截的提示放进图片或 UI 截屏。视觉编码器把字读进融合表示后，模型可能照着做。这和工具输出注入一样，都是不可信数据进入了指令上下文。

有害请求也可以写成列表、表格或流程图，外面配一句无害 caption。只审 caption 就会漏检。还可能把请求拆到文字、图片或多张裁剪中，各通道单看都通过，融合后才越界。

隐写和对抗扰动更难靠人工发现：人眼看着是风景，编码器却能读出扰动或低位信息。只要存在这种对人不可见、对编码器可见的通道，人工看图抽查就不能覆盖全部风险。

单加一句「忽略图里的字」不够，因为预训练融合已经让视觉 token 和文本 token 进入同一 attention 计算。

## 输入和动作分别检查

我会先提取图片和屏幕中可以审核的内容，再交给大模型：

1. **OCR + 文本 moderation。** 按文本审核规则检查图上的字。OCR 会错，所以这是一层，不是唯一层。
2. **图像分类 / 哈希。** CSAM、暴力、已知违法媒体走哈希和专用分类器，同步阻断，不异步。儿童安全不走「模型再想想」。
3. **指令面与数据面分开。** 视觉 token 标成 data。高风险工具（发信、支付、改权限）的参数必须来自用户明确文本或确认框，不能只来自图里读到的「请转账」。
4. **跨模态一致。** 文说无害、图像有害指令，走拒答或人审，不要默默听图。
5. **红队切片。** 攻击分类要单列「视觉指令」，不能只用公开文字 jailbreak 集，否则 overfitting 评测，见 `align-red-team`。

端侧的私有相册可以尽量不上云，但设备上仍要做轻量审核。审核也要测误拒，避免把新闻截图和医疗说明书都拦掉。

评测：攻击成功率按通道报（纯文、纯图、图文组合、截屏 UI），加上误杀率。不要只报一张「安全分」。生成侧仍要输出过滤，因为视觉绕过成功后模型会在文本里把有害内容写出来。

云端部署可以叠加专用视觉分类器和 OCR；端侧则要兼顾延迟、隐私和轻量审核。UGC 图片与模型生成输出也需要分别审核。设计时要能画清楚攻击从哪个通道进入，以及动作执行前在哪里拦截。

训练时可以把图文有害性作为 RFT grader 或 reward model（RM）的一项指标，但要同时观察它和 helpful 目标的冲突。已知违法内容和哈希匹配这类能确定检查的信号，直接用规则处理。

相关：`align-red-team`、`design-moderation`、`design-agent-harness`、`align-over-refuse`、`align-safety-tax`。

## 追问

**为什么文本过滤器不够？**
它根本看不到像素里的字。漏的是通道，不是阈值。
**OCR 全拦图上的字会怎样？**
合法截图（课表、药盒、白板）被杀。要分级：指令口吻 vs 引用证据，高风险动作再加确认。
**和工具注入有何同构？**
都是不可信数据进上下文。权限和确认把损失封顶，仅在 prompt 中声明规则还不够。
**隐写防得尽吗？**
不尽。承认残余风险，用分类器、扰动检测、动作层硬闸；发布写「未检出」不是「保证没有」。
