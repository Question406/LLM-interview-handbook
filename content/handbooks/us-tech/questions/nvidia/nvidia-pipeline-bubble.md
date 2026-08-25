---
id: nvidia-pipeline-bubble
section: nvidia
order: 4
level: S
title: NVIDIA：流水线气泡从哪来，1F1B / interleaved 怎么减
quick: >-
  气泡是 stage 在等上一站的激活或下一站的梯度，两端的 warmup / cooldown 最显眼。$P$ 个 stage、$M$
  个 microbatch，空转比例大约 $(P-1)/M$。1F1B 不减这段比例，减的是激活占用；interleaved 把每张卡切成
  $v$ 个虚 stage，气泡大约再除以 $v$。
tags:
  - NVIDIA
  - Pipeline Parallel
  - Megatron
  - 1F1B
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: NVIDIA Megatron-LM
    url: https://github.com/NVIDIA/Megatron-LM
    type: primary
---

## 题怎么来的

万亿训练几乎一定有流水线，见 `nvidia-trillion-train`。我会先画 $P$ 个 stage、$M$ 个 microbatch 的时空图，标出两端空槽，再区分：GPipe 和 1F1B 到底改了内存还是改了气泡，interleaved 为什么又能再削一刀。答「堆 microbatch」不够，要把 $P$、$M$、虚 stage $v$ 写上。

## 气泡从哪来

$P$ 张卡纵向切层。第 $k$ 个 stage 算 forward 必须等 $k-1$ 把激活送来；backward 必须等 $k+1$ 把梯度送回来。流水线还没灌满时，后面的卡闲着（warmup）；灌完最后一批 forward 之后，前面的卡闲着（cooldown）。稳态里如果各 stage 耗时一样，可以满载；切不均、P2P 没重叠、某个 stage 塞了 embedding / lm head，稳态也会冒泡。

GPipe 式 flush：先把 $M$ 个 microbatch 的 forward 全部推完，再统一 backward。气泡时间大约 $(P-1)$ 个 forward 加上 $(P-1)$ 个 backward，占一步总时间的比例

$$
\frac{P-1}{M+P-1}\approx\frac{P-1}{M}\quad (M\gg P).
$$

$M$ 必须明显大于 $P$，否则一半时间在填管子。这就是「microbatch 太少，流水线一定慢」的来源。

激活内存是另一笔账：flush 要给在途的所有 microbatch 留正向激活，$O(M)$ 份。$M$ 为了填泡泡变大，显存先爆。所以纯 GPipe 在深流水线上很难用。

## 1F1B 改的是内存，不是泡泡长度

1F1B（Megatron 用的 PipeDream-flush 一类）：先 warmup $P-1$ 个 forward，进入稳态后每个 stage 一次 forward、一次 backward 交替，最后 cooldown。两端仍然有 $P-1$ 个空槽，气泡比例还是 $\approx(P-1)/M$。

它便宜在激活：稳态里每张卡大约只挂 $O(P)$ 量级的 in-flight microbatch，而不是 $O(M)$。$M$ 可以开到几十去填泡泡，而不用把所有 forward 激活都留到最后。重计算仍然能再换一刀显存，但那是正交的。

错法：把 1F1B 说成「没有气泡」。Nsight Systems 上 warmup / cooldown 的空白还在；只是中间那段 GEMM 更密，激活峰值下来了。

## Interleaved 怎么把泡泡除以 $v$

Interleaved 1F1B：模型切成 $vP$ 段，每张卡拿 $v$ 个不连续的虚 stage。例如 $P=4$、$v=2$、8 层，卡 0 拿第 0 和第 4 层，卡 1 拿第 1 和第 5 层。同一张卡在一轮里会多次变成「流水线的上游 / 下游」，warmup 需要的空槽大约从 $P-1$ 降到 $(P-1)/v$。气泡比例近似

$$
\frac{P-1}{vM}.
$$

$v=2$ 是 Megatron 万亿博客里的常用值：泡泡减半，实现复杂度可接受。

代价：stage 边界变多，P2P 次数涨；调度更绕，microbatch 数目要能被更细的格子整除；虚 stage 太碎会变成一堆小 kernel，又回到 TP 过大那种 MFU 问题。$v$ 不是越大越好。

和张量并行的配合：节点内 TP、节点间 PP。PP 的 P2P 是点对点传激活 $[B_{\mathrm{micro}}, T, D]$，体积通常小于 TP 的 all-reduce，但延迟不能藏在 NVLink 里。气泡诊断优先看「是不是 $M$ 不够、stage 算力不均」，再看 NCCL。层内集合通信见 `nvidia-tensor-parallel`，两者不要混成一次 all-reduce。

## 追问

- **把 $M$ 开到极大？** 气泡比例下降，但数据并行的全局 batch 被 microbatch 拆碎，每步优化器看到的噪声、以及梯度累加步数都变。显存若走 GPipe 会炸；1F1B 下主要剩累计梯度和 optimizer。还要保证 $M$ 能被调度整除。
- **stage 切不均怎么办？** 最后一层加词表 softmax 往往最重，前几层 embedding 也不轻。应按 FLOPs / 激活字节切，而不是按层数均分；实在不均就让重的 stage 少挂几层。
- **Zero-bubble / DualPipe？** 用更多的 W 反传与 F 重叠，甚至拆参数梯度通信，把剩余空槽再填。面试提一句「1F1B 之后还有把 backward 再切开的工作」即可，细节没有跑过不要装。
- **和数据并行的 bubble 有何不同？** DP 的空转多半是等 all-reduce 或 dataloader；PP 的空转是流水线拓扑决定的，即使通信瞬时完成，warmup 也还在。
