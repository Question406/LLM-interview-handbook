---
id: tencent-zero-123
section: systems
order: 210
level: A
title: 腾讯混元：ZeRO-1 / 2 / 3 各分什么，什么时候升到 3？
quick: "ZeRO-1 分优化器，2 再分梯度，3 再分参数。先看哪一项放不下：能用 1/2 满足显存就少付按层 all-gather 的成本；长序列若卡在激活，要用 checkpoint 或序列并行处理。"
tags:
  - Tencent
  - Hunyuan
  - ZeRO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯-混元大模型面经-华5硕
    url: https://www.nowcoder.com/feed/main/detail/692fed73109e4d31915e46d34d27c762
    type: candidate-first-hand
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

ZeRO-1 分片优化器状态，ZeRO-2 加上梯度，ZeRO-3 再加上参数。选哪档要看哪一部分占满显存：Adam 放不下先考虑 1，梯度峰值太高看 2，权重仍放不下再考虑 3。比如 7B 全参在 8×80GB 上经常 ZeRO-1 就够，提前上 3 可能只是增加通信。

| Stage | 参数 | 梯度 | 优化器 |
| --- | --- | --- | --- |
| DP | 复制 | 复制 | 复制 |
| ZeRO-1 | 复制 | 复制 | 分片 |
| ZeRO-2 | 复制 | 分片 | 分片 |
| ZeRO-3 | 分片 | 分片 | 分片 |

Adam 的 FP32 $m/v$ 加 master 约 $12$ bytes/param，常是大头，所以只分优化器就能明显省显存，参数仍复制，前向通信较少。ZeRO-2 在反向 reduce-scatter，减少梯度副本和反向峰值。ZeRO-3 则前向按层 all-gather 参数，用完释放，反向再 gather 并 reduce-scatter 梯度；单卡参数稳态约 $/D$，每层却会有通信等待。

稳态和峰值要分别看。`nvidia-smi` 高于 $16N/D$ 并不奇怪，all-gather、activation 和临时 buffer 都会增加峰值。Activation 随 $B\cdot T$ 增长，ZeRO 不负责切它；8k 监督微调（SFT）如果卡在激活，要用 checkpoint、SP、减 micro-batch 或减 $T$。FlashAttention、checkpoint、序列并行和 LoRA 都是分片表以外的手段。

72B 的 BF16 权重约 $144\,\mathrm{GB}$，全参 Adam 状态还要再增加好几倍。单卡无法复制权重时，需要 ZeRO-3，或者先用 TP/PP 切开 $N$。TP 切计算图、矩阵和激活，ZeRO 切 DP 维状态，两者可以叠加。混元稠密模型常用 TP + ZeRO-1/2，只有切分后单卡仍放不下，才继续评估 3。

13B 到 32B 要结合序列与 batch，ZeRO-2 往往是较合适的折中；72B 全参通常要 3 或把 $N$ 切开。LoRA 时优化器只挂 adapter，底座冻结、甚至可以 offload，所需档位往往更低，能用 ZeRO-2 + 适度 TP 放下就无需升级。先问全参还是 LoRA、有没有 TP，再给判断。

## 追问

**ZeRO-3 为什么可能更慢？**
每层 all-gather 的成本可能无法被计算隐藏，小模型、小 batch 尤其明显。稳态显存下降，step time 仍可能增长。

**FSDP 对应哪一档？**
`fully_shard` 接近 ZeRO-3，`shard_grad_op` 接近 ZeRO-2，分片的对象同类，具体实现有差异。

**怎么衔接 72B 显存估算？**
先画分片表，声明 $N$、$D$ 和是否 LoRA，再算每项。把激活与 all-gather 峰值加上后，才得到显存估算。

相关：`sys-memory`、`tencent-zero3-qwen72b-mem`、`tencent-beyond-deepspeed`


## 真题记录

- 公司：腾讯 · 混元
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“ZeRO-1、2、3 有什么区别？”**
