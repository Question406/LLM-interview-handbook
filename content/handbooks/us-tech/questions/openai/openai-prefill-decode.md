---
id: openai-prefill-decode
section: openai
order: 11
level: A
title: OpenAI：prefill 和 decode 计算形态差在哪，调度为什么要拆
quick: >-
  Prefill 一次吃整段 prompt，$Q$ 是 $[B,H,S,D]$，算力密集；decode 每步 $Q$ 是 $[B,H,1,D]$，时间砸在读历史
  KV，带宽密集。混在一个 batch 里会让长 prefill 堵住别人的 decode。调度拆开才能选不同并行度和批大小。
tags:
  - OpenAI
  - Prefill
  - Decode
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DistServe — Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

ChatGPT 类服务的延迟拆成「第一个 token」和「后续 token」。OpenAI 推理 / 系统岗会问你为什么不能用训练时那套大 GEMM 去调度在线流量。公开系统论文里 DistServe 把 prefill 和 decode 拆到不同机器；我按计算形态答，不编造内部集群拓扑。KV 正确性见 `openai-kv-cache-impl`。

## 两种算术强度

**Prefill。** 输入 `[B, S, d]`，$S$ 可达数千。投影是大 GEMM，注意力若用 FlashAttention 也不反复写 $[B,H,S,S]$ 的分值矩阵。算术强度高，GPU 算得动，瓶颈常是计算或激活显存。TTFT（第一个 token）几乎等于这一次前向。

**Decode。** 每步只来 1 个新 token：$Q$ 是 `[B, H, 1, D]`，但要把 cache 里 `[B, H_kv, t, D]` 的 $K,V$ 从 HBM 读进来。计算量 $O(t d)$，数据量也 $O(t d)$，强度接近 1。步数等于生成长度，墙钟被带宽和 kernel launch 吃掉。GQA 降的就是这个读量，见 `google-gqa-mqa`。

所以「Transformer 是 $O(T^2)$」只描述 prefill 注意力；decode 有 cache 之后是逐步线性，但被内存绑住。两者的 MFU 曲线完全不同，不能共用一个「把 GPU 打满」的 batch 启发式。

我会现场估一笔账。70B、GQA、$d_{\mathrm{head}}=128$、$H_{\mathrm{kv}}=8$、一层 KV 大约 $2\cdot t\cdot 8\cdot 128$ 个元素。$t=4\mathrm{k}$、bf16 就是数 MB 每层，乘层数后每步 decode 要扫过几百 MB 历史，而这一步的 FLOPs 只有一个 `[1, d]` 的投影加 $O(t d)$ 点积。

Prefill 同一 $t$ 则是完整 $B=1$ 的大矩阵乘，算术强度高一个数量级。数字不必精确到字节，但方向必须对：decode 加 batch 是为了把那次 HBM 扫描摊开，不是为了再堆 FLOPs。

## 调度为什么要拆

静态大 batch 里塞进一个 8k prefill，同 batch 的 decode 请求要等这次重计算做完，TTFT 和 TPOT 互相拖死。这就是拆的原因：

- **批大小。** Decode 靠大 batch 摊 HBM；prefill 太大 batch 会爆激活，反而要切 chunk。
- **并行。** Prefill 吃张量并行的大 GEMM；decode 更在意 replica 和 KV 布局，TP 切太碎会让每步同步盖过计算。
- **硬件。** 高算力卡跑 prefill，高带宽 / 便宜卡跑 decode，中间传 KV。DistServe 的点是 goodput：满足 TTFT 和 TPOT SLO 的吞吐，不是裸 tokens/s。
- **chunked prefill** 是折中：把长 prompt 切成小块和 decode 交替，减轻队头阻塞，但仍在同一套执行器里抢算力。彻底拆是把 KV 作为跨池产物交出去。

投机解码的验证步又是一小段 prefill，见 `openai-speculative-decoding`。调度器要把「验证 prefill」和「用户 prompt prefill」当同一类计算，不要塞进 decode worker 的带宽假设里。

KV 从 prefill 池交到 decode 池有拷贝或 RDMA 成本。上下文越长，这次搬运越像一次小型 all-gather。拆得不偿失的工作点是：短 prompt、短生成、机器间带宽差。面试要能说出「什么时候不拆」：单机、队列里几乎没有长短混合时，chunked 就够。

错法：把 TTFT 优化说成「再开大一点 decode batch」。decode batch 摊的是 KV 带宽，帮不上正在跑的那次 prompt GEMM。反过来，给 decode worker 堆更强的 tensor core、却把 KV 放在带宽差的卡上，也是看错形态。

量化 KV 同理：它降 decode 读带宽，对 prefill GEMM 几乎没帮助，别拿来当 TTFT 的主杠杆。

面试收尾：拆的是 **资源画像**，不是两套权重。权重可以复制；KV 必须跟着 decode 走，迁移 KV 的代价要算进 SLO。

## 追问

- **训练为什么不拆？** 训练每步都是满 $T$ 的正反向，没有「一个 token 的自回归循环」。
- **第一 token 慢一定是 prefill？** 也可能是排队、tokenizer、或者 batch 里被别的长 prompt 堵住。先看队列再看 kernel。
- **paged KV 能代替拆分吗？** 不能。paging 解决显碎片，见 `openai-continuous-batching`。拆分解决两种 kernel 的资源画像。
- **MoE decode 呢？** 每步还要 all-to-all 专家，decode 更不像 dense GEMM，更不能和 prefill 混排。
