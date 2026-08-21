---
id: ali-arch-hotspots
section: alibaba
order: 33
level: S
title: 通义/云智能方向：架构与系统高频题该怎么刷？
quick: >-
  白板优先：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 α、ZeRO
  显存手算、TP 切分。每题练到能画图讲 trade-off。
tags:
  - Alibaba
  - Architecture
  - Systems
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 阿里系 2025-26 算法高频整理
    url: 'https://www.nowcoder.com/discuss/848942791164981248'
    type: legacy-reference
---

陷阱是把通义/云智能方向当成「背 Qwen 特性清单」。阿里系公开面经的高频簇是能画图、能手算、能讲 trade-off 的白板题：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 $\alpha$、ZeRO 显存、TP 切分。只会说「我们用了 GQA」而算不出 KV 体积，面试官下一问就停。Attention 公式底盘见 `ali-attention-math`。

## 结构：能推公式，能说为什么这样改

RoPE：把相对位置写进旋转，外推不是无限免费，位置外推、NTK、YaRN 各修什么要能对比。RMSNorm 去掉均值、只除 RMS，和 Pre-Norm 叠在一起是稳定训练的标配；别把 RMSNorm 说成「没有参数的 LayerNorm」。SwiGLU 的中间维通常是 $\frac{8}{3}d$ 再取整，参数量要比「两层 FFN」多一块门控。GQA：KV 头数 $n_{\mathrm{kv}}\lt n_q$，解码时 KV cache 从 $O(n_q\cdot T\cdot d_h)$ 降到 $O(n_{\mathrm{kv}}\cdot T\cdot d_h)$，换的是带宽不是 FLOPs。这些题在 Architecture 章有深卡，本卡当阿里定向清单。

## 适配与并行：LoRA、ZeRO、TP 要手算

LoRA：$\Delta W=BA$，常用 $B$ 零初始化、$A$ 高斯，保证起步等价于原模型；有效步长和 $\alpha/r$ 绑定，只改 $r$ 不改 $\alpha$ 会把更新尺度改掉。Qwen 微调阶段与 Loss 选择见 `ali-qwen-finetune-loss`。ZeRO-1/2/3 分别切优化器态、梯度、参数；显存构成是参数 + 梯度 + Adam 动量 + 激活，面试要能按层宽、层数、精度估数量级。张量并行按列/行切线性层，要注意序列并行和通信；别把 TP 和 PP、DP 混成「都是并行」。

## 推理：PagedAttention、量化、投机解码

服务侧高频：PagedAttention 把 KV 分页避免预留浪费；权重量化降带宽；投机解码用小模型起草、大模型验证。这些和 Agent 延迟题是一条线（`ali-latency-3tools`）：架构选择最终要落到 p95 和成本。刷法是每题一张图：数据怎么切、通信何时发生、哪一项显存最大。Pre-Norm 相对 Post-Norm 更好训深，但不要把「Qwen 用 RMSNorm」当成答案——要能写 RMS 公式并对比 LayerNorm 少了减均值。通义方向还可能问 MoE 路由与容量；答不出 trade-off 就不要主动展开。每题练到能在白板上指出：改这一项，显存、带宽、质量各往哪边走。

## 追问

- **GQA 一定比 MHA 准吗？** 不一定。省的是 KV 带宽，质量取决于 $n_{\mathrm{kv}}$ 和任务。白板先写 cache 公式再谈质量。
- **LoRA 的 $\alpha$ 是什么？** 缩放系数，更新等效于 $(\alpha/r)BA$。只调 $r$ 不调 $\alpha$，有效学习率会变。
- **ZeRO-3 为什么更慢？** 参数被切碎，前向要 all-gather。显存换通信，小集群未必划算。
