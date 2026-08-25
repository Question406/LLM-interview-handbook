---
id: openai-continuous-batching
section: openai
order: 12
level: A
title: OpenAI：continuous batching / iteration-level 调度解决什么
quick: >-
  请求级 batch 要等最慢那条生成完，短请求被 padding 和队头阻塞。iteration-level 每步允许新请求加入、完成的
  退出，GPU 一直对着「当前还活着的 token」。没有可分页的 KV，变长 append 会把显存预留打满。
tags:
  - OpenAI
  - Continuous Batching
  - Serving
  - KV Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Orca — A Distributed Serving System for Transformer-Based Generative Models
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

这是推理系统题，不是某一份能点名的 OpenAI onsite 原题。Orca 把调度从 request-level 改成 iteration-level；vLLM 用 PagedAttention 让 KV 可以按页增长。ChatGPT 类产品的并发来自大量不同长度的对话，我会按「浪费从哪来」答，并接到 `openai-prefill-decode`。

## 请求级 batch 在浪费什么

静态 batch：凑满 $B$ 条，pad 到这个 batch 的 max length，一起 decode，直到最慢那条 EOS。三条罪状：

1. **Padding。** 长度 20 和长度 200 坐一桌，短的每步都在算 pad。
2. **队头阻塞。** 先到的短请求必须等这个 batch 收齐，或者等长请求结束。
3. **KV 预留。** 不知道一条会生成多长，只能按 `max_new_tokens` 预留连续显存。实际往往用了 10%，剩下的 page 锁死，并发上不去。

所以裸 tokens/s 可能还行，goodput（满足延迟 SLO 的完成数）很差。这和训练的固定 $T$ 完全不是同一个问题。

具体想一个 batch：三条请求还要 8、40、200 步。请求级调度会让前两条陪着第三条空转 160 步。iteration-level 下，第 8 步和第 40 步各腾出一个槽，等待队列里的新 prefill 可以立刻填上。吞吐差的就是这些空槽，不是模型 FLOPs。

## iteration-level 在干什么

Orca 的想法：调度单位是 **一次 decoder iteration**，不是一次完整请求。每步：

- 已结束的序列出队，释放它的 KV。
- 等待中的新请求，在有空位时 prefill 并加入。
- 活着的序列各走 1 个 token，batch 形状每步都变。

GPU 不再为已经结束的位置做 GEMM。连续批（continuous batching）说的就是这个：batch 成员随时间连续替换，而不是一个栅栏等所有人。

没有 paging 时，KV 仍要连续 `cat`，变长仍迫使你按上限预留。vLLM 把 KV 切成固定 page，逻辑上连续、物理上散。新 token 申请一页，结束就还页。投机解码拒绝时还页就等于 rollback，见 `openai-speculative-decoding`。

和 prefill 的关系：新请求的 prefill 若整段塞进同一 iteration，会打爆这一步的时延。常见补丁是 chunked prefill：一步只消化部分 prompt，其余 slot 留给 decode，避免 `openai-prefill-decode` 里说的队头阻塞。彻底拆池则是另一档架构。

实现上每条请求至少要：当前 `position`、采样 RNG、结束条件、以及 KV 的 page 表。batch 维不再对应「第 $i$ 个固定样本」，而是当前活着的 slot。attention kernel 必须能吃 ragged 长度，或先按 page 间接寻址。写死 `[B, H, T_max, D]` 再 pad，等于把 continuous batching 的收益吐回去。

面试我会画两个时间线：上面是静态 batch 的空白 pad，下面是每步都满的活 token。评委追「状态存在哪」，答：每条请求一份 KV 指针 + 采样状态，没有全局 `T`。

## 追问

- **和动态 batching 的差别？** 很多框架的 dynamic batch 只是凑请求再整段跑完。continuous 是跑的过程中成员还在变。
- **公平性？** 长生成会占着 KV。要有 max tokens、优先级、或抢占（抢占必须能把 KV offload / 丢弃）。
- **batch 越大越好吗？** decode 在带宽饱和前是的；再大 TTFT 排队变差。对着 SLO 调，不对着 MFU 调。
- **训练能不能这么调度？** 没必要。训练样本长度可切齐，没有在线到达过程。
