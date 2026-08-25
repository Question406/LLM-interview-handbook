---
id: minimax-param-breakdown
section: arch
order: 202
level: B
title: MiniMax：大模型参数量在各部分大概怎么拆？
quick: >-
  按 Embedding、每层 Attention（QKV/O）、MLP（含 SwiGLU 三矩阵）、输出头估算；MoE
  再乘专家数并说明路由不增加同量激活参数。我会给公式，不背某一发布会数字。
tags:
  - MiniMax
  - Parameter Count
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯/百度/minimax 大模型算法面经总结帖
    url: https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279
    type: candidate-first-hand
---

## 真题记录

- 公司：MiniMax（总结帖收录）
- 原始措辞：**“大模型算法中模型参数量每个部分有多少？”**

这块容易背某一发布会的「70B / 456B」数字，或把总参数和每 token 激活参数混成一个数。我会给可复用的拆分：词表、注意力、MLP、输出头，再单独说 MoE。数字对不上公开技术报告就说「按公式估」，不要编造。

## 稠密 Transformer：四块加法

记隐藏维 $d$、层数 $L$、词表 $V$、FFN 中间维 $d_{\mathrm{ff}}$。SwiGLU 常用 $d_{\mathrm{ff}}\approx 8d/3$，使激活后宽度接近旧版 $4d$。

- **Token embedding**：$\approx V\cdot d$。词表到十万级时，这一项已经是数 B，不可忽略。若 lm_head 与 embedding **untied**，输出头再加一份同量级。
- **每层 Attention**：标准 MHA 是 $W_Q,W_K,W_V,W_O$ 四块 $d\times d$，约 $4d^2$。GQA 把 $K,V$ 头数降到 $n_{\mathrm{kv}}$，参数按 $d\cdot d_{\mathrm{kv}}$ 打折，见 `pdd-attention-handwrite`、`arch-mla`。偏置、RoPE 频率表相对很小。
- **每层 MLP**：SwiGLU 三矩阵（gate / up / down）约 $3d\cdot d_{\mathrm{ff}}$；ReLU FFN 是两矩阵 $2d\cdot d_{\mathrm{ff}}$。MLP 通常比 Attention 更大。
- **Norm / 其它**：RMSNorm 只有 $d$ 级，可忽略。

合计

$$
N \approx Vd + L\bigl(4d^2 + 3d\,d_{\mathrm{ff}}\bigr)
$$

（GQA / tied head 时改对应项）。口算：7B 级 $d=4096,L=32$，一层 MLP 就接近注意力的两倍以上。我会先报公式，再代入一档公开配置做数量级核对。

## MoE：总参数可以涨，激活参数按 top-$k$

专家复制的是 FFN，不是整层。$E$ 个专家、每 token 激活 $k$ 个（可加共享专家），则

$$
N_{\mathrm{total}}\approx Vd + L\bigl(4d^2 + E\cdot 3d\,d_{\mathrm{ff}}\bigr),\qquad
N_{\mathrm{act}}\approx Vd + L\bigl(4d^2 + k\cdot 3d\,d_{\mathrm{ff}}\bigr).
$$

路由器是 $d\times E$ 量级，相对专家矩阵可忽略。回答必须拆两句话：容量跟 $E$ 走，算力跟 $k$ 走。不要说「MoE 参数少」，总参数往往更多，省的是激活 FLOPs。负载不均时有效 $k$ 还会漂，见 `tencent-moe-vs-dense`、`arch-moe-balance`。

Embedding 在大词表、多语言模型里占比可到总参数的 10% 量级；只报「层内 $d^2$」会漏这块。若追问公司具体型号，回到公开技术报告的 $d,L,E,k$，用上面公式验算，对不上就承认未读到该版附录。

## 追问

- **为什么 SwiGLU 是三矩阵？** gate 与 up 都是 $d\to d_{\mathrm{ff}}$，down 是 $d_{\mathrm{ff}}\to d$。中间维常取 $\approx 8d/3$，使参数量接近旧 $4d$ FFN，而不是「多一块就多 50% 宽度」。
- **GQA 怎么改公式？** $W_K,W_V$ 变成 $d\times d_{\mathrm{kv}}$，$d_{\mathrm{kv}}=n_{\mathrm{kv}}d_h$。Q 与 O 仍是 $d\times d$。不要把 cache 节省和参数节省当成同一个系数。
- **tied embedding 省多少？** 省掉一份 $Vd$ 的 lm_head；大词表时很明显。训练稳定性与解耦后的头是否更好，是另一道题。
- **共享专家怎么算激活？** 每 token 固定走共享专家，再加 top-$k$ 路由专家，$N_{\mathrm{act}}$ 的 FFN 项是 $(k+n_{\mathrm{shared}})\cdot 3d d_{\mathrm{ff}}$。总参数仍按全部专家计。见 `tencent-qwen-vs-deepseek`。
- **能不能只报一个「XXB」？** 不能。总参数谈容量与存盘，激活参数谈训练/推理算力。MiniMax 这题要的是拆分，不是发布会口径。
