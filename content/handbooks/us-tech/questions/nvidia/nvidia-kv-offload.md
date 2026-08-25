---
id: nvidia-kv-offload
section: nvidia
order: 24
level: A
title: NVIDIA：KV 卸到 CPU / NVMe，何时带宽还不如量化
quick: >-
  热 KV 每步都要从 HBM 读，H100 大约 3 TB/s；PCIe 5.0 x16 大约 64 GB/s，NVMe 再低一截。Decode
  工作集走卸载，墙钟会被 PCIe 打死。卸载只适合冷前缀、暂停请求、多轮里暂时不飞的块。容量问题先
  FP8 KV / GQA / 分页，热路径量化几乎总比搬去 CPU 快。
tags:
  - NVIDIA
  - KV Cache
  - Offload
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: KV Cache System — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/features/kvcache.html
    type: primary
  - title: KV Cache Offloading — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/examples/llm_kv_cache_offloading.html
    type: primary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: FlexGen — High-Throughput Generative Inference of Large Language Models with a Single GPU
    url: https://arxiv.org/abs/2303.06865
    type: primary
---

## 题怎么来的

长上下文一上，评委就会问「HBM 不够把 KV 丢 CPU 行不行」。TensorRT-LLM 的 KV 文档有 `host_cache_size`：GPU 页淘汰前可以卸到 pinned host，命中再搬回来。官方 issue 写过：原生是 host DRAM，不是 GDS 直打 NVMe；NVMe / 远端要用 KV connector 自己写。FlexGen 是单卡吞吐路线，把层间权重和缓存在 GPU / CPU / 盘之间切，和在线 decode 的 SLO 不是同一题。我会先报带宽数字，再画热 / 温 / 冷。

## 三层带宽差的是数量级

一步 decode 要扫当前序列的全部 KV（GQA 之后仍是 $\Theta(T)$ 字节）。量级：

$$
\mathrm{HBM}\sim 3\ \mathrm{TB/s},\quad
\mathrm{PCIe\ 5.0\ x16}\sim 64\ \mathrm{GB/s},\quad
\mathrm{NVMe\ seq}\sim 7\text{--}14\ \mathrm{GB/s}.
$$

HBM 到 PCIe 大约快 $50\times$；到 NVMe 再差几倍，而且是顺序峰值，随机 16–64 token 的页更惨。设一层 KV 每 token $c$ 字节（含 K 和 V、所有 kv head）。读 $T$ 个 token 的时间下界 $Tc/B_{\mathrm{bus}}$。$T=32\mathrm{k}$、$c=256\,\mathrm{B}$ 量级时，HBM 是几十微秒，PCIe 是毫秒，NVMe 可以到十毫秒。Decode 的 TBT SLO 若是 50 ms 量级，**热路径每步从 CPU 流一遍 KV** 会直接打穿。

所以卸载不是「把 cache 变大就加速」。它只增加 **容量**。命中冷页时，你在用一次 PCIe 拷贝换一次重算 prefill。拷贝划得来，当且仅当这块 KV **不是每 token 都读**。

TRT-LLM：`host_cache_size` 分配 pinned host 二级池；GPU 页按优先级淘汰。`secondary_offload_min_priority` 以下的块不卸、直接丢，避免低价值块把 PCIe 打满。演示脚本把 GPU `max_tokens` 故意设很小，才能看见 reused blocks——生产上若 GPU 池已经装得下工作集，卸载路径不该被踩热。

## 何时量化更好

量化改的是热路径的 $c$。fp16 到 FP8，$c$ 减半，HBM 流量减半，同一池能装大约 2 倍 token，见 `nvidia-fp8-kv`。W4 改的是权重，不改 KV，见 `nvidia-w4a8`。GQA 减 $H_{\mathrm{kv}}$，和量化正交。

经验规则我面试就这么说：

1. **正在飞的 decode 工作集** 必须留在 HBM。先 GQA / FP8 KV / 更小 page 碎片，见 `nvidia-paged-kv`。
2. **量化把热集装进 HBM 了**，就不要为这批请求开 host offload。PCIe 再快也快不过半精度变 FP8 的那一倍 HBM。
3. **卸载留给冷数据：** 共享 system prefix 的二级副本、刚结束但可能多轮接着来的会话、被抢占暂停的请求、disagg 里 prefill 节点做好等 decode 节点来拉的块。
4. **NVMe** 只当「比重算 prefill 便宜的归档」。128k 会话的冷前缀可以落盘；当前生成那 4k 窗口不行。LMCache 一类社区方案走这条，TRT-LLM 要自己接 connector。

错法：把 FlexGen 的「单卡跑 175B、追求 token/s」搬到在线 chat。FlexGen 用大 batch、层间换入换出换吞吐，TTFT / TBT 不是目标。在线 IFB 每步都有活着的 $B$ 条序列，它们的 KV 全是热的，见 `nvidia-inflight-batch`。

## 和重算比一笔账

卸载命中：PCIe 搬 $T\cdot c$ 字节。重算：对这 $T$ 个 token 再跑一遍 prefill，算力墙，但数据已在 HBM。短前缀重算往往更快更简单；长文档前缀、带图的视觉 token，重算很贵，值得留 host 副本。Prefix 已经在 GPU 上 refcount 共享的，不要再卸一份重复。

UVM（`use_uvm`）看起来省事，缺页延迟不可控，serving 很少当主策略。Disagg 的 KV 走 RDMA 到 decode 池，那是机间搬，带宽比 PCIe 好，但仍要量化压体积。

## 追问

- **FP8 KV 再卸 host 有意义吗？** 有，冷容量可以再翻倍。热 decode 仍从 HBM 读 FP8。不要「FP8 了所以可以每步从 CPU 读」。
- **block 很小更好卸吗？** 页太小，PCIe 事务碎、随机 I/O 更差。卸载粒度往往比 attention tile 更粗。
- **和 chunked prefill？** 切块降低的是一步工作集，不是把 KV 赶出 GPU。两件事可以叠，但热 KV 还在卡上，见 `nvidia-chunked-prefill`。
- **TRT-LLM 能直接打 NVMe 吗？** 文档路径是 host pinned；盘 / 远端走 KV connector。面试不要吹 GDS 是内置开关。
