---
id: msft-ulysses
section: microsoft
order: 13
level: S
title: Microsoft：DeepSpeed Ulysses 序列并行，和 Megatron SP 对照
quick: >-
  Ulysses 按序列切样本，注意力前 all-to-all 把布局换成「整段序列、一部分头」，算完再 all-to-all 回去。每链路通信约 $4Nh/P$，和 $N$ 与 $P$ 同比放大时体积不变。Megatron SP 绑在 TP 上，all-gather / reduce-scatter 每链路仍是 $O(N)$。Ulysses 的 $P$ 不能超过注意力头数。
tags:
  - Microsoft
  - DeepSpeed
  - Ulysses
  - Sequence Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSpeed Ulysses
    url: https://arxiv.org/abs/2309.14509
    type: primary
  - title: DeepSpeed Ulysses blog
    url: https://www.microsoft.com/en-us/research/blog/deepspeed-ulysses-system-optimizations-for-enabling-training-of-extreme-long-sequence-transformer-models/
    type: primary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
  - title: USP — Unified Sequence Parallelism
    url: https://arxiv.org/abs/2405.07719
    type: secondary
---

## 题怎么来的

微软训练系统 / DeepSpeed 岗问长序列，不会只问 ZeRO。ZeRO 切的是 **参数副本**（见 `msft-deepspeed-zero`）；激活仍跟 $B\cdot T\cdot L\cdot d$ 走，会议纪要和仓库级上下文要把 $T$ 开到几十 k、上百万，状态分片救不了激活墙。公开锚点是 DeepSpeed-Ulysses（2023）以及它和 Megatron-LM sequence parallelism（Korthikanti 等人）的对照。`realInterview: false`。系统课把 Megatron SP 和「按序列切注意力」容易混名，先划清，见 `sys-seq-parallel`。

## 一记 all-to-all：序列分片换成头分片

输入按序列切开：每卡持有 $[B, N/P, h]$，其中 $N$ 是序列长度，$P$ 是序列并行度，$h$ 是 hidden。QKV 仍在本地投影。注意力需要 **整段序列** 才能做 softmax，Ulysses 的办法不是把 $K,V$ 沿环传一圈，而是转置并行轴：

1. 对 Q、K、V 做 all-to-all：每卡变成 $[B, N, h/P]$，也就是 **全长序列、一部分头**。
2. 本地算这组头的注意力（可以接 FlashAttention，论文强调 attention-agnostic）。
3. 再一次 all-to-all，把输出变回 $[B, N/P, h]$，后面的 MLP、LayerNorm 继续走序列分片。

Shape 口播：前是「短序列、全头」，后是「长序列、少头」。没有第三次把完整激活 all-gather 到每张卡。

论文给的每链路体积：QKV 三次合计 $3Nh$，输出一次 $Nh$，all-to-all 在 $P$ 张卡上每链路大约 $M/P$，所以一层约

$$
\frac{4Nh}{P}.
$$

$N$ 和 $P$ 同比放大时（序列加倍、卡数加倍），每链路字节数不变。这是面试要能写出来的那一行。

## 和 Megatron SP：切的不是同一刀

Megatron-LM 的 sequence parallelism **绑在张量并行上**。LayerNorm / dropout 按 $T$ 切开，进列并行 GEMM 前 all-gather 序列，出行并行后 reduce-scatter。它解决的是：TP 之后 LN 激活被每张卡各存一份。通信体积论文口径是：两次 all-gather、两次 reduce-scatter，每链路大约 $4Nh$，**不随 $P$ 降**（all-gather 的每链路成本在 $P$ 大时仍接近整份 $M$，不是 $M/P$）。Ulysses 论文据此写：Megatron SP 复杂度 $O(N)$，自己是 $O(N/P)$。

对照表我只写机制，不背某次 7B / 30B 的 TFLOPS 宣传图：

| | Ulysses | Megatron SP（Korthikanti） |
| --- | --- | --- |
| 并行轴 | 纯序列；注意力时改成切头 | 必须配 TP，切 LN/MLP 的序列副本 |
| 注意力布局 | all-to-all 得到全长、少头 | 先 gather 成 TP 需要的完整激活 |
| 每链路体积 | $\sim 4Nh/P$ | $\sim 4Nh$（不随 $P$ 降） |
| 状态分片 | 常叠 ZeRO-3 | 参数仍按 TP 切，不是 ZeRO 那套 |
| 上限 | $P \le$ 注意力头数（还要能整除） | $P$ 等于 TP 度 |

第三刀别混进来：Ring Attention / Megatron context parallel 是 P2P 传 KV 块，通信和计算重叠，并行度可以超过头数，但本地 GEMM 被切碎。USP 把 Ulysses 和 Ring 叠成 2D，当作 follow-up，不要假装 DeepSpeed 论文里已经有。

## 怎么选，以及错法

我会按墙选：

- 模型状态塞不进：先 ZeRO，见 `msft-deepspeed-zero`。
- 激活随 $T$ 爆、头数还够分：Ulysses。长上下文产品评测见 `msft-long-context`。
- 已经在 Megatron TP 域、只是 LN 激活重复：Megatron SP，不必强行换 all-to-all。
- $P$ 要大于头数（GQA 小模型尤其容易撞）：Ulysses 单独不够，要 Ring / CP 或 2D。

常见误区是：把 Ulysses 说成「ZeRO-4」；把 Megatron SP 说成切注意力序列；认为 all-to-all 一定比 all-gather 慢（体积小时延迟可能更差，论文优势在 $N$ 很大且 $P$ 跟上的时候）。小 $N$ 开很大 $P$，all-to-all 启动开销会吃掉收益，和「小模型开 ZeRO-3」是同一类错误。

## 追问

- **为什么 $P$ 不能大于头数？** 转置之后每卡至少要分到一个头。头不够就有卡空转，或者你得改切 KV 头 / 再叠一维并行。
- **和流水线并行？** 正交。PP 切层，Ulysses 切 $T$。微批和序列分片会一起改激活形状，画图时先固定 PP 再画 SP 组。
- **数值和单卡不一致？** all-to-all 只是重排，数学上等价。先对短序列做单卡对照。掉点优先查头是否整除、GQA 的 KV 复制有没有切错。
- **推理 逐 token 生成（decode） 也上 Ulysses？** Decode 一步 $N=1$ 的新 token，序列并行没东西切。这是训练 / 输入预填充（prefill，即处理输入并建立缓存） 的工具。在线长上下文更常走分段检索，见 `msft-long-context`。
