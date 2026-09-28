---
id: meta-multi-token
section: meta
order: 10
level: A
title: Meta：multi-token prediction 训练目标是什么，推理怎么用
quick: >-
  共享主干，在同一位置用 $n$ 个独立头并行预测接下来 $n$ 个 token。训练是辅助多步 CE，不是把自回归改成非自回归生成。默认推理仍用下一
  token 头；额外头可以当自投机草稿，一次前向提出多步再验证，论文报过大约 $3\times$ 的 decode 加速。
tags:
  - Meta
  - Llama
  - Multi-token Prediction
  - Speculative Decoding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Better & Faster Large Language Models via Multi-token Prediction
    url: https://arxiv.org/abs/2404.19737
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: secondary
---

FAIR 的 multi-token prediction 论文（Gloeckle et al., 2024）是 GenAI 岗很合适的「读过公开工作吗」题。它不是 Llama 3 官方预训练目标（Herd 论文主线仍是 next-token），别说成「Llama 3 就是这样训的」。要能把训练目标和推理用法拆开。

## 训练：同一隐状态，多个未来头

普通 LM：位置 $t$ 的隐状态 $h_t$ 过一个头，预测 token $t+1$。Multi-token：共享 trunk，上面 $n$ 个独立输出头，在**同一个** $h_t$ 上分别预测 $t+1,\ldots,t+n$。损失是 $n$ 个交叉熵的平均（或加权）：

$$
\mathcal{L} = \frac{1}{n}\sum_{k=1}^{n} \mathrm{CE}\big(f_k(h_t),\; x_{t+k}\big)
$$

关键：训练时头与头之间**没有**自回归依赖。第 $2$ 个头预测 $t+2$，并不先吃自己采样的 $t+1$。Teacher forcing 的是真实未来 token 当标签，不是把草稿喂回去。论文把这当辅助任务：主干被逼着在 $h_t$ 里提前规划后面几步，而不只是「下一个词最像什么」。

实现上 $n$ 个 lm_head 都是 $[D, V]$，显存和计算都会涨。论文常用 $n=4$，并用交错前向、不把所有头的激活同时物化，声称训练时间可以和基线打平。面试提到这一句即可，不要现场发明他们的 kernel。$n$ 不是越大越好：后面的头更难，表示收益和投机接受率都会饱和。

和 DeepSeek 后来的 MTP 不是同一张图：那种往往在深度方向再叠一块，用真实/预测的下一 token 接着往前走。Meta 这篇是**并行独立头**。现场被追问就说「我按 2024 这篇讲并行头；串行 MTP 是另一条实现」。

## 推理：默认仍是 next-token，额外头拿去投机

默认生成：只用 $k=1$ 那个头，行为就是普通自回归。质量收益来自训练时主干学到的表示，不是推理时一次吐 $n$ 个词当最终答案。直接把 $n$ 个头的 argmax 拼成一段输出，错误会沿草稿传播，这不是论文的主用法。

加速用法是 **self-speculative decoding**：额外头提出长度为 $n-1$ 的草稿，再用主 next-token 头（同一模型）在一次前向里验证。接受前缀直到第一次不一致，回滚 cache。论文报 4-token 训练的模型 decode 可以到大约 $3\times$，代码上接受长度更长。这和「另训一个小草稿模型」的投机解码同构，只是草稿头已经在大模型上。

验收：质量看 HumanEval / MBPP 这类生成任务，论文在 13B 上相对 next-token 基线有几个点的题量提升，且增益随规模变大。速度看平均接受长度，不是看「头数 $n$」。$n$ 太大，后面的头很弱，草稿频繁被拒，加速会掉。投机路径还要和 KV cache 对齐：拒绝后必须把 cache 滚到接受前缀，不能只改输出文本。这和普通投机解码是同一条不变量。

## 一个具体错法

错法：把 multi-token 说成 BERT 式双向、或说成非自回归一次性生成整句。因果 mask 还在，主干仍是 decoder-only，只是损失看见了更远的标签。另一个错法：推理时把 $n$ 个头的分布平均起来当 next-token，会把 $t+2$ 的预测污染 $t+1$。

和 tokenizer 的关系（`meta-llama3-tokenizer`）：$n$ 个未来 token 的粒度取决于词表。代码上 BPE 更「整块」，论文也说代码收益更明显；这是观察，不是证明。


规格上记住 shape：主干输出 $[B, T, D]$，每个头把每个位置映到词表，$[B, T, V]$。训练标签是把序列向未来错 $k$ 步，不是把同一位置的词表复制 $n$ 份。

面试结尾我会主动说：Llama 3 官方预训练叙事仍是 next-token，这篇是 FAIR 的并行工作，不要说成「Llama 3 的训练目标换了」。

## 追问

- **训练时 $n$ 个头的标签会泄漏未来吗？** 标签是 CE 的 target，不进主干的输入。输入仍是因果前缀。泄漏指的是把 $x_{t+k}$ 当输入，不是当 loss 标签。
- **能不能只在后训练加这些头？** 论文主实验是预训练目标。后训练加头可以当投机插件，但表示收益未必能补回来，要做对比，不要口头保证。
- **和 beam search 的差别？** Beam 是推理搜索；multi-token 是训练目标 + 可选投机。不是一回事。
- **失败模式？** 草稿头在开放域文本上接受率低于代码；验证头必须是校准过的 next-token 头，否则会系统性接受错草稿。
- **和 Medusa / EAGLE 的差别？** 都是自投机族。这篇是训练时就用多头 CE；Medusa 一类更多是在已有 next-token 模型上加头。别把名字混成一种算法。
- **推理必须把 $n$ 个头都装上吗？** 不必。只要质量、不要加速时可以丢掉草稿头，只留 $k=1$。训练代价已经付过，推理图可以更瘦。
