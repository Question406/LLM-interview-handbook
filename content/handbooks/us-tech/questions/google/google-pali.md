---
id: google-pali
section: google
order: 27
level: A
title: Google：PaLI / PaliGemma 多任务多语言视觉-语言，和 Gemini 差在哪
quick: >-
  PaLI 是视觉编码器加语言模型的生成式 VLM：多任务前缀、多语言图文、OCR 当一等任务。PaLI-3 / PaliGemma
  说明对比预训练的视觉塔比盲目把 ViT 做大更划算。Gemini 是同一条解码器吃交错模态，不是这套 encoder-decoder
  前缀机。
tags:
  - Google
  - PaLI
  - PaliGemma
  - VLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PaLI — A Jointly-Scaled Multilingual Language-Image Model
    url: https://arxiv.org/abs/2209.06794
    type: primary
  - title: PaLI-X — On Scaling up a Multilingual Vision and Language Model
    url: https://arxiv.org/abs/2305.18565
    type: primary
  - title: PaLI-3 Vision Language Models — Smaller, Faster, Stronger
    url: https://arxiv.org/abs/2310.09199
    type: primary
  - title: PaliGemma — A versatile 3B VLM for transfer
    url: https://arxiv.org/abs/2407.07726
    type: primary
---

PaLI 是 Google 公开的 Pathways 视觉-语言模型族：把放大的 ViT 和放大的语言模型拼成生成式多任务机。研究岗问这题，要听你把 **任务前缀、语言覆盖、视觉塔从哪预训练** 讲清楚，而不是背 17B。和 Flamingo 的冻 LM + 少样本见 `google-flamingo`；和 Gemini 原生解码器见 `google-gemini-mm`。不是某次逐字真题。

## 骨架：视觉 token 进语言编码器，文本当目标

第一代 PaLI：分类预训练的大 ViT（ViT-e 约 4B）加 mT5 一类 encoder-decoder。图被切成 patch，见 `google-vit-patch`，进语言编码器一侧；解码器生成文本。任务靠自然语言前缀区分：「用某语言写 alt text」「根据图回答」。这和对话 SFT 的 user / assistant 轮次不是同一套模板，后训练怎么切见 `google-mm-sft`。

PaLI-X 继续双边放大（更大 ViT + 更大 UL2 式 LM），caption、VQA、文档、检测式输出、视频问答都能做。公开观察：ImageNet 已经饱和的视觉塔，接到 VLM 上仍可能涨——因为 VLM 要的是区域和字，不是 1000 类标签。面试别把「视觉塔越大越好」说到 PaLI-3 已经改口的地方。

Shape：视觉 $[N, D]$ 和文本前缀在编码器里拼成 $[N+T_{\mathrm{pre}}, D]$，解码 $[T_{\mathrm{out}}, D]$。$N$ 跟分辨率走，没有 Flamingo 那种默认 64 latent。所以 PaLI 吃高清文档时，贵的是编码器自注意，不是 LM 窗口里塞了多少图——两边都会贵，只是账本不同。

## 多任务 × 多语言，OCR 不是附属

WebLI 一类数据把网页图、多语言描述、OCR 字拉在一起。任务混合比架构更快决定模型像什么：

- 只有自然场景 caption，模型会空泛形容，读不了菜单。
- 只有 OCR / 文档，风景图描述变干，对象计数也不稳。
- 检测或框坐标当文本输出，能逼视觉塔留空间信息，但解码格式一漂，框就废。

多语言不是把英文题机翻一遍。要看：非英文问题、图里嵌的是另一门语言的字、答案语言和问题语言不一致。机翻评测会把「翻译腔」和「看见了」混成一个分。Gemini 报告后来用 MMMU、多语言、视频等另一套切片；PaLI 族的历史贡献是 **把 OCR 和上百种语言写进同一台生成机**，不是百万 token 窗口。

PaLI-3 的关键改口：对比预训练（SigLIP 一类）的视觉塔，在「图里有字、要定位」上明显强过同等规模的分类 ViT。所以后来可以缩小视觉和语言，用数据配方追上 PaLI-X / PaLM-E 量级的老配方。PaliGemma 把这件事做成可微调的开源件：SigLIP-So400m/14 + Gemma-2B，prefix-LM 注意力（图和前缀双向，后缀因果），主打 transfer 而不是聊天产品。$224/14=16$、$16^2=256$ 个图 token；$448$ 就是 $32^2=1024$。这些数面试要能口算。

## 和 Gemini / Flamingo 怎么对照

| | PaLI 族 | Flamingo | Gemini 公开叙事 |
| --- | --- | --- | --- |
| 语言侧 | 编码-解码或 prefix-LM | 冻 decoder-only + 门控 xattn | 同一条解码器 |
| 视觉怎么进 | patch 序列进编码器 | Perceiver 压成固定 latent | 交错拼进序列 |
| 训练形态 | 多任务前缀、多语言 | 交错 few-shot | 预训练就混模态，再对话 / 工具 |
| 开源锚点 | PaliGemma | 概念论文 | 产品报告，不是这份权重 |

错法：说 PaLI 就是 Gemini 的开源版；说 PaliGemma 聊天能力等于 Gemini；把 CLIP 检索当成 PaLI 的生成目标。CLIP 是对齐；PaLI 是条件生成。产品要引用网页、要点击 UI，还得上工具，见 `google-gemini-agent`。

我会主动报的取舍：要做一个可微调的文档 / 检测头，PaliGemma 配方清晰、分辨率档（256 / 1024 token）好讲。要做小时级视频和百万上下文对话，那是 Gemini 1.5 的窗口故事，见 `google-gemini-longctx`，不是把 PaLI-X 再加层。

## 追问

- **为什么 PaLI-3 能以小打大？** 视觉塔的预训练目标换了，数据更管图里的字和框，不是参数神话。
- **前缀任务和对话 SFT 能直接混吗？** 能，但格式冲突会表现成「会做 VQA 不会聊天」或反过来。要显式混，见 `google-mm-sft`。
- **检测当文本会不会比专用检测头差？** 常常差在坐标校准。VLM 赢在开放词表；要像素级框，专用头或再配分割更稳。
- **多语言 OCR 的失败模式？** 问句一种语言、图里另一种、答案第三种。只报英文 TextVQA 不够。
