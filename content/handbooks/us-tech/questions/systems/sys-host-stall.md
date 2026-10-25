---
id: sys-host-stall
section: systems
order: 50
level: B
title: 系统：GPU 空转，先分是数据没喂上，还是卡在通信？
quick: "GPU kernel 之间有长空隙时，我会先查 dataloader、解压和拷贝是否及时，再看通信是否在等待。若 GEMM 和 AllReduce 首尾相接，则检查通信重叠；若只有一张卡晚到，则沿着慢卡查。用内存里的假 batch 做对照，可以先隔离数据路径。"
tags:
  - Pretrain
  - Profiling
  - Data Pipeline
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: PyTorch DDP notes
    url: https://pytorch.org/docs/stable/notes/ddp.html
    type: primary
---

GPU 空转时，我会先看 timeline，把主机没有及时供数据、通信没有重叠和单卡晚到分开。比如所有卡都在等下一个 batch，NCCL 条也可能是空的，这时应先查 dataloader 和拷贝。慢卡与超时见 `sys-straggler`，数据路径见 `sys-data-pipeline`。

先看一步里 GPU 利用率。利用率和 MFU 一起掉、kernel 之间有长空隙：主机没把下一批送上设备。dataloader 的 worker 不够、解压在主进程、或者主机到 GPU 的拷贝没提前。这时 NCCL 也在等，因为集体通信要所有卡一起进入。不要先把通信库换一版。

kernel 很密、步时间仍长：看 GEMM 是否达到单卡该有的速度。没有，就是形状、精度或没走到 Tensor Core。有，但步时间里多出一条和计算串行的 AllReduce，就是桶没有重叠，见 `sys-ddp-bucket`。

只有一张卡晚到：其他卡堵在同一个集合通信里。那是 straggler，不是所有卡的数据都慢。

最直接的对照是把 dataloader 换成内存里的随机 batch。步时间恢复，就能把问题缩到数据路径。不恢复，再查通信和 kernel。不要同时改桶大小、worker 数和并行度。

```python
import time
import torch

def step_seconds(loader, model, use_fake, fake_batch):
    batch = fake_batch if use_fake else next(loader)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    model(**batch).loss.backward()
    torch.cuda.synchronize()
    return time.perf_counter() - t0
```

## 追问

**验证集一跑，训练吞吐掉一截？**
验证把 GPU 占满，训练的预取被挤掉。评估放到旁路，或者隔很多步才跑，不要每步同步评。
