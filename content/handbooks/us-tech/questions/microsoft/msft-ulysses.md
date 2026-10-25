---
id: msft-ulysses
section: microsoft
order: 13
level: S
title: Microsoft：DeepSpeed Ulysses 序列并行，和 Megatron SP 对照
quick: "Ulysses 先按序列分片，注意力前 all-to-all 换成全长序列加部分头，计算后再换回来。每链路约 $4Nh/P$，适合长序列且头数够分的训练 / prefill；Megatron SP 依附 TP，主要减少 LN 等激活副本，通信仍为 $O(N)$。"
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

Ulysses 通过两次 all-to-all 在序列分片与头分片间转换，既让每个注意力头看到完整序列，又不把全部头复制到每卡。比如序列长度和卡数同时加倍，按论文口径每链路字节量不变；小序列却可能被 all-to-all 启动开销拖慢。

ZeRO 处理状态副本，见 `msft-deepspeed-zero`，激活仍随 $B\cdot T\cdot L\cdot d$ 增长。几十 k 到百万长度需要另管激活。本卡依据 DeepSpeed-Ulysses（2023）和 Korthikanti 等的 Megatron SP 公开工作，`realInterview: false`，名词对照见 `sys-seq-parallel`。

## 看布局怎样变化

输入每卡 $[B, N/P, h]$，$N$ 是序列长，$P$ 为序列并行度，$h$ 为 hidden。QKV 本地投影后，all-to-all 变成 $[B, N, h/P]$，每卡拿全长序列的一部分头，在本地完成 softmax 注意力。实现 attention-agnostic，可接 FlashAttention。

再 all-to-all 将输出变回 $[B, N/P, h]$，MLP 和 LayerNorm 继续按序列分片。这里没有第三次将完整激活 all-gather 到每卡，也没有沿环传 $K,V$。

QKV 合计 $3Nh$，输出 $Nh$，all-to-all 每链路约 $M/P$，每层合计：

$$
\frac{4Nh}{P}.
$$

因此 $N$ 与 $P$ 同比增加时，每链路体积不变。Megatron SP 则在 TP 中让 LayerNorm / dropout 按 $T$ 切，列并行 GEMM 前 all-gather、行并行后 reduce-scatter；两次 gather 与两次 scatter 每链路约 $4Nh$，all-gather 在大 $P$ 下仍接近整份 $M$，不随 $P$ 下降，复杂度为 $O(N)$，Ulysses 为 $O(N/P)$。

| | Ulysses | Megatron SP（Korthikanti） |
| --- | --- | --- |
| 并行轴 | 纯序列；注意力时改成切头 | 必须配 TP，切 LN/MLP 的序列副本 |
| 注意力布局 | all-to-all 得到全长、少头 | 先 gather 成 TP 需要的完整激活 |
| 每链路体积 | $\sim 4Nh/P$ | $\sim 4Nh$（不随 $P$ 降） |
| 状态分片 | 常叠 ZeRO-3 | 参数仍按 TP 切，不是 ZeRO 那套 |
| 上限 | $P \le$ 注意力头数（还要能整除） | $P$ 等于 TP 度 |

## 依据容量瓶颈选择

模型状态不够先看 ZeRO；激活随 $T$ 超预算、头数够分时可用 Ulysses，产品评测见 `msft-long-context`。已有 Megatron TP、只需减少 LN 激活副本时，SP 可直接解决。

Ulysses 转置后每卡至少拿一个头，因此 $P$ 受头数和整除限制，GQA 小模型尤其容易遇到上限。Ring Attention / Megatron context parallel 用 P2P 传 KV 块并重叠通信计算，可超过头数但会切碎本地 GEMM；USP 将 Ulysses 与 Ring 组成 2D，这是后续方案，不能归进原 Ulysses 论文。

all-to-all 并非总比 all-gather 快，论文优势依赖较大 $N$ 与相应 $P$。小 $N$ 配大 $P$ 的启动成本可能超过收益，要用实际通信与计算曲线判断，而非只看 7B / 30B 宣传 TFLOPS。

## 追问

**与流水线并行能一起用吗？**
能。PP 切层，Ulysses 切 $T$，先固定 PP，再画 SP 组与微批形状。

**数值不一致先查哪里？**
all-to-all 数学上只是重排，先短序列对单卡，再查头整除和 GQA KV 复制切分。

**逐 token decode 也用吗？**
decode 新 token 的 $N=1$，没有足够序列可切。Ulysses 更适合训练和 prefill，在线长文本还可分段检索，见 `msft-long-context`。
