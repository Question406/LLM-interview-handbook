---
id: sys-kv-fair-allocation
section: systems
order: 24
level: A
title: 动态长度、多分支 sampling 的 KV Cache 如何分配，为什么要有 block / page、copy-on-write 和 preemption 策略？
quick: >-
  连续预留会碎片化，prefix 也没法高效共享。我会按块做 page 分配，动态增长、共享前缀、分支 copy-on-write。容量不够时在
  recompute、swap、preempt 之间权衡，并看 KV OOM、尾延迟、被抢占率和吞吐。
tags:
  - KV Cache
  - PagedAttention
  - Scheduling
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

这块容易按 `max_seq_len` 给每条请求预留一段连续 KV。生成长度事先不知道，beam / Best-of-N / 树采样还会分叉：短请求浪费，长请求在碎片缝里分配失败，共享的 输入提示（prompt） 前缀被复制多份。Serving 的 KV 管理更像操作系统的虚拟内存，而不是「一张大 tensor 切条」。

## 1. 为什么要 page / block

PagedAttention 把 KV 切成固定大小的 block（例如 $16$ 或 $64$ 个 token）。每条序列有一张 **block table**：逻辑位置 $\to$ 物理页。新 token 按需挂页，不必连续。好处有三：

1. **动态增长：** 只为已经写出的 token 付费，而不是为 `max_new_tokens` 预留空洞。
2. **减少外部碎片：** 空闲页可以给任意序列；失败条件变成「没有空闲页」，而不是「没有足够长的连续段」。
3. **前缀共享：** 同一输入提示、同一 system 前缀可以让多条请求的 table 指向同一组物理页，靠引用计数活着。

没有这层间接寻址，continuous batching 很难把不同长度的序列紧排在一起：要么 pad 到最长（假占用），要么频繁拷贝整段 KV。

数量级：`max_new_tokens=2048`、真实平均只生成 $200$ token、并发 $64$ 时，连续预留大约浪费 $90\%$ 的 KV 槽位；page 分配则按实际长度付费。这就是 vLLM 相对「静态预留」能提高并发的主要来源，不是 attention 公式变了。

## 2. 分叉必须 copy-on-write

Best-of-N、beam、投机解码的多候选，在分歧点之前读的是同一段历史 KV。若每条分支复制整段 cache，内存按 $G$ 倍涨，前缀完全重复。正确做法是共享只读页；**当某分支要写入一个仍被共享的 block 时再拷贝该页**（copy-on-write），之后引用计数分开。

写共享页而不 CoW，会把另一条分支的历史改脏，采样分布和 attention 一起错。只在分叉瞬间拷整条序列，则又退回「预留连续段」的浪费。CoW 的粒度是 page，不是整条 request。

## 3. 容量不够时的三类策略

KV 池是硬上限（可与模型权重争 HBM）。调度器在页用尽时通常三选一或组合：

| 策略 | 做法 | 代价 |
| --- | --- | --- |
| Recompute | 丢掉受害者 KV，以后从 prompt 重算 | 算力换内存，首个 token 的等待时间（TTFT） / 中断延迟升 |
| Swap | 页换到 host / 更远存储 | PCIe 流量，逐 token 生成（decode） 步抖动 |
| Preempt | 整条请求暂停或踢出，让给更高优先级 | 公平性与尾延迟；可能级联重试 |

没有绝对最优。长思维链（CoT）占满页时，短请求会长时间无法运行；只保吞吐则大 tenant 挤占。同时看 KV OOM 次数、碎片率（有空字节却分不出页）、preempt 率、recompute token、P99 TPOT、每完成请求的有效 token。只报 GPU utilization 会掩盖「算力很忙、页已经不公平」。

优先级与长度感知的 admission（先估计剩余页、限制并发 $G$）比事后抢占更稳。公平性可以按 token、按请求或按租户配额，三种目标互相冲突，要在 SLA 里写死。

## 追问

- **Block 太大或太小怎么选？** 太大则内部碎片（页尾浪费）和 CoW 拷贝变贵；太小则 table 变长、寻址开销升。常见几十 token 一页，按模型与平均长度扫一眼内部碎片即可。
- **和 OS 虚拟内存的差别？** 思路同（页表、引用计数、缺页），但「缺页」发生在 GPU 上，swap 走 PCIe，延迟比 DRAM 缺页贵一个数量级，所以更常选抢占或重算。
- **Prefix caching 和 CoW 是同一机制吗？** 都靠共享物理页。Prefix cache 跨请求复用已算好的 prompt；CoW 是同请求多分支写入时的隔离。实现上常共用 block 分配器。
