---
id: google-gemini-mm
section: google
order: 19
level: A
title: Google：Gemini 原生多模态，视觉 token、交错训练，OCR 还是像素
quick: "原生指图 / 音 / 视频和文本进同一条解码器，交错混训，不是冻住 CLIP 再接一层投影。视觉 token 数跟分辨率和帧率走，和文本抢同一窗口。文档任务先问版面是不是答案的一部分：纯 OCR 便宜但丢表和字号；像素贵但布局还在。"
tags:
  - Google
  - Gemini
  - Multimodal
  - Vision tokens
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: primary
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: primary
  - title: NaViT — Patch n' Pack
    url: https://arxiv.org/abs/2307.06304
    type: primary
---

Gemini 1.0 / 1.5 的公开卖点是原生多模态：同一套权重处理文本、图像、音频、视频，序列里交错出现。Google 研究岗问这题，不是背「我们是端到端的」，而是问视觉到底占了多少上下文、训练信号怎么对齐、文档走 OCR 还是走像素。长窗口预算见 `google-gemini-longctx`。

## 视觉 token：和文本抢 $T$

图像侧通常是 ViT 式切 patch，每块一个 token（可能再加压缩 / pooling）。数量跟分辨率走，不跟「一张图」走。口算：边长 768、patch 16，大约 $48\times 48=2304$ 个 patch。这不是 Gemini 公开超参，是数量级。视频再乘帧数：1 fps 的一分钟已经和一篇长文一个量级。1.5 能吃小时级视频，靠的是百万 token 窗口，不是视觉编码器变免费。

所以 serving 要先问：这张图需要多大分辨率。图标、UI 截图、公式，降采样会把判别信号抹掉；风景图、演示文稿背景，可以狠压。NaViT 一类把不同分辨率 pack 进同一 batch，避免所有图都 pad 成正方形浪费。面试把「可变分辨率」说成 packing 和位置编码，不要说成又一个模型名字。

音频类似：把波形编成时间帧 token，和文本交错。失败模式是时间对齐：模型能描述画面，却把「第 3 分钟说的话」安到第 10 分钟。评测要带时间戳，不要只做开放式描述。

Shape 口头报：文本是 $[B, T_{\mathrm{txt}}, D]$，视觉是 $[B, T_{\mathrm{vis}}, D]$，拼在序列维上变成 $[B, T_{\mathrm{txt}}+T_{\mathrm{vis}}, D]$。位置编码必须能区分模态和时空，不能假定所有 token 都是从左到右的词。

## 交错训练：对照两阶段连接器

LLaVA 式常见做法：冻视觉编码器，训一个投影，再指令微调 LM。这是连接器，能很快，但视觉表示不跟着语言模型的梯度长。Gemini 公开叙事是从早期就把多模态序列混进预训练：一段文本、一张图、一句问、一段视频帧，next-token（或混合目标）在同一条因果链上。

交错的监督含义：模型要学会「图后紧跟的文本是在指图」，而不是两个塔分别编码再点积。对比学习（CLIP）仍可能当辅助；主 LM 目标是生成和跨模态条件。面试别把 CLIP 和原生 LM 并成一句「都是多模态」。

数据坑比架构坑大。网页 alt-text 很噪；PDF 里图和附近段落不一定相关；视频旁白在讲广告，画面是节目。要对齐质量做过滤，否则模型学会「看见图就说图注里的广告语」。评测用需要看图才能答的题，纯文本能答对的题不算多模态能力。

## OCR 还是像素

文档 / 截图三条路：

1. 只 OCR。Token 便宜，表格、多栏、字号、手写、图标会丢。适合已是干净数字文档、布局不进答案。
2. 只像素。布局还在，贵。一张高清 PDF 页可以吃掉几千视觉 token，长上下文成本见 `google-gemini-longctx`。
3. 交错混合。页图 + 可选 OCR 文本同时进序列。OCR 当提示，像素当仲裁。Gemini 原生能力让这条成为默认产品形态：用户贴截图，不必先跑一套独立 OCR 服务。

我会按错误类型选：要抄数字、对单元格，像素或混合；要检索条款关键词，OCR + 文本检索往往更便宜。别默认「原生所以永远不 OCR」。原生的好处是少一座会漂的级联（OCR 错了，LM 无法回到像素）；代价是 token 预算。

Serving 账要和文本同一套：一次请求的 $T$ 是文本 token 加视觉 token 加音频帧。把一张高清截图塞进已经很长的聊天记录，KV 和 输入预填充（prefill，即处理输入并建立缓存） 会一起涨，见 `google-gemini-longctx`。产品上该压分辨率就压，该 OCR 就 OCR，不要因为「原生」就把所有像素原样送进窗口。

常见误区是：把一张图说成「1 个视觉 token」；说原生多模态所以不需要长上下文；把连接器微调说成 Gemini 的预训练。

## 追问

- **冻结视觉编码器行不行？** 做产品原型行。要吃进 Gemini 那种交错推理，视觉塔最好能被 LM 损失更新，否则细节（文字、UI 状态）上不去。
- **视频怎么抽样？** 帧率是超参。动作密集要加密；讲座可以低 fps 加音频轨。评测必须固定抽样，否则分数不可比。
- **和工具调用怎么分？** 算像素上的字，模型自己看；要查库、要精确算术，仍该把工具留下。原生多模态不是取消工具。
- **位置编码怎么处理二维？** 视觉 token 需要二维（或时空）位置，再和文本一维位置嵌进同一注意力。实现各异，面试抓住「不能共用纯 1D 词位置」即可。
