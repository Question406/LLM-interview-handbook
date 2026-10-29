---
id: sys-pagedattention
section: systems
order: 8
level: A
title: PagedAttention 为什么像虚拟内存？
quick: "PagedAttention 把 KV cache 切成固定大小的 block/page，用 block table 把序列的逻辑位置映射到不连续的物理页，类似虚拟内存。序列按需增长、结束后回收，也能共享前缀，因而减少碎片并提高并发。Attention 公式保持不变，页表查找则会增加少量开销。"
tags:
  - vLLM
  - KV Cache
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ vLLM
    url: 'https://arxiv.org/abs/2309.06180'
    type: legacy-reference
---

PagedAttention 像虚拟内存，是因为它把序列的逻辑位置和 KV 的物理位置分开。比如一条请求要继续生成，不必找更长的连续 buffer，只要再分配一页、更新 block table。Attention 仍算 $QK^\top$ + softmax + $V$，主要收益来自减少碎片和提高并发；它与 FlashAttention 优化的层次不同，相关题见 `ant-vllm-paged`。

## 按页分配和回收

传统为每个 request 预留 `max_len` 连续 KV buffer：内部浪费（实际长度 $\ll$ 预留）和外部碎片（空闲区凑不出一整段）。PagedAttention 把 cache 切成固定 size 的 block/page，逻辑 sequence 通过 **block table** 映射到非连续物理块。需要时分配一页，sequence 结束就回收，像 demand paging + free list。

页表查找有开销，但碎片下降通常更值：同样 HBM 能并发更多请求，这才是 vLLM throughput 的主因之一。逐 token 生成（decode） 仍是 memory-bound，paging 不把 decode 变成 compute-bound。

相同前缀还可以共享物理页。

相同 prefix 的请求可以 copy-on-write / share 同一批物理页；beam 的共同前缀也可复用。写入新 token 时再拆页，避免改共享前缀。这和 `sys-prefix-cache` 配套：命中的是物理页，不是字符串。

动态增长：不必一开始按 `max_len` 占满。回收：请求结束页回池，连续 batching 才能立刻插入新请求。没有 paging，预留策略要么浪费，要么 OOM。并发从几十涨到上百时，碎片差的是整机 KV 容量，不是单条速度；我会把「更高并发」和「单步更快」分开说。

## 和算子优化、量化如何组合

| | 解决什么 | 改不改公式 |
| --- | --- | --- |
| FlashAttention | 单步算子 HBM I/O | 不改，exact |
| PagedAttention | KV 分配与碎片 | 不改，改寻址 |
| KV 量化 | 每页存更少 bit | 改存储精度 |

三者常叠：页里可以是 FP8 KV，算子仍走 FlashAttention 风格 kernel。不要说「vLLM = PagedAttention」，它还叠加连续 batch、调度和 CUDA graph。

## 追问

**是近似 attention 吗？**
不是。只是 $K/V$ 物理上不连续，kernel 按 block table Gather 再算。
**页大小怎么选？**
太小则表项和间接访问多；太大则内部碎片回来。实现里常见十几到几十 token 一页。
**和操作系统换页完全一样吗？**
类比是映射与碎片。一般不把 KV 换出到 CPU（太慢），缺页就是分配失败 / 抢占，不是去盘上取。
**没有 paging 能连续 batch 吗？**
能，但预留 `max_len` 会迅速把并发打没。paging 是让连续 batch 在显存上可扩展。
**页表存在哪？**
每条序列一份 block table，kernel 按 logical block id 查物理页。这是额外的小元数据，通常远小于 KV 本身。
