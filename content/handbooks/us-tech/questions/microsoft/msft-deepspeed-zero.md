---
id: msft-deepspeed-zero
section: microsoft
order: 1
level: S
title: Microsoft：DeepSpeed ZeRO 1/2/3 切的是什么状态，通信体积怎么变
quick: >-
  ZeRO 切的是数据并行里的冗余状态，不是张量并行那种切 GEMM。1 切优化器，2 再切梯度，3 再切参数。1/2
  通信体积仍是基线 DP 的 $2\Psi$，3 变成 $3\Psi$（约 $1.5\times$）。显存按阶段掉，别把 ZeRO-3 说成免费午餐。
tags:
  - Microsoft
  - DeepSpeed
  - ZeRO
  - Distributed Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: DeepSpeed — Extreme-scale model training for everyone
    url: https://www.microsoft.com/en-us/research/blog/deepspeed-extreme-scale-model-training-for-everyone/
    type: primary
---

DeepSpeed / 训练系统岗几乎都会问 ZeRO。评委要的不是「开 `zero_stage=3`」，是你能不能按字节把状态切开，再说通信体积相对普通数据并行怎么变。公开出处是 Rajbhandari 等人的 ZeRO 论文和 MSR 的 DeepSpeed 博客。万亿卡上的 3D 并行叠法见 `nvidia-trillion-train`，本题只收分片数据并行这一轴。

## 先算 16 字节，再谈切分

混合精度 Adam 里，每个参数大约：

- fp16 参数 $2$ 字节，fp16 梯度 $2$ 字节；
- fp32 主权重 + 一阶矩 + 二阶矩，约 $12$ 字节。

合计 $16\Psi$（$\Psi$ 是参数个数）。$70\mathrm{B}$ 模型光状态就是约 $1.12\mathrm{TB}$，还没算激活。普通 DDP 每张卡都存一份完整副本，所以单靠「多加几张卡做数据并行」塞不进。

ZeRO 的洞察：这些副本在数据并行组里是冗余的。不必每张卡随时握着全量状态，用的时候再集合通信拼回来。三阶段是累加的：

| 阶段 | 切什么 | 每卡状态（量级） | 每步通信体积 |
| --- | --- | --- | --- |
| 基线 DP | 不切 | $16\Psi$ | $2\Psi$（all-reduce） |
| ZeRO-1 | 优化器状态 | $4\Psi + 12\Psi/N_d$ | $2\Psi$ |
| ZeRO-2 | + 梯度 | $2\Psi + 14\Psi/N_d$ | $2\Psi$ |
| ZeRO-3 | + 参数 | $16\Psi/N_d$ | $3\Psi$（约 $1.5\times$） |

$N_d$ 是数据并行度。论文原话：1 大约 $4\times$ 显存、2 大约 $8\times$、3 随 $N_d$ 线性降。$N_d=64$ 的 ZeRO-3 才是「状态缩小 64 倍」那种宣传数字，别拿 8 卡实验外推成万亿。

## 通信：1/2 不涨，3 多半份参数

基线 DP 对梯度做 all-reduce，体积 $2\Psi$（reduce-scatter 一份 $\Psi$ 再 all-gather 一份 $\Psi$）。

ZeRO-1/2 把 all-reduce 拆成「梯度 reduce-scatter + 更新后再 all-gather 参数」。体积仍是 $2\Psi$，所以面试可以说：**前两档用通信调度换显存，体积不涨**。涨的是实现复杂度和小包延迟，不是渐进通信量。

ZeRO-3 参数也分片。前向每层 all-gather 当前层参数，算完丢掉；反向再 gather 一次，梯度 reduce-scatter。多出来的是反向那次参数 gather，总共 $3\Psi$，相对基线 $1.5\times$。这是论文给的上界，不是「通信爆炸」。

实践里 3 的痛点往往是 **延迟和气泡**，不是那多出来的 $\Psi$：层太小、prefetch 没叠上计算、CPU 侧 hook 太碎，Nsight 上全是在等集合通信。DeepSpeed 用下一层 prefetch 和 bucket 去藏；讲不出 overlap，评委会觉得你只背了表。

## 白板怎么选档，别和 TP 搅在一起

我会按显存缺口选，不按「越高越强」：

- 优化器先爆、模型还能单卡放下：ZeRO-1 就够，实现也最接近 DDP。
- 梯度也放不下：上 2。通信体积不变，显存再砍一截。
- 单层参数都放不进：才上 3。准备好 $1.5\times$ 体积和更碎的 all-gather。

ZeRO-3 **不能替代张量并行**。它解决的是「状态副本」，层内大 GEMM 仍然要一块完整矩阵。万亿 dense 常见是 TP（NVLink 域）$\times$ PP $\times$ ZeRO/DP。把「FSDP / ZeRO-3 等于模型并行」说出去，后面追问单层算力会露馅。

激活仍跟 $B\cdot T\cdot L\cdot d$ 走，ZeRO 不管这条。长上下文还是要重计算、序列并行。Offload（ZeRO-Offload / Infinity）是把状态扫到 CPU/NVMe，带宽墙换显存，和 1/2/3 的切分轴不是一回事，追问时要拆开。

## 追问

- **ZeRO-2 的梯度为什么可以切？** 更新时每张卡只需要自己那一分区的梯度。reduce-scatter 之后本来就只留分片，不必再握全量 fp16 梯度。
- **为什么 3 的通信不是 $4\Psi$？** 前向 gather 一次、反向 gather 一次、梯度 scatter 一次，三次各 $\Psi$。没有「再广播一份完整模型」。
- **和 PyTorch FSDP？** 思想对齐 ZeRO-3：参数分片、用时 all-gather。面试用 ZeRO 论文的 $2\Psi$/$3\Psi$ 讲清楚即可，不要死磕 API 名。
- **小模型也开 3？** 往往更慢。状态本来就不大，多出来的逐层 gather 延迟赚不回来。先看 profiler，再升档。
