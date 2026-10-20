---
id: meta-yarn-ntk
section: meta
order: 16
level: A
title: Meta：NTK / YaRN 长上下文外推，和改 rope_theta 差在哪
quick: >-
  PI 把位置除以 $s$，高频局部分辨率一起被压。NTK-aware 改 RoPE 底 $b$，低频多插、高频少动。YaRN 再按波长分段，并给注意力温度。Llama
  3.1 公开故事是训练时提高 `rope_theta` 并继续训长窗，不是把 YaRN 当官方配方。
tags:
  - Meta
  - Llama
  - RoPE
  - YaRN
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: YaRN — Efficient Context Window Extension of Large Language Models
    url: https://arxiv.org/abs/2309.00071
    type: primary
  - title: Extending Context Window of Large Language Models via Positional Interpolation
    url: https://arxiv.org/abs/2306.15595
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Introducing Llama 3.1
    url: https://ai.meta.com/blog/meta-llama-3-1/
    type: primary
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
---

`meta-llama-rope` 停在概念层。Llama / 长上下文岗追问时，要把 PI、NTK-aware、YaRN、改 `rope_theta` 四条拆开。前三条主要是已训好的 RoPE 模型怎么外推；后一条是训练超参。别说成「Llama 3 用了 YaRN」。

## 外推在拧哪根旋钮

RoPE 第 $d$ 对频率 $\theta_d = b^{-2d/|D|}$，波长 $\lambda_d = 2\pi/\theta_d$。训练长度 $L$，目标 $L'$，比例 $s=L'/L$。统一写法：$f'(x_m,m,\theta)=f(x_m,g(m),h(\theta))$。

- **位置插值 PI：** $g(m)=m/s$，$h(\theta)=\theta$。所有维同等拉伸。实现最便宜，近距被拉远，短任务容易掉。
- **NTK-aware：** $g(m)=m$，改底 $b' = b\cdot s^{|D|/(|D|-2)}$，于是 $h$ 变成新频率。设计目标是：最低频接近按 $s$ 插值，最高频几乎不动。无微调时往往比 PI 更能撑过原窗。代价：部分维会略微外推到训练没见过的相位，YaRN 论文写明 **NTK 微调效果常不如 PI**；实践里 $s$ 还得设得比名义倍数更大。
- **YaRN：** NTK-by-parts + 注意力温度。用 $r(d)=L/\lambda_d$（原窗里转了几圈）。$r$ 很小（低频、波长 $\ge L$）就按 $s$ 插值，避免外推；$r$ 很大（高频）完全不插，保住相邻 token 的位置分辨率；中间线性 ramp。Llama 族论文里常用 $\alpha=1,\beta=32$。温度：$1/\sqrt{t}=0.1\ln(s)+1$，等价于把 $q,k$ 再乘这个因子，softmax 不那么糊。兼容 FlashAttention，因为没改注意力核，只改了 RoPE 表。

Code Llama 公开把 RoPE base 提到 $10^6$ 量级，YaRN 把它归成 NTK-aware 的一种手调。那是 Code Llama 的外推旋钮，别安到 Llama 3 预训练头上。

## 和改 rope_theta 差在哪

Llama 2：常见 $b=10^4$，预训练 $4\mathrm{k}$。Llama 3 / 3.1 公开 conf 把 `rope_theta` 提到 $5\times 10^5$，再在 $8\mathrm{k}\to 128\mathrm{k}$ 上继续预训练（六段、约 $800\mathrm{B}$ token，见 `meta-llama3-pretrain`）。

相同点：提高 $b$，高频在大 $m$ 上少转几圈，直觉和 NTK 一类。差别：

1. **时机。** `rope_theta` 是训练（含长窗 CPT）用的基频；NTK / YaRN 默认是推理或短微调时改公式。
2. **有没有在目标长度上见过梯度。** Meta 的叙事是模型在 128k 序列上真的反传过。只改 conf 里的 theta、权重还是 8k 的，是 分布外数据（OOD，即与训练数据明显不同的数据）。
3. **$s$ 还在不在。** 官方长窗模型推理时按训练长度用 RoPE，不必再套一层 YaRN。社区给老 8k 权外推到 32k / 128k 才需要 $s$。
4. **开源 `rope_type: llama3`。** 有的权重文件带 `factor`、`low_freq_factor`、`high_freq_factor`，按波长分段，和 YaRN 同类。Herd 论文写的是继续训 + 提高 theta。现场说「实现上可能有分段缩放，训练故事仍是长窗 CPT」，不要把 HuggingFace 字段说成 Meta 训练代码。

Dynamic NTK：每步用当前长度算 $s=\max(1,t/L)$。KV cache 必须存旋转前的 $k$，否则 $s$ 一变历史 key 全错。Llama 3.1 原生 128k 服务不要开这套。

## 一个具体错法

错法一：PI、NTK、YaRN、改 theta 四个开关一起拧，还不做短任务对照。近距（代码缩进、复制）和远距（文档 QA）要分开报。

错法二：逐 token 生成（decode） 时 RoPE 从 $0$ 重新计，cache 里已经有 $S$ 个 token。位置公式再漂亮也是错的。这和 OpenAI 风格的位置偏移是同一类 bug。

错法三：haystack 全对就宣称 128k 推理链完整。针能点到，多跳推理仍可能断。长窗训练怎么验收，见 `meta-llama3-pretrain`。

## 追问

- **为什么高频先坏？** $\theta$ 大，$m\theta$ 随 $m$ 转得快，过训练长度相位 OOD。PI 用牺牲高频的办法换低频安全。
- **NTK 微调为什么可能不如 PI？** 部分维外推，微调时这些通道仍 OOD。YaRN 低频强制插值，就是堵这个。
- **YaRN 的温度能单独用吗？** 能，但论文是和 by-parts 一起拟合的。只乘温度不改频率，长距相位还是没见过。
- **128k 时该上 GQA 还是 YaRN？** 两者正交。GQA 砍 KV 带宽（`meta-llama-gqa`）；YaRN / theta 砍位置 OOD。长窗上两者都疼。

## 相关题

- [[meta-llama-rope]]：先讲 RoPE 的相对位置性质，外推旋钮只讲到概念层；内容和本卡大量重叠。
- [[openai-long-ctx-train]]：长窗怎么训：改基频之后还要在真实长文档上续训，插值补不了没见过的长依赖。
