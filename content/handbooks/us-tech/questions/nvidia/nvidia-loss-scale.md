---
id: nvidia-loss-scale
section: nvidia
order: 12
level: A
title: NVIDIA：混合精度 loss scaling，overflow 怎么发现和恢复
quick: >-
  FP16 指数范围窄，梯度容易下溢成 0。把 loss 乘 $S$，反向梯度都乘 $S$，进优化器前再除掉。$S$ 太大就溢出成
  inf。动态缩放：检测到 inf/nan 就跳过这一 step 并把 $S$ 减半；连续若干步干净再把 $S$ 加倍。BF16
  通常不需要；FP8 的 tensor scale 是另一件事。
tags:
  - NVIDIA
  - Mixed Precision
  - Loss Scaling
  - AMP
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Mixed Precision Training
    url: https://arxiv.org/abs/1710.03740
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: NVIDIA Megatron-LM
    url: https://github.com/NVIDIA/Megatron-LM
    type: primary
---

## 题怎么来的

NVIDIA 把混合精度写成了 AMP / Apex / Megatron 的默认路径。我会先问 dtype：fp16 才需要全局 loss scale，bf16 通常不用，FP8 走的是另一套 tensor amax。这不是量化题。INT8 / SmoothQuant 见 `nvidia-int8-quant`；FP8 每张量 amax 见 `nvidia-fp8`。本题只处理全局 loss scaling：发现溢出、丢掉这一拍、改 $S$、权重保持上一拍的干净值。

## 为什么要乘 $S$

FP16 最大有限值大约 $65504$，最小正规数大约 $6\times 10^{-5}$ 量级。反向里很多梯度比这个还小，flush 成 0，训练看起来 loss 在动、参数几乎不更新。做法：

$$
L' = S\cdot L,\qquad \nabla_{\mathrm{fp16}} = S\cdot \nabla,\qquad \nabla_{\mathrm{fp32}} = \nabla_{\mathrm{fp16}}/S.
$$

Master 权重和 Adam 状态留 fp32，$S$ 在更新前剥掉。这是 2017 混合精度论文的核心，不是「把模型改成 fp16 就完了」。$S$ 常用 $2^{10}$ 到 $2^{16}$ 起步。太大：乘法之后的激活 / 梯度超过 65504，变成 inf。太小：下溢还在。

BF16 指数和 fp32 同宽，动态范围够，一般不用 loss scale。今天 LLM 训练默认 bf16，这题仍会问，因为 Megatron 还能走 fp16，而且它和 FP8 的溢出故事容易被混在一起。

## 溢出怎么发现

不能等 loss 变成 nan 再猜。AMP 的路径是：`unscale_` 之后在 fp32 梯度上做 inf/nan 检查（CUDA 上有融合 kernel，不必把整份梯度 DtoH）。Megatron / GradScaler 维护一个 `found_inf` 标志。只要任何一个参数的梯度里有 inf 或 nan，这一 step 视为溢出。

检查点要在 clip / optimizer 之前。已经用 inf 去 Adam 了，动量也被污染，恢复会很难看。正确顺序：

1. `scaler.scale(loss).backward()`
2. 可选：unscale，再 clip（clip 的是未放大的 fp32 梯度）
3. `scaler.step(optimizer)`：内部若 found_inf，不调用 `optimizer.step()`
4. `scaler.update()`：按是否溢出改 $S$

```python
scaler = GradScaler(init_scale=2**16, growth_interval=2000)
opt.zero_grad(set_to_none=True)
with autocast(dtype=torch.float16):
    loss = model(x, y)
scaler.scale(loss).backward()
scaler.unscale_(opt)
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
scaler.step(opt)
scaler.update()
```

Nsight 里你看不到 overflow 这个计数器，除非自己 log。训练曲线上：偶发 step 被 skip，global step 仍加 1 但权重没动，loss 下一步通常回来。连续 skip 说明 $S$ 还是太大，或者真的数值炸了（LR、数据、除零），不能只靠再减 $S$。

## 动态恢复

溢出：丢弃本步梯度（权重、动量保持上一份干净值），$S \leftarrow S/2$。连续 `growth_interval` 步没有 inf：$S \leftarrow 2S$，上限封顶。这是在搜「刚好不炸」的最大 $S$，让更多小梯度活在 fp16 里。

跳过的 step 不要用脏梯度做一次「很小的更新」，那会把 inf 写进 Adam。也不要 rewind 一长段 checkpoint，除非 inf 来自数据损坏而不是 scale。分布式下 inf 标志要 all-reduce：一张卡炸了、别的卡仍 step，权重立刻分叉。通信原语见 `nvidia-nccl-allreduce`。

和 FP8 delayed scaling 对比：loss scale 是一条全局乘数，保护 fp16 下溢；FP8 的 $s$ 是每 GEMM 一张量，保护 E4M3 格子。Hopper 上 bf16 + FP8 很常见，此时 GradScaler 可能根本不在，溢出走 Transformer Engine 的 amax / inf 计数。

## 追问

- **为什么 skip 而不是把梯度 clip 掉 inf？** inf 没有可用方向。Clip 普通大梯度可以；clip inf 还是 nan。只能丢步。
- **growth_interval 太短？** $S$ 会锯齿：刚加倍就炸、再减半，有效更新变少。太长则长期用过小的 $S$，小梯度仍死。
- **和梯度累加？** 累加要在 unscale 之后用 fp32 加。先在 fp16 里加再检查 inf，容易中途就溢出。Scale 在整段累加里应保持同一 $S$。
- **ZeRO / TP 下谁检查 inf？** 每张卡查自己分到的那片梯度，再集合一次布尔。漏掉 all-reduce 会静默 diverge，比丢一步更糟。
