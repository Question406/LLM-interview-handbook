---
id: kuaishou-gqa-mqa-mla
section: arch
order: 142
level: A
title: 快手：除了 MHA，GQA / MQA / MLA 原理是什么？Decoder 的 QKV 从哪来？
quick: >-
  Decoder 自回归里 Q 来自当前 token，K/V 来自已生成前缀（含 cache）。MQA 共享一套 KV 头，GQA 分组共享，MLA
  用低秩联合压缩 KV。都是在质量与 KV 显存之间折中。
tags:
  - Kuaishou
  - GQA
  - KV Cache
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 快手日常实习大模型算法面经
    url: https://www.nowcoder.com/feed/main/detail/9d24592752804d2790557f81230df62d
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“问kv cache相关”**；**“decoder的 qkv输入分别来自哪”**；**“除了MHA还知道哪些(GQA MQA MLA)讲原理”**

陷阱是把 GQA / MQA / MLA 都说成「少算一点 attention」。Decode 往往受 **KV 带宽**限制，不是受 $T^2$ 训练 FLOPs 限制。先说清 QKV 从哪来，再谈压缩轴。

## Decoder 的 Q、K、V

自回归一步：当前隐状态 $h_t$ 乘 $W_Q$ 得 $q_t$；历史 $k_{1:t-1},v_{1:t-1}$ 已在 KV cache，本步只算 $k_t,v_t$ 并追加。Encoder-decoder 的 cross-attn 则 $q$ 来自 decoder、$k/v$ 来自 encoder 记忆，cache 的是 encoder 侧，不随 decode 步增长。RoPE 加在 $q,k$ 上：$(R_t q_t)^\top(R_s k_s)=q_t^\top R_{s-t}k_s$，cache 里存的是旋转后还是旋转前，实现必须和推理一致。

## 三种省 cache 的切法

MHA：每头独立 KV，每 token 约 $2 n_h d_h$，质量最好、cache 最大。MQA：所有 Q 头共享一对 KV，$n_{\mathrm{kv}}=1$，cache 最小，头间独立性最差。GQA： $1\lt n_{\mathrm{kv}}\lt n_h$，若干 Q 头共享一组 KV，LLaMA / Qwen 常用中间点。

MLA（DeepSeek）：沿表示维压，不（只）砍头数。隐状态先到低维 $c_t^{KV}=W^{DKV}h_t$，$d_c\ll n_h d_h$，RoPE 再拆出短的 $k^R$。推理用矩阵吸收，不必还原全长 K/V。这和 GQA 的压缩轴不同，见 `arch-mla`。

FFN 侧仍可以是 SwiGLU 或 MoE，与 KV 布局正交：专家路由不减小 decode cache。

## 追问

- **省的是计算还是字节？** Prefill 仍接近 $O(T^2 d)$；decode 省的是每步读 cache 的字节数。
- **GQA 能和 MLA 叠吗？** 轴不同，能设计组合，但 head / latent / RoPE 维要重定义，不是两个开关。
- **MQA 质量为什么容易掉？** 所有头抢同一份 $k,v$，表达容量不够；GQA 用分组把容量买回来。
