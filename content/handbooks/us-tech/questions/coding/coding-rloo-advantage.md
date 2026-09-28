---
id: coding-rloo-advantage
section: coding
order: 37
level: A
title: 白板：RLOO 的 leave-one-out baseline，向量化写法和它跟 GRPO 差在哪
quick: >-
  $b_i = \frac{1}{G-1}\sum_{j\ne i} r_j$，向量化是 `(sum - r) / (G - 1)`。
  $r_i - b_i = \frac{G}{G-1}(r_i - \bar r)$，和减组均值只差一个常数倍。
  GRPO 多出来的是除以组内 std，它按 prompt 重新加权。reshape 的顺序必须和 rollout 的排布一致。
tags:
  - Coding
  - GRPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Back to Basics: Revisiting REINFORCE Style Optimization for Learning from Human Feedback in LLMs"
    url: https://arxiv.org/abs/2402.14740
    type: primary
  - title: "Buy 4 REINFORCE Samples, Get a Baseline for Free!"
    url: https://openreview.net/forum?id=r1lgTGL5DE
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

每个 prompt 采 $G$ 条回答，每条一个标量奖励。RLOO 用「其余 $G-1$ 条的平均」当 baseline。题目让你写向量化版本，再问它和 GRPO 的组内归一化有什么关系。

rollout 的排布是 `prompts.repeat_interleave(G)`，也就是 `[p0, p0, ..., p0, p1, p1, ...]`。给你的代码：

```python
def rloo_advantage(rewards, G):
    # rewards: [B * G]
    r = rewards.view(G, -1)
    baseline = (r.sum(dim=0, keepdim=True) - r) / G
    return (r - baseline).reshape(-1)
```

## 错在哪

两处。

`view(G, -1)` 按行切，第一行是前 $B$ 个奖励。排布是 `repeat_interleave`，同一个 prompt 的 $G$ 条是连续的，应该 `view(-1, G)`，沿 `dim=1` 求和。写反了之后「组」里混着不同 prompt 的回答，baseline 失去意义。这个 bug 不报错，$B = G$ 时形状完全一样。

分母应该是 $G-1$。除以 $G$ 的 baseline 是 $\frac{G-1}{G}$ 倍的 leave-one-out 均值，奖励非负时 baseline 偏小，advantage 整体往正的方向偏，每条回答都被推高一点。

```python
def rloo_advantage(rewards, G):
    assert G >= 2
    r = rewards.view(-1, G)
    baseline = (r.sum(dim=1, keepdim=True) - r) / (G - 1)
    return (r - baseline).reshape(-1)
```

## 为什么不用自己

baseline 不能依赖 $y_i$ 本身。$\mathbb{E}[b\,\nabla\log\pi(y_i)] = 0$ 要求 $b$ 和 $y_i$ 独立。其余 $G-1$ 条和 $y_i$ 独立采样，所以 leave-one-out 是无偏的。

但包含自己的组均值其实也只差一个常数：

$$
r_i - \bar r = r_i - \frac{r_i + \sum_{j\ne i} r_j}{G} = \frac{G-1}{G}\Big(r_i - \frac{1}{G-1}\sum_{j\ne i} r_j\Big)
$$

减组均值 = RLOO advantage 乘 $\frac{G-1}{G}$。方向无偏，只是尺度缩小，等价于学习率小一点。面试里这一步能讲出来比写对代码更重要。

## 和 GRPO 的区别

GRPO 的 advantage 是 $(r_i - \bar r)/\mathrm{std}(r)$。减均值部分和 RLOO 只差常数倍。除以 std 不是常数：每个 prompt 的 std 不同，奖励差异小的 prompt（几乎全对或几乎全错）被放大。Dr. GRPO 认为这是一种按难度的偏置，建议去掉。全对或全错时 std 为 0，处理见 `anthropic-grpo-debug`。

## 验证

```python
import torch

G = 4
rewards = torch.tensor([1., 0., 0., 1.,  0., 0., 0., 1.])
a = rloo_advantage(rewards, G)
r = rewards.view(-1, G)
ref = torch.stack([r[:, i] - torch.cat([r[:, :i], r[:, i+1:]], 1).mean(1) for i in range(G)], 1)
assert torch.allclose(a, ref.reshape(-1))
assert torch.allclose(a, (G / (G - 1)) * (r - r.mean(1, keepdim=True)).reshape(-1))
```

## 追问

**组里全是 0 或全是 1？** leave-one-out 之后 advantage 全是 0，这个 prompt 没有梯度。和 GRPO 一样，采到这种组等于浪费算力，DAPO 的动态采样就是把它们过滤掉再补采。

**奖励里有 per-token 的 KL 惩罚怎么办？** RLOO 论文把 KL 并进序列级奖励，$r - \beta\,\mathrm{KL}$ 之后再做 leave-one-out。放在奖励还是放在 loss 见 `sys-kl-place`。

**$G = 2$ 时是什么？** $A_1 = r_1 - r_2$，$A_2 = r_2 - r_1$。两条回答互为 baseline，形式上接近一对偏好数据。
