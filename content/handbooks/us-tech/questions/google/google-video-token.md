---
id: google-video-token
section: google
order: 30
level: A
title: Google：视频 token 的时间采样，怎么和长上下文抢预算
quick: "视频预算约等于帧数 $F$ 乘每帧空间 token，再加音频，并与文本共享窗口。每帧 256 token、1 fps 的一小时就约有 $9.2\\times 10^5$ 个视觉 token；动作密集时要提高采样率，讲座可用低 fps 配音频。评测要固定抽样协议，才能区分模型改进和输入增加。"
tags:
  - Google
  - Gemini
  - Video
  - Long context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: primary
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: primary
  - title: ViViT — A Video Vision Transformer
    url: https://arxiv.org/abs/2103.15691
    type: secondary
  - title: Flamingo — a Visual Language Model for Few-Shot Learning
    url: https://arxiv.org/abs/2204.14198
    type: secondary
---

我会先按帧数和每帧 token 数算视频预算，再根据任务调整采样率。比如同是一小时，讲座可以多依赖音频、少抽帧，操作演示却可能需要加密关键动作。Gemini 1.5 报告支持小时级视频，但这张卡不是逐字真题，也没有公开内部 fps；单帧预算见 `google-vit-patch`，窗口成本见 `google-gemini-longctx`。

先按 $T_{\mathrm{vid}}\approx F\cdot N_{\mathrm{sp}}$ 估算视觉部分。令时长 $S$ 秒、采样 $r$ fps，则 $F\approx S\cdot r$（再加镜头边界帧）。每帧的空间 token $N_{\mathrm{sp}}$ 跟分辨率和 patch 走，可能再经 pooling / resampler。粗口算：

$$
T_{\mathrm{vid}}\approx F\cdot N_{\mathrm{sp}} + T_{\mathrm{aud}}
$$

$N_{\mathrm{sp}}=256$、$r=1$、一小时：$F=3600$，视觉已经约 $9.2\times 10^5$，和 1M 窗口同一量级，文本和音频几乎没地方。$r=1$ 不是「免费」；$r=4$ 直接把视觉预算乘 4。1.5 能吃长视频，靠的是百万到千万 token 的窗口上限，不是视觉编码器变免费。Serving 一次请求的 $T$ 是文本 + 视觉 + 音频 + 工具轨迹，见 `google-gemini-mm`、`google-gemini-agent`。

音频往往比密集 RGB 帧便宜：每秒 token 少，却是讲座、会议的主信息。失败模式是时间对不齐：画面描述对，却把第 3 分钟的话安到第 10 分钟。评测要带时间戳或时间桶，不要只做开放式「讲了什么」。

ViViT 一类 tubelet 把时空块当成一个 token，$F$ 和 $N_{\mathrm{sp}}$ 一起压。Flamingo 则每帧 resample 成固定 $N_{\mathrm{lat}}$ 再沿时间拼，$N_{\mathrm{sp}}$ 被固定，$F$ 仍线性，见 `google-flamingo`。面试说清压缩发生在空间、时间还是两者，不要把三个名字并成「视频模块」。

均匀 $r$ fps 可复现，适合做回归。产品上要按错误类型改：

- 讲座、播客、屏幕录制讲稿：低 fps + 音频 + 关键字幕。画面几乎不动，$r$ 高是浪费。
- 体育、操作演示、UI 点击：动作发生在短间隔。均匀 1 fps 会把关键帧抽掉。镜头切换检测、或「帧间差异超过阈值就增加采样」比盲目加 fps 便宜。
- 长监控 / 会议回看：先低分辨率全局时间线，用户或模型圈出窗口再提高局部 $r$ 和空间分辨率。这和文档动态切块是同一思想，见 `google-vit-patch`。

抽样一旦进评测集就必须冻结。换 fps 等于换题：分数涨了不知道是模型还是多看了 3 倍帧。Gemini 报告里的视频能力，对比时要对齐抽样协议，不要和自家更高 fps 的私有集比。

位置编码要时空：帧索引 + 帧内 2D。纯 1D 词位置会把相邻帧的右上角连成「下一个词」。长视频再叠加和文本同一套窗口偏差：中间一小时更容易丢，见 `google-gemini-longctx` 的位置切片。

默认不该是「整段视频原样进 1M」。和文本一样，检索或分段摘要常常在更短 $T$ 上赢。正当用途是：必须同时看见多段画面才能答（实验步骤、剧情因果）、以及检索会漏的视觉证据（图上的数字、未进 ASR 的动作）。

实际分配窗口时，我会先留用户问题和系统约束，再留音频 / ASR，再留稀疏关键帧，最后才是均匀填满的剩余帧。反了就会出现「窗口满了，问题被截断」。工具环里每步新截图也是视频的离散版，旧帧要丢或摘要，否则 agent 自己把窗口吃光。

常见误区是：把一段视频说成 1 个 token；说有 1M 窗口所以 30 fps 4K 随便喂；评测不公布 fps 还横向比。

Decode 侧：输入预填充（prefill，即处理输入并建立缓存） 已经付了 $T_{\mathrm{vid}}$ 的二次项注意力；逐 token 生成（decode） 每步读整段 KV。视频把 $T$ 抬高后，GQA / 量化 cache 与文本长上下文使用相同的优化方法，见 `google-gqa-mqa`、`google-tpu-decode`。

## 追问

**关键帧检测错了怎么办？**
当召回问题：漏检用均匀兜底稀疏网格补；误检只浪费预算。安全相关任务宁可多抽。

**多镜头、画中画怎么算 $F$？**
按合成画面抽，另加裁剪轨如果产品要。单轨均匀抽会把小窗里的人脸抽成几个糊点。

**为什么还要 ASR？**
音频 token 和视觉 token 互补。纯视觉在低 fps 下听不见论点；纯 ASR 看不见板书。交错才是 Gemini 的公开卖点。

**和 Flamingo 逐帧 resample 怎么选？**
要细节、要 OCR，少压缩拼接；只要场景级描述，固定 latent 更省窗口。
