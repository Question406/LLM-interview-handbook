---
id: "ml101-cnn"
section: "neural-networks"
order: 7
level: "A"
title: "卷积的参数共享、感受野和输出尺寸怎么计算？"
quick: "卷积核在不同空间位置复用同一组权重，所以参数量与输出图的像素数无直接乘法关系。输出尺寸由核、步幅、padding 和 dilation 决定；感受野要逐层累计，不能把参数共享理解成已经看见整张图。"
tags: ["ML101", "neural-networks"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "PyTorch: Conv2d"
    url: https://docs.pytorch.org/docs/2.14/generated/torch.nn.Conv2d.html
    type: primary
---

卷积用同一组局部滤波器扫描不同位置，因此能共享参数、提取重复出现的局部模式。普通二维卷积的权重数是 $C_{\mathrm{out}}C_{\mathrm{in}}k_hk_w$，若带偏置再加 $C_{\mathrm{out}}$，分组卷积还要按组数调整输入连接。 [PyTorch: Conv2d](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Conv2d.html)

一维方向的输出大小是 $\lfloor(H+2p-d(k-1)-1)/s+1\rfloor$，其中 $H$ 为输入长度、$p$ 为两侧各自 padding、$d$ 为 dilation、$k$ 为核大小、$s$ 为步幅。高和宽分别代入。比如 $32\times32$ 输入，$3\times3$ 核、步幅 1、padding 1，输出仍是 $32\times32$。

感受野表示某个输出在原输入上理论上能受哪些位置影响。两层 $3\times3$、步幅 1、无 dilation 的卷积，理论感受野是 $5\times5$。若前面有步幅，后续核跨越原图的距离更大，需要把前面累计的步幅一起算；理论覆盖范围也不等于各像素实际贡献一样大。

## 追问

**输入图变大，参数量也变大吗？**
相同通道和卷积配置下，卷积参数不变，输出数量、计算量和激活内存会变大。

**两个 $3\times3$ 等价于一个 $5\times5$ 吗？**
理论感受野相同，但中间若有非线性，表达和参数结构就不同。

**卷积保证平移不变吗？**
通常更接近平移等变，输入移动时特征随之移动；边界、padding 和步幅还会影响这种性质。
