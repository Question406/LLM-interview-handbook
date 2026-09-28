---
id: meta-llama-rope
section: meta
order: 9
level: A
title: Meta：Llama 的 RoPE / 长上下文外推（NTK、YaRN 只需概念层）面试怎么讲
quick: >-
  RoPE 在偶数维两两旋转，$q_m^\top k_n$ 只依赖相对位移 $n-m$。训练长度之外高频相位没见过，直接拉长会糊。Llama 3.1
  公开配置是继续训长窗并提高 `rope_theta`。NTK / YaRN 是社区外推旋钮：保高频、放低频，不要说成 Meta 官方配方。
tags:
  - Meta
  - Llama
  - RoPE
  - Long Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: YaRN — Efficient Context Window Extension of Large Language Models
    url: https://arxiv.org/abs/2309.00071
    type: secondary
  - title: Introducing Llama 3.1
    url: https://ai.meta.com/blog/meta-llama-3-1/
    type: primary
---

Llama / 推理岗常把 RoPE 和长上下文放在一道题里。公式要能写，外推不要背成「把 `max_position_embeddings` 改大」。GQA 省 KV 带宽（`meta-llama-gqa`）和 RoPE 正交：一个切 $H_{kv}$，一个切位置相位。

## RoPE 在编码什么

偶数维两两分组，位置 $m$ 的 query / key 乘旋转矩阵 $R_{\theta,m}$。关键恒等式：

$$
(R_{\theta,m} q)^\top (R_{\theta,n} k) = q^\top R_{\theta,n-m} k
$$

score 只依赖相对位移 $n-m$。第 $i$ 对频率 $\theta_i = \theta_{\mathrm{base}}^{-2i/d}$：低频管长距，高频管近距。$V$ 通常不转：位置交互主要由 $QK$ 决定。绝对位置仍在单个 $q_m$ 里，只是点积有干净的相对结构。和 KV cache 兼容：decode 时用 `cache_len` 当 $m$，不要每步都从 $0$ 转。

Llama 2 预训练上下文 $4\mathrm{k}$；Llama 3 博客写预训练 $8\mathrm{k}$；Llama 3.1 / 3.2 把窗口做到 $128\mathrm{k}$。公开 conf 里常见把 `rope_theta` 从 $10^4$ 提到 $5\times 10^5$ 量级，这是**改基频**，不是换一套位置编码。

## 外推为什么难，三条概念旋钮

训练只见过有限相位。$m$ 一过训练长度，高频通道转进没见过的区间，注意力模式 OOD。所以「推理时把窗口改成 128k」不等于模型会用 128k。

社区三条路，面试停在概念层：

- **位置插值（PI）：** 把长窗位置压回训练尺度，$m' = m \cdot L_{\mathrm{train}} / L_{\mathrm{target}}$。实现便宜，近距分辨率变差（局部 token 被拉远）。
- **NTK-aware：** 提高 $\theta_{\mathrm{base}}$，让高频少转几圈、少进 OOD，低频去够更远。和 Llama 3.1 提高 `rope_theta` 是同一类直觉，但不要把开源 conf 说成 NTK 论文的官方实现。
- **YaRN：** 按频段混合插值和 NTK，并给注意力温度，减轻「近距也变糊」。是社区方法；**没有公开材料说 Llama 官方训练用了 YaRN**。现场说「同类旋钮，验收看长依赖任务」，不要编配方。

Meta 自己的长窗叙事更稳的是：**在目标长度上继续预训练 / 长窗 SFT**，再配合 GQA、tokenizer 压缩（`meta-llama3-tokenizer`）。针-in-haystack 只能说明还能点到远处某个 id，不能说明推理链还完整。

## 一个具体错法

错法：decode 时 RoPE 用当前位置 $0,1,2,\ldots$ 而 cache 里已经有 $S$ 个 token。正确是 $m = S, S+1, \ldots$。这和 OpenAI 风格的 Transformer debug 是同一类位置偏移，只是 Meta 面试更常挂在 Llama 配置上。

另一个错法：把 YaRN 的温度、NTK 的 $\alpha$、PI 的缩放三个开关同时拧，还不做消融。外推超参很脆，要在同一套长上下文 eval 上比，不能口头保证无损。

## 追问

- **为什么高频先坏？** $\theta_i$ 大时 $m\theta_i$ 随 $m$ 转得快，训练没见过的大 $m$ 上相位乱跳。
- **提高 theta 和插值能一起用吗？** 能，YaRN 就是分段组合。组合后更要测近距（复制、代码缩进）和远距（文档 QA），只报 haystack 不够。
- **和 ALiBi 的差别？** ALiBi 在 score 上加与距离成正比的偏置，外推叙事不同。Llama 族公开的是 RoPE，别现场把 Llama 说成 ALiBi。
- **128k 时 GQA 更重要吗？** 是。KV cache 跟 $T\cdot H_{kv}$ 走，$T$ 拉长后带宽更疼，见 `meta-llama-gqa`。
