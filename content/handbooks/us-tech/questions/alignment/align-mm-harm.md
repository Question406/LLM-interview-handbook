---
id: align-mm-harm
section: alignment
order: 24
level: S
title: 对齐：图文有害——截图越狱与隐写指令
quick: >-
  文本过滤器看不见图里的字。截图把越狱提示印进像素，VLM 当视觉证据读进去；隐写 / 对抗扰动把指令藏在人看不出的地方。
  防御是把图当不可信输入：OCR 再过文本审核、图像分类、高风险动作不靠视觉指令执行。
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

Google Gemini、OpenAI 的图文模型、Apple / Meta 的端侧视觉都会问「有害请求不走纯文本怎么办」。FigStep 一类公开工作把请求写成图上的字；Jailbreak in Pieces 把攻击拆到图和文两条通道。不是某次现场逐字题。文本红队见 `align-red-team`；产品审核管道见 `design-moderation`。本题收**跨模态绕过**，不讲具体构造步骤。

## 威胁模型：指令走了视觉通道

对齐后的 VLM 对文字越狱有拒答，对图像常常还当「用户给的证据」。几类面试够用的通道：

**截图越狱。** 把本该被输入过滤器拦下的提示拍成图、或 UI 截屏。文本 moderation 看到的是「请描述这张图」，视觉编码器把字读进融合表示。模型按图里的指令走，日志里用户文本是干净的。这和工具输出注入同构：像素是不可信数据，见 `design-agent-harness`。

**排版 / 图形提示。** 有害请求以列表、表格、流程图出现在图中，配一句无害 caption。评测若只扫 caption，会报假安全。

**跨模态拼接。** 文无害、图有害，或反过来；多图把一条指令拆到几张裁剪里。单模态分类器都过，融合后才越界。

**隐写与对抗扰动。** 人眼看是风景，扰动或低位信息里是指令。不一定要「真隐写术」三个字；面试说清：存在**对人不可见、对编码器可见**的通道，就足以绕过只给人看的抽查。

不要把「加一条 system prompt：忽略图里的字」当方案。预训练融合已经把视觉 token 和文本 token 放进同一注意力。

## 防御要当输入管道，不要当生成后修饰

我会把图和屏先变成**可审核的派生物**，再进大模型：

1. **OCR + 文本 moderation。** 图上的字按文本政策打。OCR 会错，所以这是一层，不是唯一层。
2. **图像分类 / 哈希。** CSAM、暴力、已知违法媒体走哈希和专用分类器，同步阻断，不异步。儿童安全不走「模型再想想」。
3. **指令面与数据面分开。** 视觉 token 标成 data。高风险工具（发信、支付、改权限）的参数必须来自用户明确文本或确认框，不能只来自图里读到的「请转账」。
4. **跨模态一致。** 文说无害、图像有害指令，走拒答或人审，不要默默听图。
5. **红队切片。** 攻击分类要单列「视觉指令」，不能只用公开文字 jailbreak 集，否则过拟合评测，见 `align-red-team`。

端侧（Apple）还要讲：私有相册尽量不上云，但设备上仍要有轻量审核；不能把「没出设备」当成「没有害」。过度拒绝会把截图里的新闻、医疗说明书全拦，见 `align-over-refuse`。

评测：攻击成功率按通道报（纯文、纯图、图文组合、截屏 UI），加上误杀率。不要只报一张「安全分」。生成侧仍要输出过滤，因为视觉绕过成功后模型会在文本里把有害内容写出来。

公司差：Google / OpenAI 云端可以叠专用视觉分类器和 OCR；Apple 端侧要在延迟和隐私里塞进轻量层，过不了的再上 Private Cloud。Meta 还要考虑 UGC 图和模型输出两套管道。白板先画「文本 moderation 看不见像素」，再画动作层硬闸——评委听的是通道，不是又一个分类器名。

训练侧：把图文有害当 RFT grader 或 RM 的一维，会和 helpful 打架，见 `align-safety-tax`。能规则的（哈希、已知违法）不要交给 RL。

## 追问

- **为什么文本过滤器不够？** 它根本看不到像素里的字。漏的是通道，不是阈值。
- **OCR 全拦图上的字会怎样？** 合法截图（课表、药盒、白板）被杀。要分级：指令口吻 vs 引用证据，高风险动作再加确认。
- **和工具注入有何同构？** 都是不可信数据进上下文。权限和确认把损失封顶，prompt 声明不够。
- **隐写防得尽吗？** 不尽。承认残余风险，用分类器、扰动检测、动作层硬闸；发布写「未检出」不是「保证没有」。
