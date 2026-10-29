---
id: sys-kv-offload
section: systems
order: 23
level: A
title: 系统：KV 分层存储，HBM / CPU / 盘和命中率
quick: >-
  正在 decode 的 KV 要留在 HBM，已完成或暂停的前缀可以卸到 CPU，再把更冷的块放到盘上，命中时整块提升回来。这样把慢介质的成本放在首
  token 等待里，避免每步生成都等换页。命中率要按 GPU、CPU 和盘分别报，还要检查 CPU 池是否真的扩大了缓存容量。
tags:
  - vLLM
  - Serving
  - KV Cache
  - DistServe
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: KV Offloading Usage Guide — vLLM
    url: 'https://docs.vllm.ai/en/latest/features/kv_offloading_usage/'
    type: primary
  - title: Example — Offload KV cache to CPU — LMCache
    url: 'https://docs.lmcache.ai/getting_started/quickstart/offload_kv_cache.html'
    type: secondary
  - title: >-
      DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM
      Serving
    url: 'https://arxiv.org/abs/2401.09670'
    type: primary
  - title: >-
      Efficient Memory Management for Large Language Model Serving with
      PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
---

## 可以这样回答

KV 分层存储适合把暂时不用、以后可能命中的前缀卸到 CPU 或盘，正在 decode 的页仍留在 HBM。比如同一份长文档下一轮还会被问到，可以命中后整块提升回来，少算一次 prefill；每生成一个 token 都从盘读历史，则会把延迟拉长。vLLM OffloadingConnector 和 LMCache 提供了公开实现，分页见 `sys-paged-attn`，前缀复用见 `sys-prefix-cache`。DistServe 的跨池传 KV 也需要计算搬运成本。

## 技术备查

KV 分层存储适合把暂时不用、以后可能命中的前缀卸到 CPU 或盘，正在 decode 的页仍留在 HBM。比如同一份长文档下一轮还会被问到，可以命中后整块提升回来，少算一次 prefill；每生成一个 token 都从盘读历史，则会把延迟拉长。vLLM OffloadingConnector 和 LMCache 提供了公开实现，分页见 `sys-paged-attn`，前缀复用见 `sys-prefix-cache`。DistServe 的跨池传 KV 也需要计算搬运成本。

先估算一份 KV 的体积：一份 KV 大约 $2\cdot L\cdot n_{\mathrm{kv}}\cdot d_h\cdot T\cdot b$ 字节。Decode 每步都要把历史 K/V 从 HBM 读进 SM，强度低，走带宽墙。分层只能是：

**HBM（热）：**
在飞 decode 的页、马上要用的公共前缀。这一层的容量决定 `max_num_seqs`。
**CPU pinned（温）：**
已完成的前缀块、暂停请求、刚结束但可能被下一轮命中的页。vLLM 用异步 DMA 和计算重叠，把写完的 GPU 块拷到 host。
**盘 / 远端（冷）：**
超长文档前缀、跨 replica 共享。二级介质不能直接喂 GPU，必须经 CPU 中转。NVMe 或 RDMA 的延迟是毫秒到几十毫秒，只能摊在 首个 token 的等待时间（TTFT） 上，不能摊在每个 decode token 上。

带宽数量级要报出来：HBM 数 TB/s，主机 DDR 一两百 GB/s，PCIe 5 x16 大约 64 GB/s，盘再低一到两个数量级。32 路 decode、每步各读几百 MB 的 KV，只可能走 HBM。CPU 层的正确用法是 **整块前缀的命中提升**，不是逐步换页。

生产上很少把在飞 KV 当操作系统缺页去 swap，见 `sys-paged-attn`。分层存储是前缀缓存的延长，不是 decode 的 backing store。vLLM 文档说明：OffloadingConnector 扩展的是 prefix cache；块在 GPU 上算完就异步卸到慢层，命中再 promote 回 GPU。

还要分清两个「CPU offload」：`--cpu-offload-gb` 卸的是权重，每步还要搬回来算；LMCache 的本地 CPU 开关才是 KV 介质。混成一个旋钮，账会全错。

单层 CPU 要大于所有卡 GPU KV 之和。卸是立即的，CPU 池若只是 GPU 的镜子，命中率不会比 GPU prefix cache 更高，只增加一次拷贝开销。多级时 CPU 要够大，少把热点前缀打到盘上。

统计命中时，我会按介质拆开：

**GPU hit：**
在飞或 GPU 前缀池，TTFT 只剩后缀 prefill。
**CPU hit：**
一次 DMA 提升，TTFT 加拷贝；对 2k 系统提示通常仍远小于重算。
**Disk hit：**
中转加排队，只适合超长、极热、能接受百毫秒的文档头。
**Miss：**
全量 prefill。

错命中比 miss 贵：token ID、模型版本、LoRA、位置语义都要进 key，和 `sys-prefix-cache` 同一套。tenant isolation 也要进 key。

PD 分离时，prefill 池算完的 KV 本身就要搬到 decode 池，见 `sys-prefill-decode-disagg`。分层是时间上的复用，分离是空间上的搬家，可以叠：prefill 侧命中 CPU 前缀，少算一遍再传。网络体积仍跟 $T\cdot b$ 走，FP8 KV（见 `sys-kv-quant`）对搬运和 offload 都划算。

错误说法：把在飞 decode 页卸到 CPU 还能保持 TPOT；命中率 90% 就一定降 P99（热点前缀挤掉在飞页，或每次 hit 都走盘）；权重 offload 和 KV offload 混成一个旋钮。

淘汰：GPU 不够时先卸不在飞的叶子前缀，不要卸正在 decode 的最后一页。CPU 满了再冷到盘。监控 promote 延迟、各层 hit、因命中少算的 prefill token，以及在飞 KV 被挤出的次数。Agent 等工具是秒级，KV 可卸 CPU，见 `sys-agent-sched`。

## 追问

**Decode 能不能逐步从 CPU 读 KV？**
不能当默认。PCIe 喂不饱 memory-bound 的逐步 attention。CPU 层用于整块前缀提升或抢占，不是缺页。

**CPU 池要多大？**
单层至少大于聚合 GPU KV，否则只是镜子。给主机其它进程留余量。

**盘层为什么必须经 CPU？**
GPU 不能直接随机读 NVMe 页表。二级只跟 CPU 主层说话，再 DMA 上 GPU。

**和 PD 分离冲突吗？**
不冲突。分离搬的是一次请求的 KV；分层复用的是跨请求前缀。体积公式同一套。

**命中率很高但 TTFT 变差？**
查 hit 落在哪一层。Disk hit 计入命中率，实际耗时可能比 GPU miss 后的短 prefill 还差。

**暂停的 agent 请求卸哪？**
工具等待是秒级，KV 可卸 CPU，回来再 promote。见 `sys-agent-sched`。

## 相关题

- [[nvidia-kv-offload]]：同一机制的 NVIDIA 问法，侧重 PCIe 带宽算账和什么时候量化比卸载划算，和本题几乎可以当一题复习。
- [[sys-kv-quant]]：先把 KV 压窄再谈分层，讲 INT8/FP8 KV 的 scale 怎么定。
