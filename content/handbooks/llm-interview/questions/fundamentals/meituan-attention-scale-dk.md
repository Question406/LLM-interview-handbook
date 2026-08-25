---
id: meituan-attention-scale-dk
section: fundamentals
order: 140
level: A
title: 美团：Attention 为什么要除以 $\sqrt{d_k}$？
quick: >-
  $QK^\top$ 的坐标方差随 $d_k$ 线性增大，不缩放时 softmax 会进入饱和区，梯度消失。除 $\sqrt{d_k}$
  把点积标准差拉回常数级，训练才稳。这是数值稳定，不是「除掉一个维度」。
tags:
  - Meituan
  - Attention
  - Softmax
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary-paper
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Attention机制中为什么需要去除DK相关计算维度，核心作用是什么？”**

这块容易把原帖的「去除 $d_k$ 相关计算维度」理解成删掉某一轴，或背「除一下比较好」却不会推方差。核心是 **数值稳定**：点积尺度随维度变大，softmax 饱和，梯度消失。这不是「除掉一个维度」。QKV 来源见 `baichuan-attn-vs-selfattn`；矩阵形状见 `ali-attention-math`；softmax 饱和见 `fund-softmax-nll`。手写时写 `q @ k.T / math.sqrt(d_k)`（`pdd-attention-handwrite`）。FlashAttention 的 online softmax 不改变这个缩放（`ant-flash-attention`）。

## 方差怎么来的

设 $q,k\in\mathbb{R}^{d_k}$，各维独立、均值为 $0$、方差约 $1$，则

$$
\mathrm{Var}(q\cdot k)=\mathrm{Var}\Big(\sum_{i=1}^{d_k}q_i k_i\Big)=d_k,
$$

标准差约 $\sqrt{d_k}$。$d_k$ 到 $64$ 或 $128$ 时，点积绝对值经常很大。Softmax $e^{z_i}/\sum e^{z_j}$ 在 $z$ 差距大时接近 one-hot：最大项概率 $\approx 1$，其余 $\approx 0$，对非最大 key 的梯度几乎为 $0$，多层很难学到均匀一些的对齐。除以 $\sqrt{d_k}$ 后点积方差回到 $O(1)$，注意力还能在多个 key 上分配质量。

这与温度 $T$ 同类：$\mathrm{softmax}(z/T)$ 里 $T$ 变大等价于压平；$\sqrt{d_k}$ 是按维度选的固定温度，不是训练超参。QK-Norm 把 $q,k$ 先拉回单位尺度，是同一家族的稳定手段，可与除 $\sqrt{d_k}$ 并存。

## 怎么对原帖用词

「去除 $d_k$ 相关计算维度」应对成：用 $d_k$ 做缩放因子，而不是从张量里删掉该轴。Multi-head 里每个 head 的 $d_k=d_{\mathrm{model}}/h$，缩放用的是 **head 维度**，不是 $d_{\mathrm{model}}$。拼多多也常问同一点，公式要能白板推，不要只背结论。

失败模式：把缩放说成「除一下让数值变小好看」；用 $d_{\mathrm{model}}$ 而不是 $d_k$ 做分母；认为 FlashAttention 可以省略缩放。

## 和温度、QK-Norm、实现细节

Softmax 饱和是同一件事的不同旋钮。推理温度 $T$ 把 logits 除以 $T$；结构上的 $\sqrt{d_k}$ 相当于按维度选好的固定温度，保证训练时点积的典型尺度不随 head 变宽而漂移。QK-Norm 先把 $q,k$ 拉到单位尺度，再点积，对超稳定训练有帮助，但不替代论文里的缩放，两者可叠加。FlashAttention 用 online softmax 减显存，数学上仍是同一个 $\mathrm{softmax}(QK^\top/\sqrt{d_k})$，内核融合不是省略除法（`ant-flash-attention`）。

Multi-head 里每个 head 的维度是 $d_k=d_{\mathrm{model}}/h$，点积在 head 内做，所以分母是 $\sqrt{d_k}$ 不是 $\sqrt{d_{\mathrm{model}}}$。若把「去除 $d_k$ 相关计算维度」理解成 reshape 掉一轴，应对成「用 $d_k$ 做缩放因子」。实现里常见写法 `scores = q @ k.transpose(-2,-1) * (d_k ** -0.5)`，有人把系数预计算进 $W_Q$ 的初始化，效果等价，但白板仍应写出除 $\sqrt{d_k}$。拼多多手写题会查你是否漏掉这一项（`pdd-attention-handwrite`）。

若不缩放：深层的注意力迅速变 one-hot，残差学的是几乎离散的路由，梯度穿过 softmax 变得极小，训练表现为 loss 难降或对位置极敏感。这是优化问题，不只是 fp16 overflow。

## 追问

- **不除会怎样？** Softmax 变尖、梯度消失、深层对齐学不成，不是单纯 overflow。
- **和温度、QK-Norm 什么关系？** 都在管点积进入 softmax 前的尺度；温度是推理旋钮，缩放是结构常数。
- **$d_k$ 还是 $d_{\mathrm{model}}$？** 每个 head 的点积维度是 $d_k$。
- **FlashAttention 还要除吗？** 要。它加速的是实现，不改公式。
- **原帖「去除维度」怎么圆？** 说成用 $d_k$ 缩放，不是删轴；再补一句方差推导，比争用词更稳。
