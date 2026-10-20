---
id: google-vit-patch
section: google
order: 25
level: A
title: Google：ViT patch 和原生分辨率，token 数怎么爆、动态切块怎么压
quick: "视觉 token 数随分辨率变化，不是跟「一张图」走。$N=\\lfloor H/P\\rfloor\\lfloor W/P\\rfloor$，高清截图可以上万 patch。原生分辨率要保长宽比、2D 位置和 packing；动态切块是把大图拆进窗口，不是换一个模型名。"
tags:
  - Google
  - ViT
  - Patch
  - Resolution
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: An Image is Worth 16x16 Words (ViT)
    url: https://arxiv.org/abs/2010.11929
    type: primary
  - title: NaViT — Patch n' Pack
    url: https://arxiv.org/abs/2307.06304
    type: primary
  - title: FlexiViT — One Model for All Patch Sizes
    url: https://arxiv.org/abs/2212.08013
    type: primary
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: secondary
---

ViT 把图切成 $P\times P$ 的 patch，线性投进 Transformer。Google / Gemini 视觉岗问的是：**分辨率一涨，序列长度怎么爆，serving 窗口怎么收。** 原生多模态怎么和文本抢 $T$ 见 `google-gemini-mm`；视频再乘时间见 `google-video-token`。不是某次逐字真题。

## Token 账：跟 $H,W,P$ 走

一张图的 patch 数

$$
N=\bigl\lfloor H/P\bigr\rfloor\cdot\bigl\lfloor W/P\bigr\rfloor
$$

口算要对着产品图，不要对着 ImageNet 224。$224$、$P=16$ 大约 $14\times 14=196$，再加分类标记也才两百出头。边长 768、$P=16$ 就是 $48\times 48=2304$。一张 $1920\times 1080$ 的 UI 截图、$P=14$，大约 $137\times 77\approx 1.05\times 10^4$。这还没算多张图、没算视频帧。Gemini 式解码器里这些 patch 和文本占同一条因果链，窗口成本见 `google-gemini-longctx`。

三种办法，各有取舍：

- 降 $H,W$：风景图、幻灯片背景可以狠压；图标、公式、表、小字会先糊。
- 加大 $P$：同样分辨率 $N$ 按 $1/P^2$ 掉。FlexiViT 一类用可缩放的 patch 嵌入，让同一套权重切几种 $P$。细节任务 $P$ 太大等于没看见笔画。
- 压缩 / 重采样：把 $N$ 收成固定 $N_{\mathrm{lat}}$，Flamingo 走这条，见 `google-flamingo`。

常见误区是：说「一张图一个视觉 token」；说原生分辨率所以 $N$ 是常数；把所有图 pad 成正方形再 resize，长条截图被挤扁，还会为黑边消耗 token 预算。

```python
def n_patches(h, w, p):
    return (h // p) * (w // p)

def pack_counts(sizes, p, t_max):
    packs, cur, used = [], [], 0
    for h, w in sizes:
        n = n_patches(h, w, p)
        if cur and used + n > t_max:
            packs.append(cur)
            cur, used = [], 0
        cur.append(n)
        used += n
    if cur:
        packs.append(cur)
    return packs
```

## 原生分辨率：长宽比、2D 位置、packing

训练若永远 224 正方形，推理喂 4:3 文档页，位置编码和注意力统计都会漂。NaViT 的公开做法是 Patch n' Pack：按原图长宽比切 patch，不同分辨率的图 pack 进同一条序列，注意力用块对角 mask，避免图和图互相看。位置用可插值的二维编码（或分解成 $x,y$），不要假设序列下标等于从左到右的词位置。

Shape 口头报：单图 $[N, D]$，pack 之后 $[B_{\mathrm{pack}}, T_{\mathrm{pack}}, D]$，其中 $T_{\mathrm{pack}}\le T_{\max}$，一个 pack 里可能有好几张图。$B_{\mathrm{pack}}$ 往往是 1 再靠 pack 提高 MXU 利用率，和文本 packing 是同一类编译友好技巧。TPU 讨厌动态 $N$，XLA 会 pad 到静态上限，见 `google-tpu-llm`。你不 pad，编译器也会，浪费写在 padding 上。

实现上我会钉三件事：pad 到 $P$ 的倍数、2D 坐标跟 patch 走而不是跟 pad 后画布走、pack 边界写进 mask。坐标写错，模型会把两张图的右下角当成一张图的中间。

## 动态切块：窗口，不是新骨架

文档、海报、4K 截图，$N$ 直接进百万窗口也会耗尽 KV 缓存预算。产品默认应切块：

1. 先喂一张低分辨率全局图，解决「这页大概是什么」。
2. 再按版面 / 显著性 / 用户框选出若干 $S\times S$ 窗口（可重叠），每块独立切 patch。
3. 块与块之间加 2D 偏移，告诉模型它们在原图哪。需要读表、对单元格时窗口要密；只问主题可以只留全局。

这和「换一个更大的 ViT」不是一回事。切块的失败模式是跨块推理：答案在表的左上和右下，两块没同时进窗口。评测要带跨块题，不要只报单块 VQA。和 OCR 还是像素的取舍仍按错误类型，见 `google-gemini-mm`，这里不重复。

面试把「可变分辨率」收成 packing、2D 位置、可选切块；并解释它们分别解决什么问题。

## 追问

- **$P$ 能不能推理期再改？** FlexiViT 说明 patch 嵌入可以插值。改了必须在小字 / OCR 切片上重测，不能只看 ImageNet。
- **多图对话怎么 pack？** 按轮次拼，图与对应那句用户话靠近；整段聊天所有图丢进一个包，指代会乱。
- **和连接器投影的差别？** 连接器是冻 ViT 再线性到 LM 维。Gemini 公开叙事是视觉 token 进同一条解码器。token 数爆炸这件事两边都在，压缩策略不同。
- **为什么正方形 resize 是错默认？** 长条 UI、收据、双栏 PDF 会被压扁；黑边 pad 还占 $N$。原生长宽比更便宜也更不伤布局。
