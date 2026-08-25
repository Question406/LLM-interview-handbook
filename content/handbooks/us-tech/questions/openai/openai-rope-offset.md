---
id: openai-rope-offset
section: openai
order: 7
level: S
title: OpenAI：RoPE 在 decode 时位置偏移写错会 silently 错，怎么查
quick: >-
  RoPE 编码的是相对差 $m-n$。decode 时新 token 的 $m$ 必须是 `cache_len`，不能每步从 0 旋。写错不
  NaN、shape 也对，只是和 full attention greedy 对不齐。查 cos/sin 下标，不要先改 kernel。
tags:
  - OpenAI
  - RoPE
  - KV Cache
  - Debug
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 题怎么来的

公开 Transformer debug 轮会植入位置编码错误；加 KV cache 之后，位置从「一段 `[0..S)`」变成「每步一个标量」。现在默认实现是 RoPE，不是论文里的正弦绝对位置，所以我会按 RoPE 讲 decode 偏移。没有单独的 Exponent id 写「RoPE offset」这五个字，它是 `openai-kv-cache-impl` 对不齐时的第一嫌疑。

评委爱这题，因为 **silently wrong**：没有异常、没有 shape assert，短 prompt 有时还看不出来。

## 相对位置一写错，全表都在撒谎

RoPE 把一对维度转一个角 $\theta_i m$。query 在位置 $m$、key 在位置 $n$ 时，点积只依赖 $m-n$。这是优点，也是 debug 陷阱：你给所有 decode token 都旋位置 0，模型仍然在做「合法注意力」，只是每一步都以为自己站在句首。

典型错法：

```python
# 错：q_len=1 时永远旋位置 0
pos = torch.arange(q.size(2), device=q.device)
q, k = apply_rope(q, k, cos[pos], sin[pos])

# 对：新 token 用 cache 长度当绝对下标
pos = torch.arange(cache_len, cache_len + q.size(2), device=q.device)
```

Prefill 一次旋 `[0, S)` 没问题。出问题的是第二步开始：cache 里的 $K$ 已经按 $0..S-1$ 旋过，**不要再旋一遍**。新写入的 $k_t$ 只旋 $t=S$。对 cache 里的旧 $K$ 做第二次 RoPE，相对差会变成 $m-(n+\delta)$，整段历史全偏。

绝对位置编码同构：decode 查 embedding 表也要用 `cache_len`，不能 `pos_emb[0]`。

## 怎么查：对齐，再查表

1. **greedy 对齐。** 同一权重、同一前缀，full forward 和 cached decode 逐 token 必须相同。这是总闸，见 `openai-kv-cache-impl`。对不上不要先猜数值误差，先打印每层 `position_ids`。
2. **打印下标。** 第 $t$ 步 decode，`position_ids` 应是 $t$，不是 0，也不是 `arange(1)`。cos/sin 表长度要覆盖 `max_seq`，超长要插值或报错，不要 silently wrap。
3. **小矩阵探针。** 固定 $q,k$ 为相同向量，只改位置。RoPE 下 $m=n$ 时点积最大（相对 0）；若 decode 步步都像相对 0，说明 offset 没加上。
4. **不要用 loss。** 训练态每步都是 full 序列，RoPE 是对的；bug 只活在 inference 的 cache 路径。所以训练 loss 正常、serving 一开 cache 就胡言，是这题的签名。

GQA 不改变位置逻辑：旋的是每个 KV head 的 $D$ 维，head 数见 `meta-llama-gqa`。chunked prefill 时一块新 token 内部仍用连续递增的绝对下标，再接到 `cache_len` 后面。

和 softmax / mask 类 bug 的差别：那些会破坏归一或泄漏未来位，有时能用单测一眼抓住，见 `openai-softmax-bug`。RoPE offset 错了，注意力仍然是合法分布，所以必须靠有/无 cache 的 teacher 对齐，不能靠 `attn.sum(-1)==1`。

## 追问

- **为什么说 silently？** 没有非法 shape，softmax 仍归一，输出范数正常。只有和 teacher（无 cache）比才暴露。
- **ALiBi 会不会同样翻车？** 会。ALiBi 的偏置是距离；decode 若按「当前块内距离」算，等于忽略了 cache 里已经有 $S$ 个 token。
- **投机解码拒绝后位置怎么回滚？** cache 截到接受前缀，下一步的 offset 是新的 `cache_len`，见 `openai-speculative-decoding`。
- **长上下文插值？** 那是表怎么延拓，不是 offset。先保证 $m=\mathrm{cache\_len}$，再谈 NTK / YaRN。
