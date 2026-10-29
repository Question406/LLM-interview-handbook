---
id: sys-quant
section: systems
order: 12
level: A
title: GPTQ、AWQ、SmoothQuant、QAT 大概怎么区分？
quick: >-
  GPTQ 用二阶近似降低训练后权重量化的误差，AWQ 用 activation 统计保护或缩放重要权重通道；SmoothQuant 把 activation
  outlier 的难度迁到 weights，常用于 W8A8。QAT 则在训练中模拟量化误差，让权重适应。是否加速还取决于 kernel 和反量化开销。
tags:
  - Quantization
  - Inference
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: GPTQ
    url: 'https://arxiv.org/abs/2210.17323'
    type: primary
  - title: AWQ
    url: 'https://arxiv.org/abs/2306.00978'
    type: primary
  - title: SmoothQuant
    url: 'https://arxiv.org/abs/2211.10438'
    type: primary
---

GPTQ、AWQ、SmoothQuant 都是在训练后做量化，也就是 PTQ；QAT 则在训练中模拟量化误差，让权重提前适应。前三种的区别主要在于量化权重还是连激活一起量化，以及怎么处理误差。比如 GPTQ / AWQ 常把权重降到 INT4、激活仍用 16 位，先节省读取权重的带宽；实际是否加速，还要看 kernel、反量化（dequant）开销和模型是否受显存带宽限制。硬件处理不好相应形状时，INT4 也可能更慢。

## 各种方法怎样控制误差

| 方法 | 典型类别 | 核心 |
| --- | --- | --- |
| GPTQ | PTQ weight-only | 近似 Hessian，逐层重构，最小化量化误差 |
| AWQ | PTQ weight-only | 用 activation 统计找重要通道并缩放保护 |
| SmoothQuant | PTQ W8A8 | 把 activation outlier 平滑迁到 weight scale |
| QAT | 训练中量化 | forward 模拟 quant，让权适应误差 |

GPTQ / AWQ 常用于 INT4 权、激活仍 16 位，省的是权带宽。SmoothQuant 针对 W8A8：激活 outlier 让 INT8 难以表示，把难度乘到权上，两边都变得可量化。QAT 贵，但要上低 bit 或敏感模型时，PTQ 不够再上。

## 何时更快、何时只是更小

权重量化在 逐 token 生成（decode）（memory-bound、反复读权）上收益大；输入 prefill 大 GEMM 已 compute-bound，降 bit 不一定涨速。没有对应 Tensor Core / INT kernel，就要 dequant 回 BF16 再算，等于多一次读写。batch / 头数不友好时同样。我会说「先看是不是读权瓶颈，再看有没有 kernel」。模型本来就小、batch 已经很大时，量化常常只缩小磁盘，不缩短 TPOT。

KV 量化是另一条线（存 cache 不是存权），不要和 GPTQ 混，见 `sys-precision`、`sys-pagedattention`。

## 与 training precision 的区别

训练用 BF16/FP8 是为了稳定收敛；推理量化是在已收敛权上压部署成本。QAT 是中间地带：训练时看见量化噪声。RL sampling 轨迹（rollout） 若对 sampling 用 FP8 / INT4，训练图仍 BF16，必须重算 logp，见 `slime-sglang-native`。

## 追问

**AWQ 和 GPTQ 谁更准？**
取决于模型和 calibration 数据。AWQ 强调保护激活敏感通道；GPTQ 强调逐层二阶重构。不要背「谁绝对更好」。
**SmoothQuant 为什么能做 W8A8？**
激活 outlier 被 scale 挪到权上，两边动态范围都收敛到 INT8 可表示区间。
**QAT 一定优于 PTQ？**
不一定。数据少、训练不稳时 QAT 更差；先 PTQ，精度不够再 QAT。
**量化后 perplexity 差不多就一定能上线吗？**
不够。还要看长尾任务、安全拒绝和 decode throughput。PPL 对部署误差不敏感。
**W4A16 和 W8A8 怎么选？**
只缺权带宽、激活还好：W4A16（GPTQ/AWQ）。激活也有 outlier、硬件吃 INT8 GEMM：W8A8 + SmoothQuant。先看瓶颈再选配方。
