---
id: sys-mfu
section: systems
order: 46
level: A
title: 系统：预训练一步的 MFU 怎么算，哪些时间不能算进分子？
quick: "MFU 用这一步模型的有用 FLOPs 除以实际耗时和集群理论峰值，常用近似是 6ND，前向约 2ND、反向约 4ND。D 按真实有效 token 计数，数据等待、通信、checkpoint 和评估只增加分母。MFU 低时，再用 timeline 区分等待、气泡和矩阵规模过小。"
tags:
  - Pretrain
  - MFU
  - FLOPs
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

MFU 衡量集群理论算力中有多少转化成了模型的有用计算，常用模型 FLOPs 近似 $6ND$ 除以整步耗时和集群峰值。比如 dataloader 多等了一段时间，分子没变、分母变大，MFU 就会下降。这道题按 Megatron 的口径整理，后训练采样时间见 `infra-rl-mfu-6nd`。

$N$ 是参数量，$D$ 是这一步真正计入损失（loss）的 token 数。前向一次乘加大约 $2ND$，训练还要反向，合计约 $6ND$。MFU 是这组 FLOPs 除以「一步实际耗时 × 机器理论峰值」。峰值用厂商的稠密 Tensor Core 数字，不要用自己测到的 GEMM 当峰值，否则 MFU 会被抬高。

$D$ 不含 pad，也不含只为对齐补上的 token。packing 之后要以 `cu_seqlens` 里的真实 token 计数。用 global batch 乘最大长度，MFU 会虚高。

dataloader 卡住、NCCL 在等慢卡、写 checkpoint、跑验证集，这些都在分母里。分子不加大。所以 MFU 掉了，先看 timeline：GPU kernel 之间是空的，还是 kernel 本身很慢。空的多半是数据或通信。kernel 慢再看 batch 是不是小到启动开销盖过计算。

流水线气泡也计入分母。$M$ 不够大时，计算单元会因等待而空转，MFU 也就上不去。

```python
def mfu(n_params, n_tokens, step_seconds, peak_flops):
    useful = 6 * n_params * n_tokens  # forward 2ND, backward about 4ND
    return useful / (step_seconds * peak_flops)
```

## 追问

**激活重计算之后 MFU 怎么变？**
分子仍按「没有重计算的 $6ND$」算，重算的 FLOPs 不算进有用计算。实际耗时变长，MFU 下降。这是用利用率换显存。

**MoE 呢？**
$N$ 用本步实际算到的专家，不用「所有专家参数之和」。没被路由到的专家没有那 $6ND$。
