---
id: arch-moe-noaux
section: arch
order: 21
level: S
title: DeepSeek-V3 无辅助负载均衡：expert bias 怎么更新，和 aux loss 差在哪？
quick: >-
  每个 expert 有一个 bias $b_i$，路由时用分数加 $b_i$ 选 top-$k$；过载就减小 $b_i$，欠载就增大。Bias
  不进主梯度，所以不会像 aux 损失（loss）那样和语言建模目标抢路由参数。加权时 gating 仍用未加 bias 的 affinity，V3
  另外保留了一个极小的 sequence-wise aux。
tags:
  - MoE
  - DeepSeek
  - Load Balancing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: DeepSeek-V3 Technical Report
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
---

DeepSeek-V3 给每个专家配一个 bias $b_i$，只在选 top-$k$ 时加到路由分数上：某个专家过载就把 $b_i$ 调小，欠载就调大。Aux loss 是把「专家要平均」写进可 backpropagation 的惩罚项，和 next-token loss 一起更新同一套路由参数；V3 把均衡控制挪到了路由决策外面的偏置上，主损失尽量只做语言建模。

## 机制

对 token $t$、专家 $i$，先算 affinity（V3 用 sigmoid gating）：

$$
s_{i,t}=\sigma(u_t^\top e_i).
$$

选 top-$k$ 时看的是加了偏置的 $s_{i,t}+b_i$；给 expert 输出加权时，仍用未加 $b_i$ 的 $s_{i,t}$ 在选中的 $k$ 个专家上 normalization。这样 $b_i$ 只改「谁进 top-$k$」，不直接改「选中之后贡献多大」。

$b_i$ 按 batch 负载做符号更新：expert $i$ 的 token 份额高于均值，$b_i\leftarrow b_i-\gamma$；低于均值就 $+\gamma$。它是控制器的状态，不算网络权重，也不走 backpropagation。

举个例子，一个 batch 里 expert 3 吃了 40% 的 token，expert 7 几乎没人选。Aux loss 会立刻给 router 一个「别再选 3」的梯度，可能把本来适合 3 的 token 硬推走。Bias 方案只是把 $b_3$ 调低、$b_7$ 调高，下一小步的 top-$k$ threshold 变了，但当前被选中 token 的 gating weights 仍按 $s_{i,t}$ 算。

## 和 aux loss 的差别

Switch Transformer 一类的 aux loss 近似 $N\sum_i f_i P_i$，也就是实际频率乘平均 gating 概率。$\lambda$ 太小热点还在，$\lambda$ 太大 router 会为了平均牺牲语义匹配。无辅助方案把这个折中从 loss 里拿掉，负载均衡不再直接改变主损失的梯度。

V3 仍保留了一个极小的 sequence-wise complementary aux loss（论文量级 $\alpha=10^{-4}$），用来压住极端不平衡。所以面试别说成「完全没有任何均衡项」。

## 追问

**推理时 $b_i$ 怎么处理？**
训练末期的 bias 可以冻结进 checkpoint，或者推理时关掉动态更新、只保留训练学到的 router。训推路由不一致是另一道系统题。

**和 capacity / token drop 是什么关系？**
互不替代。Bias 降低热点出现的概率，capacity 是硬上限，见 capacity 卡。

**手写的话怎么写？**
先 `scores = sigmoid(x @ E.T)`，再 `choice = topk(scores + bias)`，最后 `gates = normalize(scores[choice])`。别把 bias 加进 gates。
