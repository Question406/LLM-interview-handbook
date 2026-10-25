---
id: baichuan-rope-extrapolation
section: arch
order: 143
level: A
title: 百川智能：超长文本外推常见怎么做，RoPE 你怎么理解？
quick: "RoPE 用旋转把相对位置编进 $QK$ 点积，外推光把 `max_position` 调大不够。常见做法是位置插值、NTK / YaRN 调频率，或者在更长的窗口上继续训练；ALiBi 这类距离偏置是另一条外推路线。"
tags:
  - Baichuan
  - RoPE
  - Long Context
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“有了解过最近那些超长文本大模型的预训练吗？”**；**“常见的提高外推能力的方式”**；**“讲一下你对旋转位置编码的理解”**

外推常见的做法有三类：位置插值、用 NTK / YaRN 调频率，以及在更长窗口上继续训练；ALiBi 一类偏置是另一条路线。只把 `max_position_embeddings` 改大是不够的。RoPE 把相对位置编进点积，实现简单，也和 KV cache 兼容，但它不保证训练长度之外还准：高频分量在远距离振荡得很快，模型没见过那些相位，注意力分数就会失真。

## RoPE 在编码什么

把偶数维两两分组，位置 $m$ 的 query / key 乘上旋转矩阵 $R_{\theta,m}$。关键是这个恒等式：

$$
(R_{\theta,m}q)^\top(R_{\theta,n}k)=q^\top R_{\theta,n-m}k,
$$

也就是说，score 只依赖相对位移 $n-m$。第 $i$ 对的频率是 $\theta_i=10000^{-2i/d}$，低频管远距离，高频管近距离。面试时画一个 2D 旋转就够了：同样的相对位移，旋转角度差也相同，绝对位置不会显式出现在 score 里。

这和 SwiGLU FFN、MoE 路由都无关。位置在注意力这一侧，专家选择看的是内容 $x$，跟 $R_{\theta,m}$ 没关系。

## 外推和加长的几条路

最便宜的是位置插值（PI）：把长窗口里的位置压回训练时的尺度，相当于把 $m$ 拉伸，代价是远距离的分辨率变差。NTK / YaRN 改的是基频，或者按频段混合插值，尽量保住高频分量对局部位置的区分能力，同时让低频分量适应更远的距离。最稳也最贵的是在目标长度上继续预训练或做长窗监督微调（SFT），让模型真的见过这么长的 $T$。ALiBi 换了一种做法，用和距离成正比的线性偏置，外推的道理不一样，和 RoPE 不是同一个旋钮。

工程上还要配合分块注意力、检索、sink / 窗口，光改位置编码不够。验收要用真实的长依赖任务。针-in-haystack 只能说明模型还能点到远处的某个 id，说明不了推理链仍然完整。

## 追问

**为什么高频先坏？**
$\theta_i$ 大的时候，$m\theta_i$ 随 $m$ 转得很快，到了训练没见过的大 $m$，相位就乱跳。

**YaRN 和直接插值差在哪？**
插值对所有频率一视同仁地压；YaRN 按频段区别对待，减少「近距离也变糊」的问题。

**上下文加长后，MoE 要不要重训路由？**
序列变长后专家负载的统计会变，aux / bias 可能要重新看 overflow。但那是路由的问题，RoPE 的公式没变。
