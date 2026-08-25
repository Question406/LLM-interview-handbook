---
id: xai-grok-moe
section: xai
order: 2
level: S
title: xAI：Grok 类 MoE 服务，decode 时专家并行和 batch 不齐怎么讲
quick: >-
  公开的 Grok-1 是 314B、8 专家、每 token 激活 2 个（约 25% 权重）。Decode 一步只有 $B$ 个新
  token，专家并行靠 all-to-all；热专家拖住整层，冷专家 GEMM 太碎。先讲路由和容量，再讲
  prefill / decode 不该共用同一套 EP 宽度。
tags:
  - xAI
  - Grok
  - MoE
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Open Release of Grok-1
    url: https://x.ai/news/grok-os
    type: primary
  - title: xai-org/grok-1
    url: https://github.com/xai-org/grok-1
    type: primary
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

## 题怎么来的

xAI 推理 / 训练系统岗会拿 Grok 当入口，问 MoE 在 **decode** 为什么比 dense 更难调度。这不是某一份能点名的 onsite 逐字题。公开锚点只有 Grok-1：314B、8 专家、每 token 用 2 个、约 25% 权重激活、64 层、Q 48 头 / KV 8 头、$d=6144$。官方 JAX 示例写明：MoE 层为了正确性，**不是高效实现**。后续 Grok 没有同等开源结构图，我只拿 Grok-1 加 Mixtral / Switch 的公开机制讲，不装内部 EP 拓扑、卡数或线上专家数。

## Decode 一步，专家并行在同步什么

Attention 仍按序列；FFN 换成专家。token $x$ 经 router 得 $p(i)$，取 top-$k$（Grok-1 公开是 $k=2$）：

$$
y=\sum_{i\in\mathrm{TopK}} p(i)\,E_i(x).
$$

专家并行（EP）：每张卡只放一部分专家。一层两次 all-to-all——dispatch 把 token 送到被选专家，combine 送回原位。Prefill 时序列长，$T$ 大，all-to-all 吃带宽。Decode 每条序列每步 **1 个新 token**，payload 是 $B\cdot k$ 份隐状态。集体通信变成延迟墙：固定启动开销，不是 FLOP。

Shape 我先写：decode 的 $h$ 是 `[B, 1, d]`，路由后每个专家收到 **长度不齐** 的 token 列表，不是整齐的 `[B, d]`。仓库里那种「8 个专家都算再 mask」能对数值，decode 会把未选专家的权重也扫一遍，带宽当场炸掉。

数字感：若 $B=32$、$k=2$、$E=8$，期望每个专家 8 个 token。实际可能一张卡收到 20、隔壁收到 0。一步时间由 20 那个 GEMM 加最慢那条 all-to-all 决定，空专家仍要参加同步。

## Batch 不齐：热专家决定一步时间

$B$ 个 token、top-2、8 专家，期望每个专家 $Bk/E=B/4$ 个 token。$B$ 小时泊松波动很大。All-to-all 同步，**最慢那个专家的计算加最慢那条链路**卡住整层。64 层就是每步上百次这样的同步。

训练可以用 aux loss 把专家占用 $f_i$ 和平均路由概率 $P_i$ 拉齐。推理没有反向，负载靠放置：热/冷专家绑同一张卡、复制热专家，或 capacity 溢出时 drop / 改路由。面试要说清：**drop 改质量，复制改显存和通信**。Capacity 粗算 $C=\gamma\cdot (Bk)/E$，$\gamma$ 是 capacity factor；decode 的 $Bk/E$ 经常小于 1，再设 $\gamma$ 也填不满 Tensor Core tile。

Prefill 和 decode 对 EP 宽度是反的。Prefill 一次几千 token，宽 EP 摊得开；decode 要短往返，EP 太宽只是多等网。所以我会主动提 prefill/decode 分离：两套并行度，KV 搬过去。连续 batching 把 $B$ 做大，是 MoE decode 几乎唯一能把专家 GEMM 做实的办法。没有足够并发，稀疏激活的好处会被 all-to-all 吃掉。入口限流决定 $B$ 从哪来，见 `xai-rate-limiter`。

错法：把 MoE 说成「参数多、算力少，所以一定更快」。Decode 墙的是路由同步和权重带宽。也不要编 Grok 线上专家数、是否自研通信库。集群故障和 checkpoint 另开，见 `xai-colossus`。

和 dense decode 的对比我也会主动说：dense 一步是一次大 GEMM，batch 不齐最多是 padding；MoE 一步是「路由 + 两次 all-to-all + 一堆小 GEMM」，batch 不齐会变成专家之间的空等。面试听的是你有没有把同步点说出来。

## 追问

- **为什么不把 8 个专家都放一张卡？** Grok-1 量级单卡放不下全部专家权重。EP 换的是显存，代价是每层两次集合通信。
- **和 dense 张量并行比？** TP 切同一块矩阵，每层 all-reduce，负载齐。EP 切不同专家，负载不齐。8 专家 $k=2$ 也可以 EP 叠 TP，先画清通信再叠。
- **Router 在 decode 会抖吗？** 会。同一前缀 greedy 应对齐；采样时专家选择随 token 变，负载均衡看窗口统计，不是一步一迁。
- **官方示例为什么慢？** 正确性实现会算未选专家或走通用 gather。生产要 fused dispatch 加分组 GEMM。承认没写过 kernel 比装熟好。
