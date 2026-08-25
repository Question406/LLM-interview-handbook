---
id: apple-mha-code
section: apple
order: 1
level: A
title: Apple / Siri MLE：手写 Multi-Head Attention，shape 和 mask 怎么收？
quick: >-
  $[B,T,d]$ 投成 QKV，reshape 成 $[B,H,T,d_h]$，scores 做 $QK^\top/\sqrt{d_h}$，softmax 前加因果 /
  padding mask，再乘 V、merge heads。Apple 电面常把这题当 ML coding，要能讲 mask 广播和 fp16 稳定。
tags:
  - Apple
  - Siri
  - Attention
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Apple Siri MLE Phone Screen 面经
    url: https://www.1point3acres.com/bbs/thread-1170553-1-1.html
    type: candidate-first-hand
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 真题记录

- 公司：Apple
- 岗位：Siri / Apple Intelligence 相关 MLE
- 来源：一亩三分地 2026-03 Siri MLE phone screen 讨论。公开回复把高频 ML coding 收成：sampling（top-k / top-p）、k-means、attention、KV caching、MLP 反传
- 组间差异大：有的 30 分钟 coding + 30 分钟 ML Q&A，有的偏 case study。以 recruiter 邮件为准

完整实现见 `code-attention`，KV 一步见 `code-kv-cache-step`，采样见 `code-sampling`。本题按 Apple 电面的收法写：shape 先写对，mask 说清，再提数值。

## 白板最小闭环

$d_{\mathrm{model}}$ 能被 $H$ 整除，$d_h=d_{\mathrm{model}}/H$。

1. `qkv = Linear(x)` → split 成 $Q,K,V$，各 `[B,T,H,d_h]`，再 transpose 成 `[B,H,T,d_h]`。
2. `scores = einsum("bhtd,bhsd->bhts", q, k) / sqrt(d_h)`。
3. Mask：**先加 mask，再 softmax**。因果 mask 把 $t<s$ 的位置打成 $-\infty$。Padding 同理。Mask 形状要能广播到 `[B,H,T,S]`，不要在 head 维上 silently 错位。
4. `attn = softmax(scores, dim=-1)`，再 `@ V`，transpose 回 `[B,T,H,d_h]`，view 成 `[B,T,d]`，输出投影。

电面 30 分钟写完正向就很好。主动说：fp16 下不缩放会 overflow；eval 关 dropout；decode 一步只算当前 $q$，K/V 走 cache。KV cache 是同一条评论里的高频 follow-up，见 `openai-transformer-debug`。

采样 follow-up（同一批面经）：先温度再 top-k / top-p，nucleus 在温度化之后的分布上切。不要先截断再除 $T$。细节走 `code-sampling`。

## Apple 口味

Siri 上的注意力题往往会拐到 **端侧约束**：head 数、KV 是否 GQA、量化后 mask 还能不能用 $-\infty$。答「和云端同一份 PyTorch」不够。可以说：端上 decode 更在意 KV 带宽，GQA / 量化 cache 比再堆 head 优先；mask 在 int8 scores 上要用足够负的数，不能假设 fp32 的 `-1e9` 一定安全。

组里如果做语音，可能追 self-attention vs cross-attention（encoder 记忆 vs decoder 当前）。那是另一套 shape，Q 来自 decoder，K/V 来自 encoder，没有因果 mask 在 cross 上。

## 追问

- **为什么除 $\sqrt{d_h}$？** 点积方差随维数涨，softmax 饱和。
- **和 Multi-Query 的代码差一行？** $K,V$ 的 head 维是 $H_{\mathrm{kv}}$，attention 前 repeat。见 `apple-siri-grounded` 的产品约束和 `google-gqa-mqa`。
- **k-means 为什么也出现？** 同一条面经把聚类当 ML coding 基本功。别把所有时间赌在 Transformer 上，准备一个 20 行的向量化 k-means。
