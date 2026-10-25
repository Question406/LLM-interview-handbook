---
id: nvidia-pipeline-bubble
section: nvidia
order: 4
level: S
title: NVIDIA：流水线气泡从哪来，1F1B / interleaved 怎么减
quick: "流水线启动和排空时，有些 stage 要等激活或梯度，因此会空转。$P$ 个 stage、$M$ 个 microbatch 时，$M$ 足够大才可把气泡比例近似成 $(P-1)/M$；1F1B 主要降低在途激活内存，interleaved 则用每卡 $v$ 个虚 stage 把气泡近似再除以 $v$。"
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

流水线气泡就是某个 stage 没有可算的工作，只能等上游的激活或下游的梯度。比如第一批刚进入流水线时，后面的卡还收不到激活；最后一批向后传播时，前面的卡又会先空下来。增加 microbatch 可以摊薄这段空转，1F1B 主要节省激活内存，interleaved 则进一步改变调度、减少气泡。

万亿参数训练的整体切分见 `nvidia-trillion-train`。这里用 $P$ 个 stage、$M$ 个 microbatch 和每卡 $v$ 个虚 stage，把这些调度分别算清楚。

## 气泡从哪来

$P$ 张卡纵向切层。第 $k$ 个 stage 算 forward 必须等 $k-1$ 把激活送来；backward 必须等 $k+1$ 把梯度送回来。流水线还没灌满时，后面的卡闲着（warmup）；灌完最后一批 forward 之后，前面的卡闲着（cooldown）。稳态里如果各 stage 耗时一样，可以满载；切不均、P2P 没重叠、某个 stage 塞了 embedding / lm head，稳态也会冒泡。

GPipe 式 flush：先把 $M$ 个 microbatch 的 forward 全部推完，再统一 backward。气泡时间大约 $(P-1)$ 个 forward 加上 $(P-1)$ 个 backward，占一步总时间的比例

$$
\frac{P-1}{M+P-1}\approx\frac{P-1}{M}\quad (M\gg P).
$$

$M$ 必须明显大于 $P$，否则一半时间在填管子。这就是「microbatch 太少，流水线一定慢」的来源。

激活内存是另一笔账：flush 要给在途的所有 microbatch 留正向激活，$O(M)$ 份。$M$ 为了减少气泡变大，显存先爆。所以纯 GPipe 在深流水线上很难用。

1F1B（Megatron 用的 PipeDream-flush 一类）：先 warmup $P-1$ 个 forward，进入稳态后每个 stage 一次 forward、一次 backward 交替，最后 cooldown。两端仍然有 $P-1$ 个空槽，气泡比例还是 $\approx(P-1)/M$。

1F1B 主要省激活：稳态每卡只需要保留 $O(P)$ 量级的在途 microbatch，GPipe 则要保留 $O(M)$。$M$ 可以开到几十去减少气泡，而不用把所有 forward 激活都留到最后。重计算仍然能进一步省显存，但那是正交的。

因此 1F1B 仍有气泡。Nsight Systems 上 warmup、cooldown 的空白还在，变化是稳态 GEMM 更紧凑、激活峰值更低。

## Interleaved 怎么把泡泡除以 $v$

Interleaved 1F1B：模型切成 $vP$ 段，每张卡拿 $v$ 个不连续的虚 stage。例如 $P=4$、$v=2$、8 层，卡 0 拿第 0 和第 4 层，卡 1 拿第 1 和第 5 层。同一张卡在一轮里会多次变成「流水线的上游 / 下游」，warmup 需要的空槽大约从 $P-1$ 降到 $(P-1)/v$。气泡比例近似

$$
\frac{P-1}{vM}.
$$

$v=2$ 是 Megatron 万亿博客里的常用值：泡泡减半，实现复杂度可接受。

虚 stage 增多也会增加边界和 P2P 次数，microbatch 数还要满足更细的调度整除约束。切得太碎会产生许多小 kernel，像 TP 过大一样降低 MFU，所以 $v$ 需要实测选择。

和张量并行的配合：节点内 TP、节点间 PP。PP 的 P2P 是点对点传激活 $[B_{\mathrm{micro}}, T, D]$，体积通常小于 TP 的 all-reduce，但延迟不能藏在 NVLink 里。气泡诊断优先看「是不是 $M$ 不够、stage 算力不均」，再看 NCCL。层内集合通信见 `nvidia-tensor-parallel`，两者不要混成一次 all-reduce。

## 追问

**把 $M$ 开到极大？**
气泡比例会下降，但还要核对全局 batch、microbatch 大小和梯度累加步数怎么配，它们会影响优化器看到的噪声。GPipe 要保留更多激活，可能先超出显存；1F1B 下仍需计入累计梯度和 optimizer 状态，并保证 $M$ 满足调度的整除要求。
**stage 切不均怎么办？**
最后一层加词表 softmax 往往最重，前几层 embedding 也不轻。可以按 FLOPs 和激活字节分配 stage，单按层数均分容易失衡；实在不均就让重的 stage 少挂几层。
**Zero-bubble / DualPipe？**
这类方法会进一步拆开 backward，例如把权重梯度计算 W 与 forward F 重叠，或拆分参数梯度通信，尝试填补剩余空槽。可以说明这个方向，未实际运行过的细节就明确说明。
**和数据并行的 bubble 有何不同？**
DP 的空转多半是等 all-reduce 或 dataloader；PP 的空转是流水线拓扑决定的，即使通信瞬时完成，warmup 也还在。
