---
id: meituan-rmsnorm-vs-ln
section: arch
order: 160
level: A
title: 美团：RMSNorm 相对 LayerNorm 有何优势，公式是什么？
quick: >-
  LayerNorm 先减均值、再除标准差、再做仿射；RMSNorm
  只除均方根，不做中心化。少算一次均值，所以更快，大模型里通常也够稳。大家偏爱它是因为效率和实践经验，数学上它并不严格更优。
tags:
  - Meituan
  - RMSNorm
  - LayerNorm
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 美团大模型算法二面-秋招面经
    url: 'https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177'
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法秋招
- 届别 / 流程：秋招；二面
- 面试时间：原帖未披露；帖子发布于 2025-12-18
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“RMSNorm 相较于 LayerNorm 有什么优势？公式是什么？”**

RMSNorm 的优势在效率：它不做中心化，只除均方根，少一次均值和一次同步，算得更快，对带宽也更友好，大模型实践里通常够稳。但这不是定理，它并非处处都比 LayerNorm 强。公式要能手写，同一场面试常接着问 SwiGLU，两套最好一起写出来。

## 公式

LayerNorm 先减均值，再除标准差，最后做仿射：

$$
\mathrm{LN}(x)=\gamma\odot\frac{x-\mu}{\sqrt{\sigma^2+\varepsilon}}+\beta,\quad
\mu=\mathrm{mean}(x),\;\sigma^2=\mathrm{mean}((x-\mu)^2).
$$

RMSNorm 只除均方根，通常也没有 $\beta$：

$$
\mathrm{RMSNorm}(x)=\gamma\odot\frac{x}{\sqrt{\mathrm{mean}(x^2)+\varepsilon}}.
$$

少了一次均值和一次同步，kernel 更简单，LLaMA / Qwen 系普遍采用。在 Pre-Norm 结构里，它放在 attention 和 SwiGLU 之前，先把激活尺度稳住，再进 $QK^\top$ 或者 gating $\mathrm{SiLU}(xW_1)\odot xW_2$。RoPE 加在 Norm 之后的 $q,k$ 上，Norm 本身不编码位置。

## 少了中心化，代价在哪

代价是没有显式的中心化。比如某一层的激活带着很大的偏置，LN 会先把均值减掉，RMSNorm 只按能量缩放。极少数任务上可能因此有差别，但后训练里几乎没人为这个换回 LN。面试别说「RMSNorm 一定收敛更好」，说「在 decoder-only + Pre-Norm 上验证过够用，还省一点算力和实现复杂度」。

MoE 路由看的是 Norm 之后的 $x$，负载不均和 RMSNorm 无关，别把 aux 损失（loss）和 Norm 的选型绑在一起。后端岗甚至出现过 CUDA 手撕 RMSNorm，要能写出 fused 的 rsqrt。

## 追问

**$\gamma$ 能省掉吗？**
多数实现会保留，用来恢复层间的尺度；省掉 $\beta$ 更常见。

**和 BatchNorm 比呢？**
BN 依赖 batch 统计，NLP 里序列长度不一，很不稳定；LN 和 RMSNorm 都沿特征维算，和 batch 无关。

**手写时 $\varepsilon$ 放在哪？**
放进均方根里再做 rsqrt，避免全零向量除零。别先开方，再把 $\varepsilon$ 加在外面。
