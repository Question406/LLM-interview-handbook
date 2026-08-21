---
id: meituan-swiglu
section: arch
order: 180
level: A
title: 美团秋招二面：SwiGLU 的公式是什么，相对 ReLU / GELU 强在哪？
quick: >-
  FFN 里两路线性：$(\mathrm{SiLU}(xW)\odot xV)W_o$。门控让模型学会放行多少信息，SiLU
  平滑非单调；参数大约是两矩阵 FFN 的 1.5 倍，所以中间维常按 $8d/3$ 对齐算力。
tags:
  - Meituan
  - SwiGLU
  - FFN
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

陷阱是把 SwiGLU 说成「就是 GELU 换了个名字」，或漏写门控那一路。它是 FFN 里的**乘性门控**：一路决定放行多少，一路提供内容。Qwen 系常用这套；同面还会问 RMSNorm，两套要能一起写。

## 公式与参数量

$$
\mathrm{SwiGLU}(x)=(\mathrm{SiLU}(xW_1)\odot xW_2)W_3,\qquad
\mathrm{SiLU}(z)=z\cdot\sigma(z).
$$

普通两矩阵 FFN 是 $\sigma(xW_1)W_2$。SwiGLU 多一块 $W_2$（gate），参数约 $3dd_{\mathrm{ff}}$。为了对齐算力，中间维常取 $d_{\mathrm{ff}}\approx 8d/3$ 再按硬件对齐，而不是照搬 $4d$。SiLU 在负半轴仍有梯度，不像 ReLU 死区那么硬；相对单路 GELU，多一个可学习门，表达更灵活。

位置编码不在这里：RoPE 作用在注意力的 $q,k$ 上，$q^\top R_{n-m}k$。MoE 只是把上述 FFN 复制成专家 $E_i$，路由 $y=\sum_{i\in\mathrm{top}k}g_i E_i(x)$，专家内部仍可以是 SwiGLU。

## 相对 ReLU / GELU 强在哪、代价是什么

强在门控：同一位置可以对不同通道选择抑制或放大，而不是共用一个逐元非线性。代价是多一块投影，参数与激活显存上升；若 $d_{\mathrm{ff}}$ 不往回收，层会明显更贵。没有「SwiGLU 定理上必优于 GELU」——是大规模 decoder-only 上的经验选择。面试补一句：Norm 用 RMSNorm 稳住尺度，再进门控，学习率才好调。

## 追问

- **GLU、SwiGLU、GeGLU 差在哪？** 门的非线性分别是 sigmoid / SiLU / GELU，结构都是「门 $\odot$ 值」。
- **为什么是 $8d/3$？** 三矩阵要对齐原先两矩阵 $\times 4d$ 的 FLOPs：$3d\cdot(8d/3)=8d^2$，与 $2d\cdot 4d$ 同阶。
- **能手写 PyTorch 吗？** `silu(x @ W1) * (x @ W2)` 再 `@ W3`；不要先 cat 再切错维。
