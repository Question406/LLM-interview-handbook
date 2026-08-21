---
id: sys-pagedattention
section: systems
order: 8
level: A
title: PagedAttention 为什么像虚拟内存？
quick: >-
  把 KV Cache 切成固定-size blocks/pages，逻辑 sequence 的 KV 不必物理连续；block table 负责
  logical→physical 映射，减少碎片并支持动态增长/共享。
tags:
  - vLLM
  - KV Cache
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ vLLM
    url: 'https://arxiv.org/abs/2309.06180'
    type: legacy-reference
---

陷阱是说 PagedAttention 改了注意力公式，或把它和 FlashAttention 当成同一层。它改的是 **KV 怎么分配和查找**，像 OS 虚拟内存：逻辑地址连续，物理页可以散落。Attention 数学仍是 $QK^\top$ + softmax + $V$。加速来自少碎片、高并发，不是近似 softmax。见 `ant-vllm-paged`。

## 为什么像虚拟内存

传统为每个 request 预留 `max_len` 连续 KV buffer：内部浪费（实际长度 $\ll$ 预留）和外部碎片（空闲区凑不出一整段）。PagedAttention 把 cache 切成固定 size 的 block/page，逻辑 sequence 通过 **block table** 映射到非连续物理块。需要时分配一页，sequence 结束就回收，像 demand paging + free list。

页表查找有开销，但碎片下降通常更值：同样 HBM 能并发更多请求，这才是 vLLM 吞吐的主因之一。decode 仍是 memory-bound，paging 不把 decode 变成 compute-bound。

## 共享、增长、回收

相同 prefix 的请求可以 copy-on-write / share 同一批物理页；beam 的共同前缀也可复用。新 token 写时再拆页，避免改共享前缀。这和 `sys-prefix-cache` 配套：命中的是物理页，不是字符串。

动态增长：不必一开始按 `max_len` 占满。回收：请求结束页回池，连续 batching 才能立刻插入新请求。没有 paging，预留策略要么浪费，要么 OOM。并发从几十涨到上百时，碎片差的是整机 KV 容量，不是单条速度；面试把「更高并发」和「单步更快」分开说。

## 和 FlashAttention、量化分层

| | 解决什么 | 改不改公式 |
| --- | --- | --- |
| FlashAttention | 单步算子 HBM I/O | 不改，exact |
| PagedAttention | KV 分配与碎片 | 不改，改寻址 |
| KV 量化 | 每页存更少 bit | 改存储精度 |

三者常叠：页里可以是 FP8 KV，算子仍走 FlashAttention 风格 kernel。不要说「vLLM = PagedAttention」，它还叠加连续 batch、调度和 CUDA graph。

## 追问

- **是近似 attention 吗？** 不是。只是 $K/V$ 物理上不连续，kernel 按 block table Gather 再算。
- **页大小怎么选？** 太小则表项和间接访问多；太大则内部碎片回来。实现里常见十几到几十 token 一页。
- **和操作系统换页完全一样吗？** 类比是映射与碎片。一般不把 KV 换出到 CPU（太慢），缺页就是分配失败 / 抢占，不是去盘上取。
- **没有 paging 能连续 batch 吗？** 能，但预留 `max_len` 会迅速把并发打没。paging 是让连续 batch 在显存上可扩展。
- **页表存在哪？** 每条序列一份 block table，kernel 按 logical block id 查物理页。这是额外的小元数据，通常远小于 KV 本身。
