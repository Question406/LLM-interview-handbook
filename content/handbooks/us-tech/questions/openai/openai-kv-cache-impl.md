---
id: openai-kv-cache-impl
section: openai
order: 5
level: S
title: OpenAI：从零实现 KV cache，有/无 cache greedy 必须对齐
quick: >-
  Prefill 一次写下整段 $K,V$，decode 只算当前 $[B,H,1,D]$ 的 $q,k,v$，沿时间维 concat。位置下标是
  `cache_len` 不是 0。同一前缀 greedy，有 cache 和全量重算必须逐 token 相同，对不上先查 RoPE / mask。
tags:
  - OpenAI
  - KV Cache
  - Inference
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
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer / MLE
- 轮次：ML debugging；公开报告是「改完带 bug 的 Transformer，再加 KV cache」
- 来源：Exponent 2025 候选人报告；细节和查 bug 顺序见 `openai-transformer-debug`

我会把正确性不变量先说出来，再写 concat。评委要的不是「cache 能跑」，是 **greedy 对齐**。

## 题怎么收：先不变量，再 API

打开 `eval()`，argmax，关 dropout。固定同一 prompt，两条路径各生成 $T$ 步：

1. 每步把已生成前缀整段重算（无 cache）。
2. prefill 一次，之后每步只喂 1 个 token（有 cache）。

逐 token 的 id 必须相同。差一个，cache 就是错的。采样温度不是 0 时对不齐，所以这题只用 greedy。

张量契约我现场写：prefill 后 `k_cache` / `v_cache` 是 `[B, H, S, D]`。一步 decode 的 $q,k,v$ 是 `[B, H, 1, D]`。`torch.cat(..., dim=2)` 得到 `[B, H, S+1, D]`。scores 是 `[B, H, 1, S+1]`。softmax 沿最后一维。GQA 时 cache 的 head 维是 $H_{\mathrm{kv}}$，repeat 发生在算注意力时，不要把 cache 存成 $H_q$ 份，见 `google-gqa-mqa`。

## 实现里我会主动踩的坑

```python
def decode_step(q, k_t, v_t, k_cache, v_cache):
    # q, k_t, v_t: [B, H, 1, D]
    k = torch.cat([k_cache, k_t], dim=2)
    v = torch.cat([v_cache, v_t], dim=2)
    scale = q.size(-1) ** -0.5
    scores = (q @ k.transpose(-2, -1)) * scale  # [B, H, 1, S]
    attn = torch.softmax(scores, dim=-1)
    return attn @ v, k, v
```

坑：

- **位置：** 新 token 的 RoPE / 绝对位置是 `k_cache.size(2)`，不是 0。写错不报错，只是和全量对不齐，见 `openai-rope-offset`。
- **mask：** 一次只 decode 1 个 token、cache 已是合法前缀时，没有「未来 key」要挡。一次塞进多个新 token（chunked decode）仍要一块相对 cache 的因果 mask；mask 用 0 会漏质量，见 `openai-softmax-bug`。
- **层：** 每一层一份 cache，不能只改最外层。
- **batch：** padding 不同长度时，cache 长度按序列走，不要用 batch 里的 max 去给短序列旋位置。

时间复杂度：无 cache 生成到长度 $t$ 是 $O(t^2 d)$ 每层；有 cache 单步 $O(t d)$。显存跟 $2 L T H_{\mathrm{kv}} d$ 成正比，优化是后话。

## 时间不够怎么收

先保证 greedy 对齐，再提 paged KV、量化 cache、speculative 的 rollback（`openai-speculative-decoding`）。评委追「为什么 decode 还是慢」，转到 prefill/decode 形态，见 `openai-prefill-decode`。

## 追问

- **和 full attention 差在哪？** 数学上应对齐。差了就是实现 bug，不是近似算法。
- **cache 要不要存 $Q$？** 不要。下一步的 $q$ 只来自新 token。
- **拒绝草稿为什么还碰 cache？** 投机解码会把未验证 token 写进 KV，拒绝后必须截断，否则后续注意力在看一段不存在的前缀。
- **GQA 的 cache shape？** `[B, H_kv, S, D]`，不是 `[B, H_q, S, D]`。
