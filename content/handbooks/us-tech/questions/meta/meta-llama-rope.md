---
id: meta-llama-rope
section: meta
order: 9
level: A
title: Meta：Llama 的 RoPE / 长上下文外推（NTK、YaRN 只需概念层）面试怎么讲
quick: "RoPE 把偶数维两两旋转，让 $q_m^\\top k_n$ 的位置作用只依赖相对位移 $n-m$。超出训练长度后，相位分布变化会影响注意力；Llama 3.1 的公开做法包括提高 `rope_theta` 和长窗续训，NTK / YaRN 则是要单独验证的社区方法。"
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

RoPE 通过旋转 query 和 key，让点积带上相对位置信息；扩长上下文时，还要处理训练范围之外的相位变化。比如 cache 已有 $S$ 个 token，新 token 的位置就应从 $S$ 接着算，若每步重置到零，位置关系会错。GQA 减少 $H_{kv}$、RoPE 调整位置相位，两者是独立的机制。

## RoPE 在编码什么

偶数维两两分组，位置 $m$ 的 query / key 乘旋转矩阵 $R_{\theta,m}$。关键恒等式：

$$
(R_{\theta,m} q)^\top (R_{\theta,n} k) = q^\top R_{\theta,n-m} k
$$

score 只依赖相对位移 $n-m$。第 $i$ 对频率 $\theta_i = \theta_{\mathrm{base}}^{-2i/d}$：低频管长距，高频管近距。$V$ 通常不转：位置交互主要由 $QK$ 决定。绝对位置仍在单个 $q_m$ 里，只是点积有干净的相对结构。和 KV cache 兼容：逐 token 生成（decode） 时用 `cache_len` 当 $m$，不要每步都从 $0$ 转。

Llama 2 预训练上下文 $4\mathrm{k}$；Llama 3 博客写预训练 $8\mathrm{k}$；Llama 3.1 / 3.2 把窗口做到 $128\mathrm{k}$。公开 conf 里常见把 `rope_theta` 从 $10^4$ 提到 $5\times 10^5$ 量级，这是**改基频**，不是换一套位置编码。

## 长上下文为什么还要训练和验证

训练只见过有限相位。$m$ 一过训练长度，高频通道转进没见过的区间，注意力模式 分布外数据（OOD，即与训练数据明显不同的数据）。所以「推理时把窗口改成 128k」不等于模型会用 128k。

社区常见的扩展方式有三类：

- **位置插值（PI）：** 把长窗位置压回训练尺度，$m' = m \cdot L_{\mathrm{train}} / L_{\mathrm{target}}$。实现便宜，近距分辨率变差（局部 token 被拉远）。
- **NTK-aware：** 提高 $\theta_{\mathrm{base}}$，让高频少转几圈、少进 OOD，低频去够更远。和 Llama 3.1 提高 `rope_theta` 是同一类直觉，但不要把开源 conf 说成 NTK 论文的官方实现。
- **YaRN：** 按频段混合插值和 NTK，并给注意力温度，减轻「近距也变糊」。是社区方法；**没有公开材料说 Llama 官方训练用了 YaRN**。应用到具体模型后，仍要用长依赖任务验收。

Meta 公开的长窗训练包括在目标长度上继续预训练 / 长窗监督微调（SFT），再配合 GQA、tokenizer 压缩（`meta-llama3-tokenizer`）。针-in-haystack 只能说明还能点到远处某个 id，不能说明推理链还完整。

实现时检查 decode 位置：cache 已有 $S$ 个 token，就应取 $m = S, S+1, \ldots$，不能重新用 $0,1,2,\ldots$。这类位置偏移会让长窗评测与配置看起来不一致。

YaRN 温度、NTK 的 $\alpha$ 和 PI 缩放也要分开消融，在同一套长上下文 eval 上比较。只改大 `max_position_embeddings`，或同时打开所有缩放开关，都不足以证明扩窗无损。

相关：`meta-llama-gqa`。

## 追问

**为什么高频先坏？**
$\theta_i$ 大时 $m\theta_i$ 随 $m$ 转得快，训练没见过的大 $m$ 上相位乱跳。
**提高 theta 和插值能一起用吗？**
能，YaRN 就是分段组合。组合后更要测近距（复制、代码缩进）和远距（文档 QA），只报 haystack 不够。
**和 ALiBi 的差别？**
ALiBi 在 score 上加与距离成正比的偏置，外推叙事不同。Llama 族公开的是 RoPE，别现场把 Llama 说成 ALiBi。
**128k 时 GQA 更重要吗？**
是。KV cache 跟 $T\cdot H_{kv}$ 走，$T$ 拉长后带宽更疼，见 `meta-llama-gqa`。

## 相关题

- [[meta-yarn-ntk]]：同样讲 NTK / YaRN 和提高 `rope_theta`，但把 PI、NTK、YaRN 各拧哪根旋钮展开了；两张卡大量重叠。
- [[openai-long-ctx-train]]：从训练侧讲：改基频、在长文档上续训、packing 要加文档 mask。
- [[coding-rope]]：RoPE 旋转的代码写法，decode 时位置取 cache 长度。
- [[coding-alibi]]：不用旋转的另一种位置编码，外推方式不同。
