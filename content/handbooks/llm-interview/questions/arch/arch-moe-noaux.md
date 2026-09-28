---
id: arch-moe-noaux
section: arch
order: 21
level: S
title: DeepSeek-V3 无辅助负载均衡：expert bias 怎么更新，和 aux loss 差在哪？
quick: >-
  路由分数加上每个 expert 的 bias $b_i$ 再做 top-$k$；过载就减小 $b_i$，欠载就增大。Bias
  不进主梯度，所以不会像 aux loss 那样和语言建模目标抢参数。门控权重仍用未加 bias 的 affinity。
tags:
  - MoE
  - DeepSeek
  - Load Balancing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

Aux loss 把「专家要平均」写进可反传的惩罚项，和 next-token loss 抢同一套 router 参数。DeepSeek-V3 把均衡控制挪到路由决策的外部偏置上，主损失尽量只做语言建模。

## 机制

对 token $t$、expert $i$，先算 affinity（V3 用 sigmoid 门控）：

$$
s_{i,t}=\sigma(u_t^\top e_i).
$$

选择 top-$k$ 时看的是加偏置后的分数 $s_{i,t}+b_i$；真正加权 expert 输出时，仍用未加 $b_i$ 的 $s_{i,t}$ 在被选中的 $k$ 个专家上归一化。这样 $b_i$ 只改「谁进 top-$k$」，不直接改「选中之后贡献多大」。

$b_i$ 按 batch 负载做符号更新：expert $i$ 的 token 份额高于均值则 $b_i\leftarrow b_i-\gamma$，低于均值则 $+\gamma$。它是控制器状态，不是网络权重，不走反向传播。

## 和 aux loss 的差别

Switch Transformer 一类 aux loss 近似 $N\sum_i f_i P_i$（实际频率 $\times$ 平均门控概率）。$\lambda$ 太小热点仍在，$\lambda$ 太大 router 为了平均而牺牲语义匹配。无辅助方案把这个折中从 loss 里拿掉：主梯度不再被「必须均匀」污染。

V3 仍保留一个极小的 sequence-wise complementary aux loss（论文量级 $\alpha=10^{-4}$），用来压极端不平衡，均衡没有完全交给主损失。面试别说成「完全没有任何均衡项」。

## 例子

一个 batch 里 expert 3 吃了 40% token、expert 7 几乎没人。Aux loss 会立刻给 router 一个「别再选 3」的梯度，可能把本来适合 3 的 token 硬推走。Bias 方案只是把 $b_3$ 下调、$b_7$ 上调，下一小步 top-$k$ 门槛变了，但当前被选中 token 的门控权重仍按 $s_{i,t}$ 算。

## 追问

- **推理时 $b_i$ 怎么办？** 训练末期的 bias 可以冻结进 checkpoint，或推理关掉动态更新、只保留训练学到的 router。训推路由不一致是另一道系统题。
- **和 capacity / token drop？** Bias 降低热点概率，capacity 是硬上限。两者正交，见 capacity 卡。
- **手写时写什么？** 先 `scores = sigmoid(x @ E.T)`，`choice = topk(scores + bias)`，`gates = normalize(scores[choice])`。别把 bias 加进 gates。
