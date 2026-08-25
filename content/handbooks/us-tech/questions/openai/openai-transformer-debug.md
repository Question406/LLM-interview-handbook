---
id: openai-transformer-debug
section: openai
order: 1
level: S
title: OpenAI：给一份带 bug 的 Transformer，怎么查？KV cache 怎么加？
quick: >-
  先固定 greedy + eval，按 shape 和数值把 bug 分到因果 mask、softmax 维、1/sqrt(d)、位置偏移、target
  shift。改完再加 prefill/decode：cache 沿时间维 concat，新 token 的位置下标是 cache 长度，cached
  与 uncached 逐 token 必须一致。
tags:
  - OpenAI
  - Transformer
  - KV Cache
  - Debug
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Experience (2025)
    url: https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2
    type: candidate-first-hand
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: OpenAI MLE phone screen Transformer debugging (1Point3Acres)
    url: https://www.1point3acres.com/interview/thread/1134115
    type: candidate-first-hand
---

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer / Machine Learning Engineer
- 轮次：ML debugging（onsite 技术轮）；也有 phone screen 变体
- 来源：Exponent 2025 候选人报告；一亩三分地 MLE phone screen 摘要
- 题面大意：给约 300 行 Transformer，四个标注区间各有一个 bug。改完实现 KV cache。几乎不给提示。

这块容易一上来改「感觉不对」的几行。OpenAI 这轮要的是可复现的定位：先让生成确定性，再按张量契约把 bug 归类。KV cache 是加分项也是翻车项，位置偏移写错会 silently 和 full attention 对不上。

## 先固定观测，再按五类查

打开 `eval()`，greedy / argmax，关掉 dropout。训练态和采样态混在一起，你改对了也看不出来。然后对每个标注块问：

1. **因果 mask：** `masked_fill` 必须在 softmax 之前，非法位置是 $-\infty$ 不是 $0$。用 $0$ 乘权重，softmax 仍会分质量给未来 token。
2. **softmax 轴：** 必须沿 key 长度。`dim=0` 或沿 head 维是公开复述里很常见的植入 bug。
3. **缩放：** $QK^\top/\sqrt{d_k}$。漏了之后 fp16 很容易 overflow，loss 变 NaN。
4. **位置：** 绝对位置编码在 decode 时必须用 `cache_len` 当 offset，不能每步都写位置 0。RoPE 同理，旋转的是 cache 对齐后的下标。
5. **训练对齐：** next-token 要 shift；logits 上不能先 softmax 再喂 CE。

Shape 断言比读代码快：`q` 是 `[B,H,1,D]`，`k` 是 `[B,H,S,D]`，`scores` 是 `[B,H,1,S]`。head 维和时间维交换是另一类高发 bug。完整手写见 `code-attention`。

公开报告里的四个区间，大致就落在位置编码、因果 mask、输出投影、训练 loop 这几类。不要把时间花在没标注的「风格重构」上。

## KV cache：正确性不变量比省算力先说

Prefill 一次写下整段 $K,V$。Decode 只算当前 $q_t,k_t,v_t$，沿时间维 concat，再 $q_t$ 对全部 past keys 做点积。单步从 $O(t^2 d)$ 变成 $O(t d)$。张量步骤见 `code-kv-cache-step`，显存公式见 `arch-kv-cache`。

面试里我主动报不变量：**同一前缀、greedy，有 cache 和没 cache 必须逐 token 相同。** 写错最常见的是位置：新 token 用 `cache_len`，不是 0。cache 非空且一次只 decode 1 个 token 时，没有「未来位置」要 mask；chunked decode（一次多个新 token）仍要一块相对 cache 的因果 mask。

Cache 要穿过每一层，不能只改最外层 attention。GQA 时 cache 的 head 维是 $H_{\mathrm{kv}}$ 不是 $H_q$，repeat/broadcast 发生在注意力计算里。

时间不够就先保证正确性，再提 MQA/GQA、paged attention、量化 cache。评委追优化时再讲带宽：decode 是读历史 KV，和训练时的 $O(T^2)$ 不是同一件事。

## 追问

- **为什么 mask 不能用 0？** softmax($[s,0]$) 仍给未来位置正质量。必须是 $-\infty$，softmax 后才是 0。
- **cache 显存怎么降？** 跟 $H_{\mathrm{kv}}\cdot T\cdot d$ 成正比。GQA/MQA、量化、paged 共享。见 `arch-gqa`。
- **speculative decoding 和 cache？** 拒绝草稿 token 时要 rollback cache 到验证通过的前缀，不能只改输出文本。
