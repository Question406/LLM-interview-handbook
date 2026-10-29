---
id: meituan-qwen3-vl-pos
section: multimodal
order: 180
level: A
title: 美团 27 暑期：Qwen3-VL 的位置编码方案要怎么讲？
quick: >-
  文本继续用 1D RoPE；视觉 token 带二维网格坐标，视频再加时间，动态分辨率下坐标随 patch 网格重算，不能固定假设 $H\times
  W$。Qwen3-VL 用 Interleaved M-RoPE，把时间、高、宽的频率交织后放进同一个 attention 里算。
tags:
  - Meituan
  - Qwen-VL
  - Positional Encoding
  - '2027'
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 美团27暑期大模型算法岗一二面面经
    url: 'https://www.nowcoder.com/feed/main/detail/9a1c96c6ac6c4d07b1bfc9cf3a6f2505'
    type: candidate-first-hand
  - title: Qwen3-VL Technical Report
    url: 'https://arxiv.org/abs/2511.21631'
    type: primary-paper
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：27 暑期；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：“介绍 Qwen3-VL 多模态模型的位置编码方案”

Qwen3-VL 用的是 Interleaved M-RoPE：每个 token 的位置是三元组 $(t,h,w)$，文本三轴取同一个下标，退化成普通 1D RoPE；视觉 token 用网格的行、列（视频再加时间）坐标；三轴的旋转频率交织分配，再放进同一个 attention 里算。相对 Qwen2 / 2.5-VL，主要变化是频率从分段改成了交织，视频里的时间则改用显式的时间戳 token 来对齐。

常见的错答是把视觉 token 当成一维句子做标准 RoPE，或者背一堆没公开的层数。具体的 head 切分数字，除非你读过当时的技术报告，否则别编；细节以 arXiv:2511.21631 为准。

白板上可以先画三个整数轴。图像 token 的 position id 是 $(t,h,w)$，同一帧里 $t$ 不变，$h,w$ 沿网格走；文本 token 是 $(n,n,n)$。举个例子，空间上左右相邻的两个 patch，$\Delta h=0,\Delta w=1$，旋转差很小；换成光栅扫描的 1D 序号，上下相邻的两个 patch 相距 $W$，旋转差完全是另一回事。「把价签框出来」依赖的是邻域关系，和「它是第 137 个视觉 token」无关，这就是 grounding 需要二维位置的原因。

## 文本、视觉、融合三层

文本用标准 RoPE。Qwen 系的 M-RoPE 对文本令 $t=h=w=$ 同一递增下标，退化回 1D，纯文本能力不会被视觉坐标打乱。

视觉的每个 patch 有行 / 列坐标，视频再加时间。Qwen2 / 2.5-VL 把旋转频率按维度切成 $t,h,w$ 三段，报告指出这种切法频谱不均，不利于长视频建模。Qwen3-VL 改成 interleaved M-RoPE，把 $t,h,w$ 交错写进高低频，让三轴都能用上低频。空间上相邻的 patch 旋转更接近，比光栅扫描的 1D 更利于 grounding / OCR 对位。

融合发生在 attention 里：视觉 token 投影进 LLM 的隐空间后，同一个 attention 同时看到文本位置和视觉网格位置。分辨率一变网格就变，坐标必须重算，不能复用固定 224 时的序号。

视频这边，Qwen3-VL 还把「用位置编码对齐绝对时间」改成了显式的时间戳 token，时钟不再全靠位置编码来承担。被追问时可以说「时间接地从 T-RoPE 走到了文本时间戳」，事件定位更像对齐到字面时间，不再是对齐到某个 RoPE 段。

## 动态分辨率和 grounding

高清图会切出更多 patch，1D 序号会把「同一物体换了尺寸」当成完全不同的句子位置；网格坐标方案只是改了 $H,W$ 的取值范围。网格坐标让上下左右可区分，字段框、价签、按钮点击才有几何意义。不过 token 预算仍然要控，位置编码再好，视觉序列把上下文占满了，OCR 也没地方放。

DeepStack 这类跨层视觉残差不增加上下文长度，和位置编码是另一条线，被问到再说，别主动堆名词；损失改成 $\sqrt{}$ token 平均也不属于位置编码。

美团如果追问点选 / 框选，就补上坐标空间的问题：模型输出的点要映射到当前网格对应的原图像素，固定的 224 画布不对。分辨率桶一变，后处理映射也要跟着变，否则 grounding 指标全是假的。这和桌面 GUI grounding 是同一个坑，逻辑像素和截图像素不是一回事。

## 追问

**文本三轴相同，会不会和图像冲突？**
不会。文本没有独立的 $h,w$ 语义，三轴同值就是 1D；图像三轴不同才编码出平面。真出冲突，多半是实现里 id 写错了，公式本身没问题。

**为什么要交织频率？**
分段 M-RoPE 几乎把低频都分给了某一轴，长程的时间建模会偏科；交织让 $t,h,w$ 都能用上低频。

**和可学习的绝对 2D 位置表比呢？**
位置表绑定固定的 $H\times W$。动态分辨率下 RoPE 外推更干净，也省掉一张随分辨率膨胀的表。

**坐标用相对格子还是绝对格子？**
实现上是把格子下标送进 RoPE，相对关系由旋转差体现，不需要再加相对偏置表。

**输出的目标框怎么对齐？**
按当前的 patch 网格反投影到原图。换了分辨率就要换映射，不能写死 224 的标定。
