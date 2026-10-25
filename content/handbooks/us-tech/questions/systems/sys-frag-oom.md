---
id: sys-frag-oom
section: systems
order: 65
level: B
title: 系统：显存没用满却 OOM，是碎片还是缓存？
quick: "显存总空闲够，也可能因为找不到足够大的连续块而分配失败；分配器保留的缓存又和真正活跃的张量占用不同。我会先看失败的那次分配要多大，再判断是实际峰值超容量、碎片，还是两套状态同时驻留。"
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

显存没用满仍 OOM 时，我会先看这次申请要多大的连续块，再看活跃张量和分配器缓存的占用。比如还空着 10GB，却分散成很多小块，申请一个连续的 2GB 仍可能失败。这道题按 PyTorch caching allocator 整理，激活与参数的容量排查见 `sys-oom-order`。

设备上的活跃张量占用和分配器还没还给驱动的保留空间，要分开看。`empty_cache` 把缓存还给驱动，不缩小这一步真正要的峰值。训练中途调用它，常常只是把下一步的分配变慢。

失败信息里的「要 2GB」比「还剩 10GB」重要。剩的 10GB 是多块小空闲，2GB 要连续。长时间训练、反复分配不同大小的激活，容易变成这样。流水线切换 microbatch、后训练里 KV 池和训练状态反复加载和释放，也会把地址空间打散。

先确认峰值本身是否超过卡的容量。超过，减激活或上 ZeRO，整理碎片没用。峰值够、只是找不到连续块：固定住常见的激活大小，避免每步形状差很多；后训练切换 KV 和训练状态时，按 `sys-rollout-place` 的顺序，不要两边同时占着。 expandable segments 和推理引擎的虚拟内存分配器不能混用，verl 的权重同步里会暂时关掉它。

```python
def frag_hint(allocated, reserved, request):
    free_in_pool = reserved - allocated
    if free_in_pool > request and allocated + request < reserved:
        return "fragmented cache: need a contiguous block"
    return "true peak: shrink activations or shard state"
```

## 追问

**只在跑了几千步之后 OOM？**
通常不只是静态参数状态的 16 字节估算问题。看是缓存涨了，还是某条长样本把激活峰值抬高。把那一步的序列长度打出来。
