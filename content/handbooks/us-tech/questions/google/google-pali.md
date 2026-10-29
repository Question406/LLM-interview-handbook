---
id: google-pali
section: google
order: 27
level: A
title: Google：PaLI / PaliGemma 多任务多语言视觉-语言，和 Gemini 差在哪
quick: >-
  PaLI 用视觉编码器加语言模型做条件生成，通过任务前缀覆盖多任务、多语言，并把 OCR 作为主要任务之一。PaLI-3 和 PaliGemma
  说明，改进视觉塔的对比预训练也能提高效率，不必一味增大 ViT。Gemini 的公开路线则是让多种模态进入同一条交错生成序列。
tags:
  - Google
  - PaLI
  - PaliGemma
  - VLM
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: PaLI — A Jointly-Scaled Multilingual Language-Image Model
    url: 'https://arxiv.org/abs/2209.06794'
    type: primary
  - title: PaLI-X — On Scaling up a Multilingual Vision and Language Model
    url: 'https://arxiv.org/abs/2305.18565'
    type: primary
  - title: 'PaLI-3 Vision Language Models — Smaller, Faster, Stronger'
    url: 'https://arxiv.org/abs/2310.09199'
    type: primary
  - title: PaliGemma — A versatile 3B VLM for transfer
    url: 'https://arxiv.org/abs/2407.07726'
    type: primary
---

## 可以这样回答

PaLI 把视觉编码器和语言模型连起来，用任务前缀指定要生成什么。比如同一张菜单，前缀可以要求读出文字、回答问题，或用另一种语言描述；OCR 和多语言因此都是主要训练任务。它是 Google 公开的 Pathways 视觉语言模型族，与 Flamingo 的冻结 LM 加少样本路线见 `google-flamingo`，与 Gemini 的交错生成路线见 `google-gemini-mm`。

第一代 PaLI：分类预训练的大 ViT（ViT-e 约 4B）加 mT5 一类 encoder-decoder。图被切成 patch，见 `google-vit-patch`，进语言编码器一侧；decoding 器生成文本。任务靠自然语言前缀区分：「用某语言写 alt text」「根据图回答」。这和对话 SFT 的 user / assistant 轮次不是同一套模板，后训练怎么切见 `google-mm-sft`。

## 技术备查

PaLI 把视觉编码器和语言模型连起来，用任务前缀指定要生成什么。比如同一张菜单，前缀可以要求读出文字、回答问题，或用另一种语言描述；OCR 和多语言因此都是主要训练任务。它是 Google 公开的 Pathways 视觉语言模型族，与 Flamingo 的冻结 LM 加少样本路线见 `google-flamingo`，与 Gemini 的交错生成路线见 `google-gemini-mm`。

第一代 PaLI：分类预训练的大 ViT（ViT-e 约 4B）加 mT5 一类 encoder-decoder。图被切成 patch，见 `google-vit-patch`，进语言编码器一侧；decoding 器生成文本。任务靠自然语言前缀区分：「用某语言写 alt text」「根据图回答」。这和对话 SFT 的 user / assistant 轮次不是同一套模板，后训练怎么切见 `google-mm-sft`。

PaLI-X 继续双边放大（更大 ViT + 更大 UL2 式 LM），caption、VQA、文档、检测式输出、视频问答都能做。公开观察：ImageNet 已经饱和的视觉塔，接到 VLM 上仍可能涨：因为 VLM 要的是区域和字，不是 1000 类标签。面试别把「视觉塔越大越好」说到 PaLI-3 已经改口的地方。

从形状看，视觉 $[N, D]$ 和文本前缀在编码器里拼成 $[N+T_{\mathrm{pre}}, D]$，decoding $[T_{\mathrm{out}}, D]$。$N$ 跟分辨率走，没有 Flamingo 那种默认 64 latent。所以 PaLI 吃高清文档时，贵的是编码器自注意，不是 LM 窗口里塞了多少图；两边都会贵，只是账本不同。

WebLI 一类数据把网页图、多语言描述、OCR 字拉在一起。任务配比会直接改变模型的表现：

- 只有自然场景 caption，模型会空泛形容，读不了菜单。
- 只有 OCR / 文档，风景图描述变干，对象计数也不稳。
- 检测或框坐标当文本输出，能逼视觉塔留空间信息，但 decoding 格式一漂，框就废。

多语言不是把英文题机翻一遍。要看：非英文问题、图里嵌的是另一门语言的字、答案语言和问题语言不一致。机翻评测会把「翻译腔」和「看见了」混成一个分。Gemini 报告后来用 MMMU、多语言、视频等另一套切片；PaLI 族的历史贡献是把 OCR 和上百种语言写进同一台生成机，不是百万 token 窗口。

PaLI-3 进一步发现，对比预训练（SigLIP 一类）的视觉塔，在「图里有字、要定位」上明显强过同等规模的分类 ViT。所以后来可以缩小视觉和语言，用数据配方追上 PaLI-X / PaLM-E 量级的老配方。PaliGemma 把这件事做成可微调的开源件：SigLIP-So400m/14 + Gemma-2B，prefix-LM attention（图和前缀双向，后缀因果），主打 transfer 而不是聊天产品。$224/14=16$、$16^2=256$ 个图 token；$448$ 就是 $32^2=1024$。这些数可以直接用分辨率除以 patch 大小算出来。

| | PaLI 族 | Flamingo | Gemini 公开叙事 |
| --- | --- | --- | --- |
| 语言侧 | 编码-decoding 或 prefix-LM | 冻 decoder-only + gating xattn | 同一条 decoding 器 |
| 视觉怎么进 | patch 序列进编码器 | Perceiver 压成固定 latent | 交错拼进序列 |
| 训练形态 | 多任务前缀、多语言 | 交错 few-shot | 预训练就混模态，再对话 / 工具 |
| open-source reference | PaliGemma | 概念论文 | 产品报告，不是这份权重 |

常见误区是：说 PaLI 就是 Gemini 的开源版；说 PaliGemma 聊天能力等于 Gemini；把 CLIP 检索当成 PaLI 的生成目标。CLIP 是对齐；PaLI 是条件生成。产品要引用网页、要点击 UI，还得上工具，见 `google-gemini-agent`。

取舍：要做一个可微调的文档 / 检测头，PaliGemma 配方清晰、分辨率档（256 / 1024 token）好讲。要做小时级视频和百万上下文对话，那是 Gemini 1.5 的窗口故事，见 `google-gemini-longctx`，不是把 PaLI-X 再加层。

## 追问

**为什么 PaLI-3 能以小打大？**
视觉塔的预训练目标换了，数据更管图里的字和框，提升来自预训练目标和数据配方。

**前缀任务和对话 SFT 能直接混吗？**
能，但格式冲突会表现成「会做 VQA 不会聊天」或反过来。要显式混，见 `google-mm-sft`。

**检测当文本会不会比专用检测头差？**
常常差在坐标 calibration。VLM 赢在开放 vocabulary；要像素级框，专用头或再配分割更稳。

**多语言 OCR 的失败模式？**
问句一种语言、图里另一种、答案第三种。只报英文 TextVQA 不够。
