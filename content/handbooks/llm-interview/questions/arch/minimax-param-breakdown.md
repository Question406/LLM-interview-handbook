---
id: minimax-param-breakdown
section: arch
order: 202
level: B
title: MiniMax：大模型参数量在各部分大概怎么拆？
quick: "按 Embedding、每层 Attention 的 QKV/O 矩阵、MLP 和输出头分别估，再加起来。SwiGLU 的 MLP 有三组矩阵，通常比 Attention 还大；MoE 的总参数按全部专家算，每个 token 的激活参数只算实际选中的专家。拿公式代入配置，比背发布会数字可靠。"
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

我会按四块来拆：词表 embedding、每层注意力、每层 MLP、输出头，MoE 再单独说，并且把总参数和每个 token 的激活参数分成两个数报。背某一场发布会的「70B / 456B」意义不大，数字对不上公开技术报告时，就说「按公式估」，别编。

## 稠密 Transformer：四块相加

记隐藏维 $d$、层数 $L$、词表 $V$、FFN 中间维 $d_{\mathrm{ff}}$。SwiGLU 常用 $d_{\mathrm{ff}}\approx 8d/3$，让参数量接近中间维取 $4d$ 的普通 FFN。

先算 token embedding，$\approx V\cdot d$。词表到了十万级，这一项就已经是数 B，不能忽略；lm_head 如果不和 embedding 共享权重，输出头还要再加一份同量级的参数。

每层 Attention 里，标准 MHA 有 $W_Q,W_K,W_V,W_O$ 四块 $d\times d$，大约 $4d^2$。GQA 把 $K,V$ 的头数降到 $n_{\mathrm{kv}}$，K、V 投影的参数就变成 $d\cdot d_{\mathrm{kv}}$，见 `pdd-attention-handwrite`、`arch-mla`。偏置、RoPE 频率表都很小。

每层 MLP 用 SwiGLU 的话是三块矩阵（gate / up / down），大约 $3d\cdot d_{\mathrm{ff}}$；ReLU FFN 是两块，$2d\cdot d_{\mathrm{ff}}$。MLP 通常比 Attention 大。RMSNorm 这类 Norm 只有 $d$ 级参数，可以忽略。

合起来是

$$
N \approx Vd + L\bigl(4d^2 + 3d\,d_{\mathrm{ff}}\bigr)
$$

用了 GQA 或者共享输出头权重，就调整对应的项。口算一下，7B 级 $d=4096,L=32$ 时，一层 MLP 就接近注意力的两倍以上。我会先报公式，再代入一档公开配置核对数量级。

## MoE：总参数能涨，激活参数按 top-$k$ 算

专家复制的是 FFN，整层并没有复制。设 $E$ 个专家，每个 token 激活 $k$ 个（可以再加共享专家），则

$$
N_{\mathrm{total}}\approx Vd + L\bigl(4d^2 + E\cdot 3d\,d_{\mathrm{ff}}\bigr),\qquad
N_{\mathrm{act}}\approx Vd + L\bigl(4d^2 + k\cdot 3d\,d_{\mathrm{ff}}\bigr).
$$

路由器是 $d\times E$ 量级，相对专家矩阵可以忽略。专家数 $E$ 决定能存多少总参数，每个 token 选中的专家数 $k$ 决定主要的计算量。所以别说「MoE 参数少」，它的总参数往往更多，省的是激活 FLOPs。负载不均时，实际参与计算的专家数也可能变化，见 `tencent-moe-vs-dense`、`arch-moe-balance`。

另外，大词表、多语言模型里，Embedding 可能占到总参数的 10% 量级，只报层内的 $d^2$ 会漏掉这块。如果被追问公司的具体型号，就回到公开技术报告里的 $d,L,E,k$，用上面的公式验算；对不上，就承认没读到那一版的附录。

## 追问

**为什么 SwiGLU 是三块矩阵？**
gate 和 up 都是 $d\to d_{\mathrm{ff}}$，down 是 $d_{\mathrm{ff}}\to d$。中间维常取 $\approx 8d/3$，让参数量接近旧的 $4d$ FFN，所以多一块矩阵并不等于多 50% 宽度。

**GQA 怎么改公式？**
$W_K,W_V$ 变成 $d\times d_{\mathrm{kv}}$，$d_{\mathrm{kv}}=n_{\mathrm{kv}}d_h$，Q 和 O 仍是 $d\times d$。cache 省了多少和参数省了多少，别当成同一个系数。

**tied embedding 能省多少？**
省掉一份 $Vd$ 的 lm_head，大词表时很明显。至于训练稳定性、解耦的头是不是更好，是另一道题。

**共享专家怎么算激活参数？**
每个 token 固定走共享专家，再加 top-$k$ 个路由专家，$N_{\mathrm{act}}$ 的 FFN 项是 $(k+n_{\mathrm{shared}})\cdot 3d d_{\mathrm{ff}}$。总参数仍按全部专家算，见 `tencent-qwen-vs-deepseek`。

**只报一个「XXB」行不行？**
不行。总参数讲的是容量和存盘，激活参数讲的是训练和推理的算力。MiniMax 这题要的是拆分，发布会口径回答不了它。
