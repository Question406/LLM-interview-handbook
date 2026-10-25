---
id: xai-grok-moe
section: xai
order: 2
level: S
title: xAI：Grok 类 MoE 服务，decode 时专家并行和 batch 不齐怎么讲
quick: "MoE decode 每步只有 $B$ 个新 token，路由后各专家拿到的小 batch 不齐，每层两次 all-to-all 和热点专家会拖慢整层。以公开 Grok-1 的 314B、8 专家、top-2 为例，先算负载与通信，再考虑降低 decode EP 宽度、连续 batching 或复制热点专家。"
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

MoE decode 难在每步 token 少，还要把它们分发到不同专家：每个专家的 GEMM 小且不齐，整层又要等最慢专家和通信。可以用公开 Grok-1 的 top-2 / 8 专家结构解释这个问题，再按 prefill 和 decode 分别选并行度。

这道系统题依据 Grok-1、Mixtral / Switch 的公开机制，并非能点名某次 onsite 的逐字题。Grok-1 公开配置是 314B、8 专家、每 token 选 2 个、约 25% 权重激活、64 层、Q 48 头 / KV 8 头、$d=6144$。官方 JAX 示例注明 MoE 层以正确性为目标，没有做高效实现。后续 Grok 没有同等开源结构图，所以这里不推断内部 EP 拓扑、卡数或线上专家数。

Attention 仍按序列；FFN 换成专家。token $x$ 经 router 得 $p(i)$，取 top-$k$（Grok-1 公开是 $k=2$）：

$$
y=\sum_{i\in\mathrm{TopK}} p(i)\,E_i(x).
$$

专家并行（EP）把专家分放到不同卡。一层用两次 all-to-all，dispatch 把 token 送到选中的专家，combine 再送回原位。Prefill 的序列长、$T$ 大，通信更看带宽；decode 每条序列每步只有 1 个新 token，只传 $B\cdot k$ 份隐状态，固定启动开销就会更突出。

decode 的 $h$ 是 `[B, 1, d]`，路由后各专家收到长度不同的列表，不能统一当作 `[B, d]`。仓库里把 8 个专家都算完再 mask 的示例能验证数值，但还会读取未选专家权重，不适合作为高效 decode 路径。

例如 $B=32$、$k=2$、$E=8$ 时，平均每个专家 8 个 token，实际却可能一张卡收到 20、另一张收到 0。收到 20 的 GEMM 和最慢的 all-to-all 决定这一步耗时，空专家也要参加同步。

$B$ 个 token、top-2、8 专家，期望每个专家 $Bk/E=B/4$ 个 token。$B$ 小时泊松波动很大。All-to-all 同步，最慢那个专家的计算加最慢那条链路卡住整层。64 层就是每步上百次这样的同步。

训练可以用 aux loss 把专家占用 $f_i$ 和平均路由概率 $P_i$ 拉齐。推理没有反向，负载靠放置：热/冷专家绑同一张卡、复制热专家，或 capacity 溢出时 drop / 改路由。drop 改质量，复制改显存和通信。Capacity 粗算 $C=\gamma\cdot (Bk)/E$，$\gamma$ 是 capacity factor；decode 的 $Bk/E$ 经常小于 1，再设 $\gamma$ 也填不满 Tensor Core tile。

Prefill 一次几千 token，较宽 EP 有机会分摊计算；decode 更需要短往返，过宽 EP 会增加等待。可以考虑 prefill/decode 分离，使用两套并行度并传递 KV。连续 batching 增大 $B$，也是把专家 GEMM 做大的主要办法；并发不足时，all-to-all 可能吃掉稀疏激活的收益。入口如何提供和限制并发，见 `xai-rate-limiter`。

因此不能从稀疏激活直接推出 decode 一定更快，还要测路由同步和权重带宽。Grok 线上专家数和通信库未公开；集群故障与 checkpoint 另见 `xai-colossus`。

和 dense decode 对比：dense 一步是一次大 GEMM，batch 不齐最多是 padding；MoE 一步是「路由 + 两次 all-to-all + 一堆小 GEMM」，batch 不齐会变成专家之间的空等。同步点要说清楚。

## 追问

**为什么不把 8 个专家都放一张卡？**
Grok-1 量级单卡放不下全部专家权重。EP 换的是显存，代价是每层两次集合通信。
**和 dense 张量并行比？**
TP 切同一块矩阵，每层 all-reduce，负载齐。EP 切不同专家，负载不齐。8 专家 $k=2$ 也可以 EP 叠 TP，先画清通信再叠。
**Router 在 decode 会抖吗？**
会。同一前缀 greedy 应对齐；采样时专家选择随 token 变，负载均衡看窗口统计，不是一步一迁。
**官方示例为什么慢？**
正确性实现会算未选专家或走通用 gather。生产要 fused dispatch 加分组 GEMM。承认没写过 kernel 比装熟好。

- [[xai-moe-decode]]：同为 xAI 的续篇，和本题部分重合，只收 decode 一步专家负载不齐和连续 batch 碎片。
- [[meta-llama-moe]]：同样的「公开架构 + EP 服务」问法，换成 Llama 4 的 shared + top-1、dropless。
- [[google-gemini-moe]]：Google 版，多讲专家容量和丢 token，decode 成本的结论和本题一致。
- [[google-moe-routing]]：路由 permute、容量 pad 的实现，以及 decode 时降 EP 度、复制热点专家。
