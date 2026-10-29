---
id: openai-speculative-decoding
section: openai
order: 8
level: A
title: OpenAI：speculative decoding 拒绝草稿时为什么要 rollback KV
quick: >-
  验证草稿时，target 已经为整段草稿写入 KV；若只接受前缀，就必须把 target 和 draft 的 cache 都截回接受长度。比如第 $k+1$
  个草稿被拒绝，后面的 $K,V$ 属于未提交文本，不能继续参与 attention，RoPE offset 也要随新长度回退。
tags:
  - OpenAI
  - Speculative Decoding
  - KV Cache
  - Inference
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: 'https://arxiv.org/abs/2211.15661'
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 可以这样回答

拒绝草稿后必须回滚 KV，因为验证前向已经把草稿对应的状态写进 cache。比如接受前 $k$ 个、拒绝第 $k+1$ 个，输出文本里没有被拒绝的草稿，cache 里也不能留下它，否则下一步会读到未采用的历史。

小草稿模型 $q$ 一次提出 $\gamma$ 个 token $x_{t+1},\ldots,x_{t+\gamma}$。目标模型 $p$ 用一次平行前向（这段很像短 prefill）算出这 $\gamma$ 个位置的 logits。然后从左到右接受：以 $\min(1, p(x)/q(x))$ 的概率留下草稿 token，直到第一次拒绝。拒绝处从修正分布再抽一个真正的 token。期望接受长度大于 1 时，target 的前向次数就少了。

## 技术备查

拒绝草稿后必须回滚 KV，因为验证前向已经把草稿对应的状态写进 cache。比如接受前 $k$ 个、拒绝第 $k+1$ 个，输出文本里没有被拒绝的草稿，cache 里也不能留下它，否则下一步会读到未采用的历史。



这张卡按 Leviathan 等人的 speculative decoding 论文整理，是 `openai-kv-cache-impl` 的正确性延伸，没有对应的公开逐字原题。

## 接受前缀决定 cache 长度

小草稿模型 $q$ 一次提出 $\gamma$ 个 token $x_{t+1},\ldots,x_{t+\gamma}$。目标模型 $p$ 用一次平行前向（这段很像短 输入 prefill）算出这 $\gamma$ 个位置的 logits。然后从左到右接受：以 $\min(1, p(x)/q(x))$ 的概率留下草稿 token，直到第一次拒绝。拒绝处从修正分布再抽一个真正的 token。期望接受长度大于 1 时，target 的前向次数就少了。

关键：这一次平行前向已经把草稿位置的 $K,V$ 算出来并 append 进 target cache。接受 $k$ 个、拒绝第 $k+1$ 个，意味着序列里没有第 $k+1$ 个草稿 token，但它的 KV 已经躺在 cache 末尾。

所以 rollback 是：

- target cache 从 $S+\gamma$ 截回 $S+k$（再写入拒绝处新 sampling 的那个 token 的 KV）。
- draft cache 同样截。两条 cache 的长度必须等于已提交文本的长度。
- 下一步 RoPE 的 offset 是新的 `cache_len`，见 `openai-rope-offset`。

只 `pop` 输出 token、不截 KV，后面每一步 $q_t$ 都会点积到那段未被采用的 key。生成会 silently 偏，和「位置从 0 旋」同属对齐失败，不是随机噪声。

拒绝处的那一个 token 从修正分布抽，不是草稿里的下一个。论文写法是把 $p$ 里被 $q$ 多给的质量削掉再归一。实现上我先 `resize` cache 到 $S+k$，再把这个新 token 当普通 decode 一步写进去。顺序反了会把拒绝草稿的 KV 留在 $S+k$ 这个槽里。

```python
k_cache = k_cache[:, :, : S + n_accept, :]
v_cache = v_cache[:, :, : S + n_accept, :]
# 再 append 拒绝处新 sampling token 的 k_t, v_t
```

## 再看草稿成本与调度

验证那一步是 compute-bound 的小 prefill，草稿模型本身仍是 decode。加速比取决于 $q$ 有多接近 $p$、$\gamma$ 取多大。$\gamma$ 太大，拒绝来得早，白写的 KV 和白算的草稿变多。$\gamma$ 太小，一次前向摊不回。

和 continuous batching 叠的时候更烦：每个请求的接受长度不同，不能假设 batch 里每条都 append $\gamma$ 再一起 truncate。按请求维护 cache 指针，拒绝就 `resize` 时间维。paged KV 把「截断」变成还 page，而不是大块 `cat` 再拷，见 `openai-continuous-batching`。

数值：greedy 投机（草稿和目标都 argmax）时，接受规则退化成「前缀必须逐 token 相同」，rollback 仍然要做：相同前缀之后第一条分歧仍会多写 KV。

验收和 `openai-kv-cache-impl` 同一把尺子：固定 greedy，投机路径（$\gamma>1$）和逐步 decode 必须逐 token 相同。对不上先查 rollback 有没有漏层，再查 RoPE offset。

文本指针和 KV 指针是同一个长度。任何让两者分叉的优化都要在拒绝时让两者重新保持一致。

## 追问

**不 rollback 能靠 mask 挡掉幽灵 token 吗？**
能硬挡，但长度、位置、page 表全要记一份额外状态，还容易漏一层。截断更干净。
**草稿模型要不要和 target 共享 tokenizer？**
要，否则接受规则没有同一 $x$ 可比。
**和 Medusa / 多头草稿？**
草稿来源变了，rollback 不变量不变：未提交的位置不准留在 cache 里。
**拒绝后要不要重算 prefill？**
不要。接受前缀的 KV 是合法的，只丢拒绝点及其后。

## 相关题

- [[openai-kv-cache-impl]]：先把基础 KV cache 写对、有/无 cache 对齐，本题的回滚建立在它之上。
- [[openai-rope-offset]]：回滚之后 `cache_len` 变了，RoPE 的位置偏移也得跟着退回去。
- [[openai-transformer-debug]]：主体是查 Transformer 的 bug，追问里同样问 speculative decoding 和 cache 怎么配合。
- [[google-tpu-decode]]：从 throughput 角度看 speculative decoding：把 decode 的 $M$ 做大，喂满 MXU。
- [[sys-spec-sys]]：同样讲拒绝后截断 KV，内容大半重叠，另外多了草稿长度怎么选和 throughput 怎么测。
- [[coding-spec-accept]]：先把接受规则写对，才知道 KV 要截到哪一步。
