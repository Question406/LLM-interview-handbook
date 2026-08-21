---
id: baichuan-rope-extrapolation
section: arch
order: 143
level: A
title: 百川智能：超长文本外推常见怎么做，RoPE 你怎么理解？
quick: >-
  RoPE 用旋转把相对位置编进 $QK$ 点积，外推不等于把 `max_position` 加大。常用插值、NTK / YaRN
  调频率、或训练时加长窗口；ALiBi 等偏置则是另一条外推路线。
tags:
  - Baichuan
  - RoPE
  - Long Context
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

陷阱是把 RoPE 外推说成「把 `max_position_embeddings` 改大就行」。RoPE 把相对位置编进点积，实现简单、和 KV cache 兼容，但**不保证**训练长度之外仍然准：高频分量在远距离会快速振荡，注意力分数失真。

## RoPE 在编码什么

对偶数维两两分组，位置 $m$ 的 query / key 乘旋转矩阵 $R_{\theta,m}$。关键恒等式

$$
(R_{\theta,m}q)^\top(R_{\theta,n}k)=q^\top R_{\theta,n-m}k,
$$

即 score 只依赖相对位移 $n-m$。第 $i$ 对频率 $\theta_i=10000^{-2i/d}$：低频管长距，高频管近距。这与 SwiGLU FFN、MoE 路由无关——位置在注意力侧，专家选择看的是内容 $x$，不是 $R_{\theta,m}$。

面试画一个 2D 旋转即可：同一相对位移，旋转差相同。绝对位置不显式出现在 score 里。

## 外推 / 加长常见几条路

- **位置插值（PI）**：把长窗位置压回训练尺度，相当于拉伸 $m$。实现便宜，远距分辨率变差。
- **NTK / YaRN**：调基频或按频段混合插值，尽量保住高频局部、放低频去够更远。
- **继续预训练 / 长窗 SFT**：在目标长度上真的见过 $T$，最稳，最贵。
- **换偏置**：ALiBi 用与距离成正比的线性偏置，外推叙事不同，和 RoPE 不是同一旋钮。

工程上还要配合分块注意力、检索、sink / 窗口，不能只改位置编码。验收必须用真实长依赖任务；针-in-haystack 只能说明「还能点到远处某个 id」，不能说明推理链仍完整。

## 追问

- **为什么高频先坏？** $\theta_i$ 大时 $m\theta_i$ 随 $m$ 转得快，训练没见过的大 $m$ 上相位乱跳。
- **YaRN 和直接插值差在哪？** 插值一视同仁压所有频率；YaRN 按频段区别对待，减少「近距也变糊」。
- **加长后 MoE 要不要重训路由？** 序列变长，专家负载统计会变，aux / bias 可能要再看 overflow，但那是路由问题，不是 RoPE 公式变了。
