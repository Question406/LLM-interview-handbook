---
id: msft-deepspeed-zero
section: microsoft
order: 1
level: S
title: Microsoft：DeepSpeed ZeRO 1/2/3 切的是什么状态，通信体积怎么变
quick: >-
  ZeRO 在数据并行组内分片冗余状态：1 切优化器，2 再切梯度，3 再切参数。论文定义下 1/2 每步通信仍为 $2\Psi$，3 为
  $3\Psi$，约多 $1.5\times$。按显存缺口选阶段，再检查逐层 gather 延迟，激活和大 GEMM 仍需其他并行策略。
tags:
  - Microsoft
  - DeepSpeed
  - ZeRO
  - Distributed Training
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: 'https://arxiv.org/abs/1910.02054'
    type: primary
  - title: DeepSpeed — Extreme-scale model training for everyone
    url: >-
      https://www.microsoft.com/en-us/research/blog/deepspeed-extreme-scale-model-training-for-everyone/
    type: primary
---

## 可以这样回答

ZeRO 按阶段切分数据并行中的冗余状态，用通信换取显存：ZeRO-1 分优化器，2 再分梯度，3 再分参数。例如 $70\mathrm{B}$ 模型的混合精度 Adam 状态约 $1.12\mathrm{TB}$，普通 DDP 每卡都保留完整副本，多加数据并行卡也不会降低这份单卡占用。

公开依据是 Rajbhandari 等的 ZeRO 论文与 MSR DeepSpeed 博客。这里讨论分片数据并行，3D 并行组合另见 `nvidia-trillion-train`，选型不能只看 `zero_stage=3`。

## 技术备查

ZeRO 按阶段切分数据并行中的冗余状态，用通信换取显存：ZeRO-1 分优化器，2 再分梯度，3 再分参数。例如 $70\mathrm{B}$ 模型的混合精度 Adam 状态约 $1.12\mathrm{TB}$，普通 DDP 每卡都保留完整副本，多加数据并行卡也不会降低这份单卡占用。

公开依据是 Rajbhandari 等的 ZeRO 论文与 MSR DeepSpeed 博客。这里讨论分片数据并行，3D 并行组合另见 `nvidia-trillion-train`，选型不能只看 `zero_stage=3`。

## 先按字节算状态

每个参数约占 fp16 参数 $2$ 字节、fp16 梯度 $2$ 字节，fp32 主权重、一阶矩和二阶矩合计约 $12$ 字节，总共 $16\Psi$，$\Psi$ 为参数数目，还不包括激活。把这些状态在 $N_d$ 个数据并行 rank 中分片，才会减少每卡冗余：

| 阶段 | 切什么 | 每卡状态（量级） | 每步通信体积 |
| --- | --- | --- | --- |
| 基线 DP | 不切 | $16\Psi$ | $2\Psi$（all-reduce） |
| ZeRO-1 | 优化器状态 | $4\Psi + 12\Psi/N_d$ | $2\Psi$ |
| ZeRO-2 | + 梯度 | $2\Psi + 14\Psi/N_d$ | $2\Psi$ |
| ZeRO-3 | + 参数 | $16\Psi/N_d$ | $3\Psi$（约 $1.5\times$） |

论文给出阶段 1 约 $4\times$、阶段 2 约 $8\times$ 的节省，阶段 3 随 $N_d$ 线性降低；$N_d=64$ 才对应状态缩小 64 倍，不能从 8 卡结果直接外推。

基线梯度 all-reduce 包含 reduce-scatter 一份 $\Psi$ 和 all-gather 一份 $\Psi$，总 $2\Psi$。ZeRO-1/2 改为梯度 reduce-scatter、分片更新后 all-gather 参数，量级仍是 $2\Psi$，增加的是调度复杂度和小包延迟。

ZeRO-3 每层前向 gather 参数，算完释放，反向再 gather，梯度再 reduce-scatter，总 $3\Psi$，相对基线 $1.5\times$，属于论文定义的通信上界。实际瓶颈往往是逐层延迟和气泡：小层、prefetch 没与计算重叠、CPU hook 太碎，会在 Nsight 里看到等待集合通信。DeepSpeed 用下一层 prefetch 与 bucket 隐藏这部分时间。

## 按缺口选阶段，并留意未解决的内存

模型能单卡容纳、只有优化器状态太大时可先用 ZeRO-1；梯度也超预算时用 2；参数也需分片才考虑 3，并检查额外通信和逐层 gather。小模型状态本来不大，3 可能反而变慢，要依据 profiler。

参数分片并未切开层内大 GEMM，计算时仍需相应矩阵，所以 ZeRO-3 不能替代张量并行。万亿 dense 常组合 TP（NVLink 域）$\times$ PP $\times$ ZeRO/DP，单层计算和容量还需各自处理。

激活随 $B\cdot T\cdot L\cdot d$ 增长，长上下文仍要重计算或序列并行。ZeRO-Offload / Infinity 把状态移至 CPU/NVMe，以带宽换显存，属于另一条选择轴。

## 追问

**ZeRO-2 为什么能只留梯度分片？**
每个 rank 只更新对应状态，reduce-scatter 后留自己的梯度即可，不必再保留全量 fp16 梯度。

**阶段 3 为什么不是 $4\Psi$？**
前向 gather、反向 gather、梯度 scatter 各 $\Psi$，没有额外再广播完整模型。

**与 PyTorch FSDP 什么关系？**
都可参数分片、按需 all-gather，思想与 ZeRO-3 一致；具体实现与 API 再分别核对。
