---
id: google-flamingo
section: google
order: 26
level: A
title: Google：Flamingo 用 Perceiver resampler 和交叉注意把视觉压进 LLM
quick: >-
  冻视觉塔和冻 LM，中间用 Perceiver 把变长 patch 压成固定 $N_{\mathrm{lat}}$ 个 latent，再 gated
  交叉注意插进 LM。图可以很大，进 LM 的视觉 token 数几乎是常数。和 Gemini 原生拼接不是同一条架构。
tags:
  - Google
  - DeepMind
  - Flamingo
  - Perceiver
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Flamingo — a Visual Language Model for Few-Shot Learning
    url: https://arxiv.org/abs/2204.14198
    type: primary
  - title: Perceiver — General Perception with Iterative Attention
    url: https://arxiv.org/abs/2103.03206
    type: primary
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: secondary
---

Flamingo 是 DeepMind 2022 的公开概念：少样本看图说话，不靠把整图 patch 全塞进 LM。Google / Gemini 岗拿它当对照，问视觉信息在哪一层被压扁、LM 权重要不要动。 原生拼接见 `google-gemini-mm`；patch 数怎么爆见 `google-vit-patch`。别编内部连接器超参。

## Perceiver resampler：变长视觉进固定 latent

视觉编码器（论文用冻的 NFNet 一类）吐出网格特征，长度跟分辨率走，形状大约 $[N_{\mathrm{vis}}, D_{\mathrm{vis}}]$。$N_{\mathrm{vis}}$ 可以是几百到几千，见 `google-vit-patch`。Resampler 学一组 latent 查询 $L$，形状 $[N_{\mathrm{lat}}, D]$，对视觉特征做交叉注意（可叠加 latent 自注意），输出仍是 $[N_{\mathrm{lat}}, D]$。$N_{\mathrm{lat}}$ 论文量级是几十，比如 64，不随 $H,W$ 涨。

这是带宽和窗口的交易：LM 侧注意力从看 $T_{\mathrm{txt}}+N_{\mathrm{vis}}$ 变成看 $T_{\mathrm{txt}}+N_{\mathrm{lat}}$，外加一次 $N_{\mathrm{lat}}\times N_{\mathrm{vis}}$ 的交叉注意。高分辨率、多目标、小字，信息有可能在这一步就被平均掉。压缩不是无损。caption、场景问答题，固定 latent 很香；读表、UI 状态、密集 OCR，你得加 $N_{\mathrm{lat}}$、加切块，或改走 Gemini 那种少压缩拼接。

视频：每帧（或每管）先 resample 成 $N_{\mathrm{lat}}$，再沿时间拼。帧数 $F$ 仍线性涨 token，只是空间维被掐死。和时间采样抢预算见 `google-video-token`。

## Gated 交叉注意：冻 LM 也能插视觉

Flamingo 不把视觉 token 和文本 token 在序列维上 concat 进同一套自注意（那是连接器微调 / Gemini 更常见的公开画法）。它在冻 LM 的若干层之间插入 gated xattn-dense：文本隐状态当 query，resampler 输出当 key/value。门控写成

$$
h \leftarrow h + \tanh(\alpha)\,\mathrm{XAttn}(h, v)
$$

$\alpha$ 初始化成 0 附近，训练初期残差几乎是 0，冻好的语言模型不会一上来被随机视觉支路打烂。这是「能插模块」的数值技巧，不是可有可无的激活函数。论文里这类层通常每隔若干 LM 层插一次，不是每一层都插。

对照只抓三列，别背成一种 kernel：

- 谁更新。 Flamingo：视觉塔和 LM 冻，训 resampler 和门控层。连接器微调：冻视觉，训投影和（部分）LM。Gemini 公开叙事：早期就把交错多模态混进预训练，视觉表示可以跟着 LM 损失长。
- 视觉占多少 $T$。 Flamingo 近似常数 $N_{\mathrm{lat}}$；拼接派跟分辨率走。
- 能力形态。 Flamingo 主叙事是交错图文上的 few-shot in-context；PaLI 是多任务前缀生成，见 `google-pali`；Gemini 产品是对话加工具，见 `google-gemini-agent`。

错法：把 CLIP 双塔点积说成 Flamingo；把「交叉注意」说成一定优于自注意拼接。交叉注意省的是 LM 窗口，付的是压缩和模块缝。

## 交错序列：图在条件里，字在损失里

训练目标仍是文本 next-token，条件是前面的图和字。一段交错样本：图、一句描述、另一张图、一个问题、答案。模型要学会「图后紧跟的文本在指这张图」，而不是两个塔分别编码再检索。视觉 token 在 Flamingo 里甚至不进 LM 的自注意序列，只进 xattn 的 KV；文本自注意仍是因果的。

数据比模块更容易翻车。图文对不齐，门控层会学到「看见图就说图注广告语」。评测必须用离开图就答不对的题。少样本协议要固定示范的图数和排序，换了示范等于换了题。

Serving 上 resampler 是一次前向的固定开销；$v$ 在 decode 逐步生成时可以缓存。这和 KV cache 不是同一块内存，但都要算进首 token 延迟。不要把 resampler 说成 decode 每步都重算一遍视觉塔。

后训练若解冻 LM，就更接近多模态 SFT，见 `google-mm-sft`。门控初始化那套好处会变小，文本遗忘风险变大。

## 追问

- **latent 数怎么选？** 先按任务错误类型：场景描述 64 量级常常够；文档要加，或切块后再 resample。只调 $N_{\mathrm{lat}}$ 不改数据，OCR 上不去。
- **解冻 LM 行不行？** 可以，就变成另一条训练配方。Flamingo 的卖点是少动 70B 级 LM 还能 few-shot 看图。
- **和 Q-Former 一类是不是一回事？** 都是学查询去打视觉。面试抓「固定查询压变长网格」，不要在名字上争优先级。
- **Gemini 还用不用 resampler？** 公开报告没把 Flamingo 模块当 Gemini 骨架。对照用：压缩换窗口，还是拼进去换细节。产品可以两种都有，编码不同层。
