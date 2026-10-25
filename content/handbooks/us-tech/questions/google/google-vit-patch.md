---
id: google-vit-patch
section: google
order: 25
level: A
title: Google：ViT patch 和原生分辨率，token 数怎么爆、动态切块怎么压
quick: "ViT 的 patch 数约为 $N=\\lfloor H/P\\rfloor\\lfloor W/P\\rfloor$，分辨率越高，视觉序列越长。要保留小字和布局，可以保长宽比、使用二维位置和 packing，再按需要对高清图动态切块；降低分辨率或加大 patch 则会牺牲细节。"
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

ViT 把图像切成 $P\times P$ 的 patch，再把每块线性投影成 token；图越高清，序列就越长。比如 UI 截图里的小字需要保留分辨率，却可能一张图就占上万 patch，所以要结合任务选择缩放、压缩或切块。这张卡是机制题，非逐字真题；多模态共享同一条 $T$ 的预算，见 `google-gemini-mm`，视频时间维见 `google-video-token`。

给定 $H,W,P$，一张图的 patch 数是

$$
N=\bigl\lfloor H/P\bigr\rfloor\cdot\bigl\lfloor W/P\bigr\rfloor
$$

算预算时要用实际产品图片的分辨率。$224$、$P=16$ 大约 $14\times 14=196$，再加分类标记也才两百出头。边长 768、$P=16$ 就是 $48\times 48=2304$。一张 $1920\times 1080$ 的 UI 截图、$P=14$，大约 $137\times 77\approx 1.05\times 10^4$。这还没算多张图、没算视频帧。Gemini 式解码器里这些 patch 和文本占同一条因果链，窗口成本见 `google-gemini-longctx`。

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

训练若永远 224 正方形，推理喂 4:3 文档页，位置编码和注意力统计都会漂。NaViT 的公开做法是 Patch n' Pack：按原图长宽比切 patch，不同分辨率的图 pack 进同一条序列，注意力用块对角 mask，避免图和图互相看。位置用可插值的二维编码（或分解成 $x,y$），不要假设序列下标等于从左到右的词位置。

从张量形状看，单图 $[N, D]$，pack 之后 $[B_{\mathrm{pack}}, T_{\mathrm{pack}}, D]$，其中 $T_{\mathrm{pack}}\le T_{\max}$，一个 pack 里可能有好几张图。$B_{\mathrm{pack}}$ 往往是 1 再靠 pack 提高 MXU 利用率，和文本 packing 是同一类编译友好技巧。TPU 讨厌动态 $N$，XLA 会 pad 到静态上限，见 `google-tpu-llm`。你不 pad，编译器也会，浪费写在 padding 上。

实现时我会检查：pad 到 $P$ 的倍数、2D 坐标跟 patch 走而不是跟 pad 后画布走、pack 边界写进 mask。坐标写错，模型会把两张图的右下角当成一张图的中间。

文档、海报、4K 截图，$N$ 直接进百万窗口也会耗尽 KV 缓存预算。产品默认应切块：

1. 先喂一张低分辨率全局图，解决「这页大概是什么」。
2. 再按版面 / 显著性 / 用户框选出若干 $S\times S$ 窗口（可重叠），每块独立切 patch。
3. 块与块之间加 2D 偏移，告诉模型它们在原图哪。需要读表、对单元格时窗口要密；只问主题可以只留全局。

这和「换一个更大的 ViT」不是一回事。切块的失败模式是跨块推理：答案在表的左上和右下，两块没同时进窗口。评测要带跨块题，不要只报单块 VQA。和 OCR 还是像素的取舍仍按错误类型，见 `google-gemini-mm`，这里不重复。

这样，packing 减少补齐浪费，二维位置保留布局，切块控制单次输入预算，分别对应不同问题。

## 追问

**$P$ 能不能推理期再改？**
FlexiViT 说明 patch 嵌入可以插值。改了必须在小字 / OCR 切片上重测，不能只看 ImageNet。

**多图对话怎么 pack？**
按轮次拼，图与对应那句用户话靠近；整段聊天所有图丢进一个包，指代会乱。

**和连接器投影的差别？**
连接器是冻 ViT 再线性到 LM 维。Gemini 公开叙事是视觉 token 进同一条解码器。token 数爆炸这件事两边都在，压缩策略不同。

**为什么正方形 resize 是错默认？**
长条 UI、收据、双栏 PDF 会被压扁；黑边 pad 还占 $N$。原生长宽比更便宜也更不伤布局。
