---
id: arch-qlora
section: arch
order: 12
level: A
title: QLoRA 的 NF4、Double Quantization、Paged Optimizer 是什么？
quick: "QLoRA 把冻结的基座权重用 4-bit NF4 存着，只训练 LoRA，省显存主要靠基座不用存 Adam 状态。NF4 按正态分布的分位数摆量化格子，Double Quantization 再把量化常数压一遍，Paged Optimizer 把优化器状态分页换出，削掉显存峰值。"
tags:
  - QLoRA
  - Quantization
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ QLoRA
    url: 'https://arxiv.org/abs/2305.14314'
    type: legacy-reference
---

QLoRA 是训练期省显存的办法：冻结的基座用 4-bit 存，只给 LoRA 建优化器状态。它的计算并不是全程 INT4 算术，前向通常会把量化权重解回更高精度再乘激活；它和 GPTQ 这类推理量化也是两回事。LoRA 的更新照旧是 $\Delta W=\frac{\alpha}{r}BA$，只是 $W$ 以 NF4 的形式驻留在显存里。

省下来的大头在优化器状态。Adam 一类优化器要给每个可训练参数存 $m,v$，全参微调时这部分是权重的好几倍。QLoRA 只给 LoRA 的 $A,B$ 建状态，基座完全没有优化器状态。剩下三个名词各管一块：NF4 管权重怎么存，Double Quantization 管量化常数，Paged Optimizer 管峰值。

## NF4：按正态分位数摆格子

预训练权重近似零均值正态，大部分值挤在中心附近。均匀 4-bit 把格子平均铺在整个范围上，和这个分布对不上。NF4（NormalFloat4）按标准正态定义 $2^4-1$ 个分位，让离散格子贴着分布摆，再对每个 block 做缩放。面试说一句就够：同样是 4 bit，NF4 的格子是按数据分布切的。

这和 MoE、SwiGLU、RoPE 互不相干。量化的是线性权重的存储，门控 $\mathrm{SiLU}(xW_1)\odot xW_2$ 和旋转 $R_{\theta,m}$ 照样在解量化之后的计算里发生。

## Double Quantization 和 Paged Optimizer

每个 block 的 scale（可能还有零点）本身也要用 FP32 / FP16 存。参数量一大，这些常数加起来很可观。Double Quantization 把量化常数再做一次低比特量化，省的是这部分「元数据」，权重精度并没有再砍一遍。

即便基座没有优化器状态，长序列的激活加上 LoRA 的优化器状态，仍然可能把显存顶满。Paged Optimizer 用统一内存把优化器的页在 CPU 和 GPU 之间换入换出，削的是峰值，算法本身不变。

## 追问

**NF4 和 INT4 哪个准？**
对近似正态的权重，NF4 通常贴得更好。最终还是看下游结果，名字说明不了什么。

**训完 QLoRA，是不是直接得到一个 4-bit 部署模型？**
不是。QLoRA 是训练期的显存技巧：冻结基座、4-bit 存权重、只训低秩适配器。GPTQ / AWQ 是推理权重量化，服务时不需要 LoRA。合并 adapter 之后要再量化，是另外一步。

**能不能训 MoE 的专家？**
可以，挂在专家的线性层上就行。不过路由 logits 的量化误差会放大负载不均，要单独盯 overflow。

**Paged Optimizer 是不是把整个模型都 offload 了？**
不是。它分页的只是优化器状态，权重仍然按 QLoRA 的路径在 GPU 上解量化计算。
