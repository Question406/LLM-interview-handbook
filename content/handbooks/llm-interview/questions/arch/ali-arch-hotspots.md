---
id: ali-arch-hotspots
section: arch
order: 33
level: S
title: 通义/云智能方向：架构与系统高频题该怎么刷？
quick: >-
  按白板题刷：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 α、ZeRO
  显存手算、TP 切分。每题练到能画图、能手算，说得出改这一项后显存、带宽、质量各往哪边走。
tags:
  - Alibaba
  - Architecture
  - Systems
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 阿里系 2025-26 算法高频整理
    url: 'https://www.nowcoder.com/discuss/848942791164981248'
    type: legacy-reference
---

阿里系架构和系统题，我会当白板题来刷，背 Qwen 特性清单用处不大。公开面经的常见 topics 都是能画图、能手算、能讲 trade-off 的题：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 $\alpha$、ZeRO 显存、TP 切分。

比如只会说「我们用了 GQA」，却算不出 KV 有多大，面试官下一问就停了。所以每题我都练到能在白板上指出：改这一项，显存、带宽、质量各往哪边走。这些题在 Architecture 章都有深卡，这张卡当阿里定向清单用。

## 结构题：能推公式，能说为什么这样改

RoPE 把相对位置写进旋转，外推并不是无限免费的，位置外推、NTK、YaRN 各修什么要能对比。RMSNorm 去掉均值、只除 RMS，和 Pre-Norm 叠在一起是稳定训练的标配。要能写出 RMS 公式，指出它比 LayerNorm 少了减均值这一步，也别把它说成「没有参数的 LayerNorm」。Pre-Norm 比 Post-Norm 更好训深，但光说「Qwen 用 RMSNorm」答不了题。

SwiGLU 的中间维通常是 $\frac{8}{3}d$ 再取整，参数量比「两层 FFN」多一块 gating。GQA 让 KV 头数 $n_{\mathrm{kv}}\lt n_q$，decoding 时 KV cache 从 $O(n_q\cdot T\cdot d_h)$ 降到 $O(n_{\mathrm{kv}}\cdot T\cdot d_h)$，省下来的是带宽，FLOPs 没怎么变。Attention 公式本身见 `ali-attention-math`。

## 适配与并行：LoRA、ZeRO、TP 要手算

LoRA 写成 $\Delta W=BA$，常用 $B$ 零初始化、$A$ 高斯，保证起步时等价于原模型。有效步长和 $\alpha/r$ 绑在一起，只改 $r$ 不改 $\alpha$，更新尺度就跟着变了。Qwen 微调阶段与 Loss 选择见 `ali-qwen-finetune-loss`。

ZeRO-1/2/3 分别切优化器态、梯度、参数。显存由参数、梯度、Adam 动量和激活四块组成，我会按层宽、层数、精度估出数量级。张量并行按列或按行切线性层，还要讲序列并行和通信。TP、PP、DP 各切什么要分清，别混成一句「都是并行」。

## 推理：PagedAttention、量化、speculative decoding

服务侧的高频是 PagedAttention 把 KV 分页、避免预留浪费，权重量化降带宽，speculative decoding 用小模型起草、大模型验证。这些和 Agent 延迟题是一条线（`ali-latency-3tools`），架构选择最后都要落到 p95 和成本上。刷的时候每题画一张图：数据怎么切、通信什么时候发生、哪一项显存最大。

通义方向还可能问 MoE 路由与容量。讲不出 trade-off 的话，就别主动往这边展开。

## 追问

**GQA 一定比 MHA 准吗？**
不一定。它省的是 KV 带宽，质量取决于 $n_{\mathrm{kv}}$ 和任务。白板上先写 cache 公式，再谈质量。

**LoRA 的 $\alpha$ 是什么？**
缩放系数，更新等效于 $(\alpha/r)BA$。只调 $r$ 不调 $\alpha$，有效学习率会变。

**ZeRO-3 为什么更慢？**
参数被切碎了，前向要 all-gather。它是拿通信换显存，小集群上未必划算。
