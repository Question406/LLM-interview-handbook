---
id: coding-grpo-loss-agg
section: coding
order: 36
level: S
title: 白板：GRPO 的 token loss 怎么聚合成一个数？三种写法的长度偏置
quick: >-
  先每条回答内 token 平均、再对回答平均，每个 token 的梯度权重是 $1/(B|o_i|)$，长的错答案被罚得轻。
  整个 batch 按 token 平均，权重是 $1/\sum_i|o_i|$，但分母跟着 micro-batch 变。
  Dr. GRPO 除以常数 $B\cdot L_{\max}$。pad 永远不进分子和分母。
tags:
  - Coding
  - GRPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Understanding R1-Zero-Like Training (Dr. GRPO)
    url: https://arxiv.org/abs/2503.20783
    type: primary
  - title: "DAPO: An Open-Source LLM Reinforcement Learning System at Scale"
    url: https://arxiv.org/abs/2503.14476
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

clip 和 advantage 写对之后，还剩最后一步：`[B, T]` 的 token loss 怎么变成一个标量。这一步决定每个 token 的梯度权重，写错不会报错，只会让回答长度慢慢漂。和 `fireworks-grpo-sft-loss` 是同一类题，那道管单个 token 的权重，这道管 reduction。

给你的代码：

```python
def grpo_loss(per_tok, mask):
    # per_tok: [B, T] = -min(r*A, clip(r)*A)，A 已经广播到每个 token
    # mask:    [B, T] 1 = response token，0 = prompt / pad
    return per_tok.mean(dim=-1).mean()
```

## 错在哪

`mask` 没用上。pad 位置的 logprob 是模型在 pad 上随便算出来的，advantage 又被广播过去了，`per_tok` 在 pad 上不是 0，梯度会流进 pad。先乘 mask 再平均，分母仍然是 $T$，也不对：$T$ 是这个 batch 的 padding 长度，换一个 batch 就变，loss 的尺度跟着乱跳。

## 三种正确写法

写 $\ell_{i,t}$ 为第 $i$ 条回答第 $t$ 个 token 的 loss，$|o_i|$ 是它的 response 长度。

**先序列内平均，再对序列平均**（GRPO 原文）：

$$
L = \frac{1}{B}\sum_i \frac{1}{|o_i|}\sum_t \ell_{i,t}
$$

每个 token 的权重是 $1/(B|o_i|)$。同样 $A<0$，长回答里每个 token 分到的惩罚更小；同样 $A>0$，短回答里每个 token 分到的奖励更大。Dr. GRPO 论文指出，这会让模型在答错时倾向写得更长。

**整个 batch 按 token 平均**（DAPO 的 token-level loss）：

$$
L = \frac{1}{\sum_i |o_i|}\sum_i\sum_t \ell_{i,t}
$$

每个 token 权重相同。长回答整体贡献更大，这是有意的：长推理里出错的 token 也要被罚到。

**除以常数**（Dr. GRPO）：

$$
L = \frac{1}{B\cdot L_{\max}}\sum_i\sum_t \ell_{i,t}
$$

$L_{\max}$ 是生成长度上限，不是这个 batch 的 padding 长度。权重和 batch 里有多少 token 无关。Dr. GRPO 同时去掉了 advantage 里除以组内 std 的那一步。

```python
def loss_seq_mean(per_tok, mask):
    per_seq = (per_tok * mask).sum(-1) / mask.sum(-1).clamp(min=1)
    return per_seq.mean()

def loss_token_mean(per_tok, mask):
    return (per_tok * mask).sum() / mask.sum().clamp(min=1)

def loss_const_norm(per_tok, mask, max_len):
    return (per_tok * mask).sum() / (per_tok.shape[0] * max_len)
```

## 直接看权重

对 `per_tok` 求梯度，得到的就是每个 token 的权重，一眼能看出长度偏置。

```python
import torch

mask = torch.tensor([[1., 1., 0., 0.], [1., 1., 1., 1.]])
per_tok = torch.zeros(2, 4, requires_grad=True)
g, = torch.autograd.grad(loss_seq_mean(per_tok, mask), per_tok)
# 第一条每个 token 1/4，第二条每个 token 1/8
g, = torch.autograd.grad(loss_token_mean(per_tok, mask), per_tok)
# 所有有效 token 都是 1/6
```

## 梯度累积

token-mean 最容易在 micro-batch 上写错。每个 micro-batch 自己除以自己的 token 数，再把几个 micro-batch 的 loss 相加或平均，结果不等于整个 batch 的 token-mean：token 少的 micro-batch 被放大了。正确做法是先把整个 global batch 的有效 token 数算出来（多卡时 all-reduce 一下），每个 micro-batch 都除以这个全局数，然后直接累加梯度。累积和数据并行怎么对齐见 `sys-grad-accum`。

## 追问

**选哪个？** 没有唯一答案。长推理任务上 token-mean 和常数归一都比 seq-mean 稳，长度不会被 loss 本身推着走。常数归一的 loss 数值随 batch 里有效 token 数变化，学习率要按这个尺度调。

**KL 项和 entropy 项也要这样聚合吗？** 要用同一种。policy loss 用 token-mean、KL 用 seq-mean，等于给两项配了不同的长度权重，$\beta$ 的含义跟着变。

**全被 mask 掉的回答怎么办？** 截断到长度 0，或者被 overlong 过滤掉的回答，`mask.sum(-1)` 是 0，seq-mean 必须 clamp 分母，并且这条回答不该计入 $B$。哪些位置该是 0 见 `sys-adv-bcast`、`sys-eos-mask`。
