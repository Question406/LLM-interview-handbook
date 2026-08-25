---
id: meituan-rmsnorm-vs-ln
section: arch
order: 160
level: A
title: 美团：RMSNorm 相对 LayerNorm 有何优势，公式是什么？
quick: >-
  LayerNorm 减均值再除标准差并仿射；RMSNorm 只除均方根，不做中心化。少一次均值，算得更快，大模型里通常够稳。偏好来自效率与实践，不是数学上严格更优。
tags:
  - Meituan
  - RMSNorm
  - LayerNorm
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
- 团队 / 岗位：大模型算法秋招
- 届别 / 流程：秋招；二面
- 面试时间：原帖未披露；帖子发布于 2025-12-18
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“RMSNorm相较于LayerNorm有什么优势？公式是什么？”**

这块容易把 RMSNorm 说成「数学上严格更优的 LayerNorm」。它少做中心化，算得更快、带宽更友好；大模型实践里通常够稳，不是定理保证处处更强。公式必须能手写。同场常接着问 SwiGLU，两套要一起写。

## 公式

LayerNorm 减均值再除标准差，再仿射：

$$
\mathrm{LN}(x)=\gamma\odot\frac{x-\mu}{\sqrt{\sigma^2+\varepsilon}}+\beta,\quad
\mu=\mathrm{mean}(x),\;\sigma^2=\mathrm{mean}((x-\mu)^2).
$$

RMSNorm 只除均方根，常无 $\beta$：

$$
\mathrm{RMSNorm}(x)=\gamma\odot\frac{x}{\sqrt{\mathrm{mean}(x^2)+\varepsilon}}.
$$

少一次均值和一次同步，kernel 更简单。LLaMA / Qwen 系普遍采用。Pre-Norm 结构里，它挡在注意力和 SwiGLU 前面，把激活尺度稳住，再进 $QK^\top$ 或门控 $\mathrm{SiLU}(xW_1)\odot xW_2$。RoPE 加在 Norm 之后的 $q,k$ 上，Norm 不编码位置。

## 优势是效率与实践，不是换掉残差哲学

代价是没有显式中心化：若某层激活带很大偏置，LN 会先拔掉，RMSNorm 只按能量缩放。极少数任务可能不同，但后训练里几乎不因此换回 LN。面试别说「RMSNorm 一定收敛更好」；说「在 decoder-only + Pre-Norm 上被验证够用，且省一点算力和实现复杂度」。

MoE 路由看的是 Norm 后的 $x$，负载不均不是 RMSNorm 造成的，不要把 aux loss 和 Norm 选型绑死。后端岗甚至出现过 CUDA 手撕 RMSNorm，要能写 fused 的 rsqrt。

## 追问

- **$\gamma$ 能省吗？** 多数实现保留，用来恢复层间尺度；省 $\beta$ 更常见。
- **和 BatchNorm 比？** BN 依赖 batch 统计，NLP 变长序列不稳定；LN / RMS 沿特征维，与 batch 无关。
- **手写时 $\varepsilon$ 放哪？** 放进均方根再 rsqrt，避免全零向量除零；不要先开方再加 $\varepsilon$ 到外面。
