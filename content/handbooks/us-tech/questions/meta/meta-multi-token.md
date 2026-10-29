---
id: meta-multi-token
section: meta
order: 10
level: A
title: Meta：multi-token prediction 训练目标是什么，推理怎么用
quick: >-
  Multi-token prediction 在同一隐状态上用 $n$ 个独立头预测未来 $n$ 个 token，训练仍保持因果输入。推理可只留下一
  token 头，也可让额外头提出草稿、主头验证；论文报告过约 $3\times$ decode 加速，但效果取决于接受长度。
tags:
  - Meta
  - Llama
  - Multi-token Prediction
  - Speculative Decoding
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Better & Faster Large Language Models via Multi-token Prediction
    url: 'https://arxiv.org/abs/2404.19737'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: secondary
---

## 可以这样回答

Meta 这篇 multi-token prediction 用同一个隐状态，并行预测后面多个 token，增加训练监督；推理时仍可按普通 autoregressive 生成，也可让额外头提草稿加速。例如第一个头预测下一词，第二个头预测再下一词，但训练中第二个头不会先读第一个头 sampling 的结果。这里讨论的是 FAIR 的 Gloeckle et al., 2024 工作，Llama 3 Herd 的主线仍是 next-token。

训练时这些头之间没有 autoregressive 依赖。第 $2$ 个头预测 $t+2$，并不先吃自己 sampling 的 $t+1$。Teacher forcing 的是真实未来 token 当标签，不是把草稿喂回去。论文把这当辅助任务：主干被逼着在 $h_t$ 里提前规划后面几步，而不只是「下一个词最像什么」。

## 技术备查

Meta 这篇 multi-token prediction 用同一个隐状态，并行预测后面多个 token，增加训练监督；推理时仍可按普通 autoregressive 生成，也可让额外头提草稿加速。例如第一个头预测下一词，第二个头预测再下一词，但训练中第二个头不会先读第一个头 sampling 的结果。这里讨论的是 FAIR 的 Gloeckle et al., 2024 工作，Llama 3 Herd 的主线仍是 next-token。

## 训练：同一隐状态，多个未来头

普通 LM：位置 $t$ 的隐状态 $h_t$ 过一个头，预测 token $t+1$。Multi-token：共享 trunk，上面 $n$ 个独立输出头，在**同一个** $h_t$ 上分别预测 $t+1,\ldots,t+n$。损失是 $n$ 个 cross entropy 的平均（或加权）：

$$
\mathcal{L} = \frac{1}{n}\sum_{k=1}^{n} \mathrm{CE}\big(f_k(h_t),\; x_{t+k}\big)
$$

训练时这些头之间没有 autoregressive 依赖。第 $2$ 个头预测 $t+2$，并不先吃自己 sampling 的 $t+1$。Teacher forcing 的是真实未来 token 当标签，不是把草稿喂回去。论文把这当辅助任务：主干被逼着在 $h_t$ 里提前规划后面几步，而不只是「下一个词最像什么」。

实现上 $n$ 个 lm_head 都是 $[D, V]$，显存和计算都会涨。论文常用 $n=4$，并用交错前向、不把所有头的激活同时物化，声称训练时间可以和基线打平。具体 kernel 不在这里作额外推断。$n$ 不是越大越好：后面的头更难，表示收益和投机接受率都会饱和。

和 DeepSeek 后来的 MTP 不是同一张图：那种往往在深度方向再叠一块，用真实/预测的下一 token 接着往前走。Meta 这篇是**并行独立头**。所以讨论 2024 这篇时，要和串行 MTP 的实现区分。

## 推理：默认仍是 next-token，额外头拿去投机

默认生成：只用 $k=1$ 那个头，行为就是普通 autoregressive。质量收益来自训练时主干学到的表示，不是推理时一次吐 $n$ 个词当最终答案。直接把 $n$ 个头的 argmax 拼成一段输出，错误会沿草稿传播，这不是论文的主用法。

加速用法是 **self-speculative decoding**：额外头提出长度为 $n-1$ 的草稿，再用主 next-token 头（同一模型）在一次前向里验证。接受前缀直到第一次不一致，回滚 cache。论文报 4-token 训练的模型 逐 token 生成（decode） 可以到大约 $3\times$，代码上接受长度更长。这和「另训一个小草稿模型」的 speculative decoding 同构，只是草稿头已经在大模型上。

验收：质量看 HumanEval / MBPP 这类生成任务，论文在 13B 上相对 next-token 基线有几个点的题量提升，且增益随规模变大。速度看平均接受长度，不是看「头数 $n$」。$n$ 太大，后面的头很弱，草稿频繁被拒，加速会掉。投机路径还要和 KV cache 对齐：拒绝后必须把 cache 滚到接受前缀，不能只改输出文本。这和普通 speculative decoding 是同一条不变量。

主干仍是带因果 mask 的 decoder-only，未来 token 只作为损失标签，不作为输入。因此它与 BERT 式双向编码、非 autoregressive 整句生成不同。推理时也不能把 $n$ 个头的分布平均成 next-token 分布，否则 $t+2$ 的预测会污染 $t+1$。

和 tokenizer 的关系（`meta-llama3-tokenizer`）：$n$ 个未来 token 的粒度取决于 vocabulary。代码上 BPE 更「整块」，论文也说代码收益更明显；这是观察，不是证明。


从 shape 看，主干输出 $[B, T, D]$，每个头把每个位置映到 vocabulary，$[B, T, V]$。训练标签是把序列向未来错 $k$ 步，不是把同一位置的 vocabulary 复制 $n$ 份。

使用这些头时，要分别测训练带来的质量收益和投机带来的速度收益，避免只按头数估计加速。

## 追问

**训练时 $n$ 个头的标签会泄漏未来吗？**
标签是 cross entropy loss（CE） 的 target，不进主干的输入。输入仍是因果前缀。泄漏指的是把 $x_{t+k}$ 当输入，不是当 loss 标签。
**能不能只在后训练加这些头？**
论文主实验是预训练目标。后训练加头可以当投机插件，但表示收益未必能补回来，要做对比，不要口头保证。
**和 beam search 的差别？**
Beam 是推理搜索；multi-token 是训练目标 + 可选投机。不是一回事。
**失败模式？**
草稿头在开放域文本上接受率低于代码；验证头必须是 calibration 过的 next-token 头，否则会系统性接受错草稿。
**和 Medusa / EAGLE 的差别？**
都是自投机族。这篇是训练时就用多头 CE；Medusa 一类更多是在已有 next-token 模型上加头。别把名字混成一种算法。
**推理必须把 $n$ 个头都装上吗？**
不必。只要质量、不要加速时可以丢掉草稿头，只留 $k=1$。训练代价已经付过，推理图可以更瘦。

## 相关题

- [[nvidia-spec-medusa]]：Medusa 一类是在已有 next-token 模型上加草稿头，这篇是预训练时就加多步目标。
- [[google-spec-decode]]：额外头当草稿之后，无损性靠的是那张卡讲的 rejection sampling 验证。
