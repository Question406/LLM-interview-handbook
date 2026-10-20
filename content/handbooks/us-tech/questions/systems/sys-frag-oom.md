---
id: sys-frag-oom
section: systems
order: 65
level: B
title: 系统：显存没用满却 OOM，是碎片还是缓存？
quick: >-
  分配器要一块连续地址，空闲总量够也可能失败。caching allocator 会把释放的块留着。
  先看是哪一次分配失败、要多大，再决定是减峰值、换分配器，还是真的状态放不下。
tags:
  - Pretrain
  - Memory
  - OOM
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: PyTorch CUDA memory management
    url: https://pytorch.org/docs/stable/notes/cuda.html
    type: primary
---

## 题怎么来的

`sys-oom-order` 分的是激活和参数。这道是「nvidia-smi 还有十几 GB，分配仍失败」。按 PyTorch 的 caching allocator 拟的。

## 两种数

设备上已占用的，和分配器手里还没还给驱动的，不是同一个数。`empty_cache` 把缓存还给驱动，不缩小这一步真正要的峰值。训练中途调用它，常常只是把下一步的分配变慢。

失败信息里的「要 2GB」比「还剩 10GB」重要。剩的 10GB 是多块小空闲，2GB 要连续。长时间训练、反复分配不同大小的激活，容易变成这样。流水线切换 microbatch、后训练里 KV 池和训练状态反复加载和释放，也会把地址空间打散。

## 怎么处理

先确认峰值本身是否超过卡的容量。超过，减激活或上 ZeRO，整理碎片没用。峰值够、只是找不到连续块：固定住常见的激活大小，避免每步形状差很多；后训练切换 KV 和训练状态时，按 `sys-rollout-place` 的顺序，不要两边同时占着。 expandable segments 和推理引擎的虚拟内存分配器不能混用，verl 的权重同步里会暂时关掉它。

## 代码

```python
def frag_hint(allocated, reserved, request):
    free_in_pool = reserved - allocated
    if free_in_pool > request and allocated + request < reserved:
        return "fragmented cache: need a contiguous block"
    return "true peak: shrink activations or shard state"
```

## 追问

**只在跑了几千步之后 OOM？** 通常不只是静态参数状态的 16 字节估算问题。看是缓存涨了，还是某条长样本把激活峰值抬高。把那一步的序列长度打出来。
