---
id: meituan-swiglu
section: arch
order: 180
level: A
title: 美团秋招二面：SwiGLU 的公式是什么，相对 ReLU / GELU 强在哪？
quick: "SwiGLU 在 FFN 里用两路线性：$(\\mathrm{SiLU}(xW)\\odot xV)W_o$，一路当门决定放行多少，一路提供内容，SiLU 又平滑、非单调。它的参数大约是两矩阵 FFN 的 1.5 倍，所以中间维常取 $8d/3$ 来对齐算力。"
tags:
  - Meituan
  - SwiGLU
  - FFN
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法二面-秋招面经
    url: https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；二面
- 面试时间：原帖未披露；帖子发布于 2025-12-18
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“SwiGLU的公式是什么？”**

SwiGLU 是 FFN 里的乘性门控：一路决定放行多少，一路提供内容，两路逐元素相乘后再投影回去。它比 ReLU / GELU 强在这个门，同一个位置可以对不同通道分别抑制或放大。所以它和「GELU 换了个名字」差得很远，写公式时门控那一路不能漏。Qwen 系常用这套，同一场面试还会问 RMSNorm，两套要能一起写。

## 公式和参数量

$$
\mathrm{SwiGLU}(x)=(\mathrm{SiLU}(xW_1)\odot xW_2)W_3,\qquad
\mathrm{SiLU}(z)=z\cdot\sigma(z).
$$

普通两矩阵 FFN 是 $\sigma(xW_1)W_2$。SwiGLU 多了一块 $W_2$（gate），参数大约 $3dd_{\mathrm{ff}}$。为了对齐算力，中间维常取 $d_{\mathrm{ff}}\approx 8d/3$，再按硬件对齐，并不照搬 $4d$。SiLU 在负半轴仍有梯度，没有 ReLU 死区那么硬；和单路 GELU 相比，多了一个可学习的门，表达更灵活。

位置编码不在这里。RoPE 作用在注意力的 $q,k$ 上，$q^\top R_{n-m}k$。MoE 只是把上面这个 FFN 复制成多个专家 $E_i$，路由是 $y=\sum_{i\in\mathrm{top}k}g_i E_i(x)$，专家内部仍然可以是 SwiGLU。

## 强在哪，代价是什么

强在门控：每个通道可以单独选择抑制或放大，用不着共用同一个逐元素非线性。代价是多一块投影，参数和激活显存都会上升；如果不缩小 $d_{\mathrm{ff}}$，这一层的计算开销会明显增加。也没有「SwiGLU 在理论上必然优于 GELU」这种定理，它是大规模 decoder-only 上的经验选择。面试可以补一句：前面用 RMSNorm 把尺度稳住再进门控，学习率才好调。

## 追问

**GLU、SwiGLU、GeGLU 差在哪？**
差在门的非线性，分别是 sigmoid、SiLU、GELU。结构都是「门 $\odot$ 值」。

**为什么是 $8d/3$？**
三块矩阵要对齐原来两块矩阵配 $\times 4d$ 的 FLOPs：$3d\cdot(8d/3)=8d^2$，和 $2d\cdot 4d$ 同阶。

**能手写 PyTorch 吗？**
能。`silu(x @ W1) * (x @ W2)` 再 `@ W3`。别先 cat 再切，容易切错维。
