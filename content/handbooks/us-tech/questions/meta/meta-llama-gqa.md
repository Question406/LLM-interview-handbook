---
id: meta-llama-gqa
section: meta
order: 1
level: A
title: Meta / Llama：为什么 70B 用 GQA？和 MHA 比 decode 省在哪？
quick: >-
  Llama 2 70B 公开配置是 $32$ 个 query head、 $8$ 个 KV head。KV cache 大约降到 MHA 的 $1/4$，decode
  带宽跟着降。质量用 grouped 的 KV 保住，不走到 MQA 的极端共享。这是 Meta 推理岗的默认开口。
tags:
  - Meta
  - Llama
  - GQA
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

Meta GenAI / Llama 岗很少问「GQA 的全称」，会问你 70B 为什么不继续用满头 KV。公式和选型见 `arch-gqa` 和 `google-gqa-mqa`。本题按 Llama 2 论文的公开配置收。

## 70B 的账

Llama 2 70B：隐藏维 $8192$，$32$ query heads，所以 $d_{\mathrm{head}}=256$。GQA 把 KV head 收到 $8$ 组，每组 $4$ 个 query head 共享。KV cache：

$$
2 \cdot L \cdot T \cdot H_{\mathrm{kv}} \cdot d_{\mathrm{head}} \cdot \mathrm{bytes}
$$

$H_{\mathrm{kv}}$ 从 $32$ 变 $8$，cache 和 decode 读带宽大约 $\times 1/4$。Decode 每步几乎不算大 GEMM，时间砸在读历史 KV 上，所以这个 $1/4$ 是墙钟，不只是显存表上的数。

MQA（$H_{\mathrm{kv}}=1$）还能再省 $8$ 倍，但 70B 这种质量敏感的对话模型，Meta 选了 GQA。论文明确写 GQA 是为了在不显著掉质量的前提下加快推理。不要答成「GQA 一定比 MHA 准」。

## 训练和推理要对齐

Llama 2 是 **训练时就是 GQA**，不是 MHA 训完再 merge。现场若问「能不能 MHA 训、GQA 推」，可以，GQA 论文给了 mean-pool 初始化，但有转换误差，要在同一套 eval 上量，不能口头保证无损。

实现：attention 里 $K,V$ 是 `[B, 8, S, 256]`，$Q$ 是 `[B, 32, S, 256]`。要么把 KV repeat 4 次，要么走 GQA kernel。repeat 发生在计算时，cache 里仍存 $8$ 组。把 cache 存成 $32$ 组，等于把省下来的带宽又花回去。

长上下文（Llama 3 的 128k）把 $T$ 拉大之后，GQA 的相对收益更大。再往后是量化 KV 和 paging，那是系统题，见 `sys-quant`。

## 追问

- **8 这个数怎么来的？** 公开论文没把搜索过程写死。面试答：在 $1$ 和 $H_q$ 之间扫，$8$ 是质量和带宽的工作点。不要编造「必须是 $4$ 的幂」除非你做过消融。
- **和 MoE 专家并行冲突吗？** 不直接冲突。GQA 改的是注意力 KV；MoE 改的是 FFN 路由。显存上两者叠加，需要一起算。
- **Llama 4 / 后续还用 GQA 吗？** 以当时公开技术报告为准。原理不变：decode 带宽跟 $H_{\mathrm{kv}}$ 走。
