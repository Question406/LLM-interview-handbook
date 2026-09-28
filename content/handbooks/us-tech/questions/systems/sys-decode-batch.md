---
id: sys-decode-batch
section: systems
order: 30
level: A
title: 系统：decode batch 动态，结束序列腾槽、inflight
quick: >-
  Inflight 是此刻正在一步 decode 的序列，不是排队里的总数。eos 或长度上限一到，立刻还页、还计算槽，waiting
  里补人。有效 $B$ 决定能不能喂饱 decode GEMM；CUDA graph 按几档上限 pad，不要每步重捕获。
tags:
  - vLLM
  - NVIDIA
  - DistServe
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: "Orca: A Distributed Serving System for Transformer-Based Generative Models"
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: primary
  - title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving"
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: Continuous batching from first principles
    url: https://huggingface.co/blog/continuous_batching
    type: secondary
---

## 题怎么来的

Orca 把调度改到 iteration 级，TensorRT-LLM 叫 in-flight batching，vLLM / TGI 叫 continuous batching。`sys-cont-batch` 讲为什么静态 batch 有洞；本题把镜头放在 decode 池里的槽位：谁算 inflight、结束怎么腾、新请求凭什么进来、图捕获怎么跟动态 $B$ 共存。NVIDIA 岗见 `nvidia-inflight-batch`。Agent 把槽挂起而不结束，见 `sys-agent-sched`。

## Inflight 是算力集合，不是队列长度

我会先对齐口径。记 `max_num_seqs` 为槽上限，$B_{\mathrm{run}}$ 为本步真正 launch 的序列数，$B_{\mathrm{wait}}$ 为排队。Inflight 在面试里应等于 $B_{\mathrm{run}}$（外加本步混进来的 prefill 块），不含 `tool_wait`、不含已经 eos、不含还在 CPU 上的 KV 命中提升。产品仪表若把「已接收未完成」都叫 inflight，要当场对齐口径，否则和 GPU 利用率对不上。

每一步大致：

1. 看上一步的 token：eos / stop / `max_tokens` / 客户端取消。命中则从 running 摘掉，block table 还进 free list，引用计数减到 0 的物理页回池，见 `sys-paged-attn`。
2. 看预算：槽位 $B_{\mathrm{run}} \lt S_{\max}$（`max_num_seqs`），KV 页够，且本步 token 数不超过 `max_num_batched_tokens`。
3. 从 waiting 准入。优先补 decode（memory-bound，需要 $B$ 喂权重带宽），还是塞一块 chunked prefill，是 SLO 问题：TTFT 紧就塞 prefill，TPOT 紧就保护 decode，见 `sys-chunked-prefill`。
4. 组元数据：`kv_indptr`、`last_page_len`、采样参数，交给核，见 `sys-flashinfer`。

结束腾的是两样：计算行和 KV 页。只腾计算、页按 `max_len` 占着，新请求没有地方写，Orca 的调度会在显存上失败。只腾页、计算仍走稠密 padded GEMM，结束行还在做 mask 废乘加。Ragged / packed kernel 和分页要一起开。

具体形状：上限 32 槽。某步 28 条 decode + 1 条 512 token 的 prefill 块。3 条 eos，还 3 槽和对应页；waiting 里有 5 条，只能再进 3 条（或更少，若 KV 不够）。下一步仍约 29 条活着。静态 batch 里那 3 个空槽会一直陪到全局最长。这就是动态 decode batch 的全部好处：洞在 iteration 边界就被填上。

## 动态 $B$、图、和准入策略

Decode GEMM 的 $M=B_{\mathrm{run}}$。$B$ 太小，读完整份权重摊不薄，FP8 也救不了，见 `sys-fp8-gemm`。$B$ 开到 KV 爆边，每步读的历史 KV 变长，TPOT P99 先坏。Frontier 是 SLO 内 goodput，不是瞬时 tokens/s。

CUDA graph：捕获固定 shape。做法是几档 $B\in\{1,2,4,8,16,32\}$，本步 pad 到 $\ge B_{\mathrm{run}}$ 的最近档。活着的用 `last_page_len` / 有效掩码。每步 $B$ 变就重捕获，启动税比一步 decode 还贵。FlashInfer 采样的 seed 也要做成 GPU tensor，才能进图，见 `nvidia-cuda-graph`。

准入还会踩：

- **KV 水位。** 新 decode 预留的不是 1 页，是「还要生成的上限」的悲观估计，否则生成到一半 OOM 再抢占，P99 更差。乐观分配 + 抢占（把某条卸 CPU）是另一套，见 `sys-kv-offload`。
- **长短公平。** 短请求一直插，长请求饿死；只跑长请求，槽被占满。Aging / 配额。
- **结束突刺。** 很多序列同时 eos（齐步的 batch 作业），$B_{\mathrm{run}}$ 塌一下，下一档 graph 更瘦。作业负载要预期这个锯齿；在线 chat 通常更平滑。
- **PD 分离。** Decode 池的 inflight 不应被大 prefill 污染。大 prefill 在另一池，搬完 KV 再进入 decode inflight，见 `sys-prefill-decode-disagg`。单池则靠 chunked 把 prefill 块大小卡在 token 预算里。

Prefix / radix 命中的请求进入 decode 池时，prefill 后缀可能很短，几乎像直接 inflight。命中率高时 decode 池更满、KV 更紧，要重新调 KV 预留比例，见 `sys-radix-tree`。

错误说法：inflight 等于当天 QPS；结束序列可以等整图跑完再回收；`max_num_seqs` 开到显存极限吞吐最好；没有分页也能靠把 batch 开大吃满 GPU。前三条把口径和回收弄反了，后一条会在碎片上先 OOM。

监控：$B_{\mathrm{run}}$、槽利用率、KV 使用率、每步结束条数、因 KV 不足无法准入的次数、graph 档位分布、P99 TPOT。$B_{\mathrm{run}}$ 长期远小于上限，不是「还有余量」，是 waiting 空或 KV 碎片导致补不进去。

## 追问

- **结束为什么必须还页？** 不还页等于内部碎片。动态 batch 的内存前提是分页回收，见 `sys-paged-attn`。
- **Inflight 含排队吗？** 不含。排队不占 SM。含了就会出现「inflight 很高、GPU 很空」。
- **和 continuous batching 重复吗？** 那张卡讲洞和 iteration 粒度。这张卡讲 decode 槽、inflight 口径、graph 分档、准入预算。
- **eos 和 tool_wait 一样腾槽吗？** 都离开 running。eos 释放 KV（或插入 radix 后降引用）；tool_wait 挂起 KV，见 `sys-agent-sched`。
- **为什么要 token 预算不只看条数？** 一条 8k prefill 块和 32 条 decode 的 FLOPs / 墙钟完全不同。`max_num_batched_tokens` 封的是一步毫秒。
- **$B$ 突然掉一半？** 齐步结束或抢占。看结束直方图。作业负载要错开 max tokens；在线负载更该查是不是准入被 KV 堵住。
