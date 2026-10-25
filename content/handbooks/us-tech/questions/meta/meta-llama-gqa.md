---
id: meta-llama-gqa
section: meta
order: 1
level: A
title: Meta / Llama：为什么 70B 用 GQA？和 MHA 比 decode 省在哪？
quick: "按这张卡采用的 Llama 2 70B 公开配置，$32$ 个 query head 共享 $8$ 个 KV head，KV 存储与读取量约为 MHA 的 $1/4$。GQA 在质量与带宽间折中，cache 只存紧凑 KV，计算时逻辑展开或用融合 kernel；总加速还取决于其他开销。"
tags:
  - Meta
  - Llama
  - GQA
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

GQA 让多个 query head 共享一组 K/V，主要减少 decode 时保存和读取历史 KV 的开销，同时比 MQA 保留更多 KV 组来折中质量。这张卡按 Llama 2 论文配置讨论，通用公式与选型见 `arch-gqa`、`google-gqa-mqa`。

按这里的 70B 配置，隐藏维 $8192$、$32$ query heads，$d_{\mathrm{head}}=256$，K/V 收到 $8$ 组，每组 $4$ 个 query head 共用。KV cache 字节为：

$$
2 \cdot L \cdot T \cdot H_{\mathrm{kv}} \cdot d_{\mathrm{head}} \cdot \mathrm{bytes}
$$

$H_{\mathrm{kv}}$ 从 $32$ 到 $8$，KV cache 与相关读取带宽约为 $\times 1/4$。Decode 每步的大 GEMM 较少，读取历史 KV 很重要，所以这是影响耗时的资源减少；$1/4$ 指这部分开销，还要连同其他开销判断实际延迟。MQA 用 $H_{\mathrm{kv}}=1$ 还能少 $8$ 倍，质量敏感的对话模型则可停在 GQA；论文强调不显著损失质量地加快推理，并不表示它必然比 MHA 更准。

Llama 2 训练时就采用 GQA，K/V 投影直接产出紧凑头。实现形状可画成 $K,V$ 为 `[B, 8, S, 256]`，$Q$ 为 `[B, 32, S, 256]`，计算时 repeat 4 次或直接用 GQA kernel，cache 始终只存 $8$ 组。若把 $32$ 组展开结果写入 cache，就重复花掉了本想节省的空间与带宽。

MHA 检查点也可以转换，GQA 论文给 mean-pool 初始化，但转换有误差，要在相同评测上验证，不能保证无损。Llama 3 的 128k 把 $T$ 拉长后，这项 KV 节约更显著，再叠 KV 量化与 paging 需要另算，见 `sys-quant`。

## 追问

**为什么选 8？**
公开论文没有固定描述搜索过程，可在 $1$ 与 $H_q$ 间扫质量与带宽工作点，不能编成必须是 $4$ 的幂。

**与 MoE 冲突吗？**
机制不直接冲突，GQA 改注意力 KV，MoE 改 FFN 路由，显存要把两者一起算。

**后续 Llama 还用吗？**
按相应公开报告核对具体配置，原理仍是 decode KV 带宽随 $H_{\mathrm{kv}}$ 变化。

## 相关题

- [[google-gqa-mqa]]：MHA、MQA、GQA 三档对比。
- [[meta-gqa-kernel]]：cache 紧凑存储，kernel 按 `h_q // g` 映射。
- [[apple-ondevice-kv]]：手机端 DRAM / ANE 与 8-bit cache。
- [[us-llm-paper-stack]]：GQA、Llama 精读公式。
