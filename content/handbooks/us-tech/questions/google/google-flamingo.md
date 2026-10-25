---
id: google-flamingo
section: google
order: 26
level: A
title: Google：Flamingo 用 Perceiver resampler 和交叉注意把视觉压进 LLM
quick: "Flamingo 冻结视觉编码器和 LM，用 Perceiver 把变长视觉特征压成固定 $N_{\\mathrm{lat}}$ 个 latent，再通过带门控的交叉注意力输入 LM。这样节省语言侧窗口，但压缩可能丢小字和细节，视频仍会随帧数增加 token。"
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

Flamingo 用固定数量的 latent 压缩视觉特征，再通过交叉注意力接入冻结的语言模型。它是 DeepMind 2022 年的公开少样本视觉语言方案，重点是在少动大 LM 的情况下接入图像。比如场景描述可以受益于这种压缩，但密集 OCR、小字或多目标细节可能在压缩时丢失。

视觉编码器使用冻结的 NFNet 一类模型，输出约为 $[N_{\mathrm{vis}}, D_{\mathrm{vis}}]$ 的网格特征，$N_{\mathrm{vis}}$ 可从几百到几千，随分辨率增加。Perceiver resampler 学一组 latent 查询 $L$，形状 $[N_{\mathrm{lat}}, D]$，对视觉特征做交叉注意，可再叠 latent 自注意，输出仍为 $[N_{\mathrm{lat}}, D]$。论文里的 $N_{\mathrm{lat}}$ 是几十量级，例如 64，不随 $H,W$ 增长。

视觉占用的上下文长度 $T$ 在语言侧因此从 $T_{\mathrm{txt}}+N_{\mathrm{vis}}$ 压到 $T_{\mathrm{txt}}+N_{\mathrm{lat}}$，但要额外算一次 $N_{\mathrm{lat}}\times N_{\mathrm{vis}}$ 交叉注意。这是带宽、窗口与细节的取舍，caption 和场景问答较合适；读表、UI 状态、密集 OCR 可能要增加 $N_{\mathrm{lat}}$、分块，或采用 Gemini 那类较少压缩的拼接路线。只调 latent 数而不改善数据，也不能保证 OCR 提升。

视频可先对每帧或每管 resample，再按时间拼接，每帧空间长度固定，总 token 仍随帧数 $F$ 线性增长。Resampler 是一次前向的固定开销，decode 时视觉表示 $v$ 可以缓存，无需每步重算视觉塔。这与 KV cache 不是同一块内存，但都要计入首 token 等待时间。

## 视觉怎么进入冻结 LM

Flamingo 在冻结 LM 的若干层之间插入 gated xattn-dense，文本隐状态作 query，resampler 输出作 key/value，视觉 token 进入 xattn 的 KV，文本自注意仍是因果的。门控写作：

$$
h \leftarrow h + \tanh(\alpha)\,\mathrm{XAttn}(h, v)
$$

$\alpha$ 初始化在 0 附近，让初期残差接近 0，随机视觉支路才不会立刻破坏原语言能力。这些层通常隔若干 LM 层插入，并非每层都有。训练更新 resampler 和门控层，视觉塔与 LM 冻结；后训练若解冻 LM，就更接近多模态 SFT，门控初始化的好处会减小，文本遗忘风险增加。它的优势之一是少动 70B 级 LM 也能 few-shot 看图。

连接器微调通常冻结视觉、训练投影与部分 LM，并可能把视觉和文本 token 拼进自注意；Gemini 的公开叙述是早期交错多模态预训练，让视觉表示随 LM loss 学习。Flamingo 的重点是交错图文 few-shot in-context，PaLI 偏多任务前缀生成，Gemini 产品还包括对话与工具。CLIP 双塔点积是不同路径，交叉注意与自注意拼接各有成本，不能直接排优劣。Q-Former 一类也采用学习查询去读取视觉特征，理解这一点比争名字更有用。

训练目标仍是文本 next-token，条件为前面的图和文字。例如图、描述、另一张图、问题、答案交错出现，模型要学会紧随图片的文字对应哪张图。图文错配可能让门控层只学到图注广告语，因此评测要包含离开图就答不对的题。Few-shot 示范的图数和顺序也要固定，变化会影响结果。

Gemini 公开报告没有把 Flamingo 模块作为骨架，不应编内部连接器超参。可以用它解释压缩换窗口与拼接保细节的取舍，产品在不同编码层也可能组合两种方式。

相关：`google-gemini-mm`、`google-vit-patch`、`google-video-token`、`google-pali`、`google-gemini-agent`、`google-mm-sft`
