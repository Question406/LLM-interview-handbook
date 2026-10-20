---
id: coding-grpo-loss-agg
section: coding
order: 36
level: S
title: 白板：GRPO 的 token loss 怎么聚合成一个数？三种写法的长度偏置
quick: "seq-mean 给每个 token $1/(B|o_i|)$ 的权重，长的错答案被罚得轻；token-mean 和 Dr. GRPO 的常数归一没有这种长度偏置，pad 都不进分子分母。"
tags:
  - 完整编程练习
  - Coding
  - GRPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
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

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，CPU 浮点张量上验证；没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `loss_seq_mean(per_tok, mask)`：每条回答先对自己的有效 token 取平均，再对 B 条回答取平均。没有有效 token 的回答贡献 0，仍计入 B。
- `loss_token_mean(per_tok, mask)`：整个 batch 的有效 token loss 求和，除以有效 token 总数。
- `loss_const_norm(per_tok, mask, max_len)`：有效 token loss 求和，除以常数 `B * max_len`。`max_len` 是固定的正整数，且不小于 T。
- `per_tok` 和 `mask` 都是 `[B, T]`，`mask` 中 1 表示 response token，0 表示 prompt 或 pad。形状不一致、`max_len` 不合法时抛 `ValueError`。
- 全部被 mask 时三个函数都返回 0，并且能正常反传（梯度为 0，不出现 NaN）。

### 输入输出示例

```text
per_tok = [[1, 3, 99], [2, 4, 6]]
mask    = [[1, 1,  0], [1, 1, 1]]

loss_seq_mean               -> 3     # (2 + 4) / 2
loss_token_mean             -> 3.2   # 16 / 5
loss_const_norm(max_len=4)  -> 2     # 16 / (2 * 4)
```

### 解题思路与正确性

三种写法的共同点是先用 mask 把分子里的 pad 清零，pad 位置上的 99 不能进任何一项。区别只在分母：seq-mean 用每条回答自己的长度，token-mean 用全 batch 的有效 token 数，常数归一用固定的 `B * max_len`。不能拿 padding 长度 T 当作回答的真实长度。

因为分母不同，三种目标一般不相等，每个 token 拿到的梯度权重也不同。对 `per_tok` 求梯度就能直接看到这些权重，测试里把三种权重都检查了一遍。

分母为 0 的情况用 `clamp(min=1)` 处理：此时分子也是 0，结果是 0，梯度仍然有定义。

### 完整参考实现（Python 3）

```python
import torch


def _check_shapes(per_tok, mask):
    if per_tok.ndim != 2 or per_tok.shape != mask.shape:
        raise ValueError("per_tok and mask must both be [B, T], got "
                         f"{tuple(per_tok.shape)} and {tuple(mask.shape)}")


def loss_seq_mean(per_tok, mask):
    """每条回答内对有效 token 取平均，再对 B 条回答平均；空回答贡献 0，仍计入 B。"""
    _check_shapes(per_tok, mask)
    lengths = mask.sum(dim=-1).clamp(min=1)          # [B]，空回答的分母取 1
    per_seq = (per_tok * mask).sum(dim=-1) / lengths  # [B]
    return per_seq.mean()


def loss_token_mean(per_tok, mask):
    """整个 batch 的有效 token 一起平均；没有有效 token 时返回 0。"""
    _check_shapes(per_tok, mask)
    return (per_tok * mask).sum() / mask.sum().clamp(min=1)


def loss_const_norm(per_tok, mask, max_len):
    """有效 token 的 loss 总和除以常数 B * max_len（Dr. GRPO）。"""
    _check_shapes(per_tok, mask)
    batch, seq_len = per_tok.shape
    if not isinstance(max_len, int) or max_len < seq_len:
        raise ValueError(f"max_len must be an int >= T={seq_len}, got {max_len!r}")
    return (per_tok * mask).sum() / (batch * max_len)
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
per_tok = torch.tensor([[1.0, 3.0, 99.0], [2.0, 4.0, 6.0]], requires_grad=True)
mask = torch.tensor([[1.0, 1.0, 0.0], [1.0, 1.0, 1.0]])

# 三种聚合：seq = (2 + 4) / 2，token = 16 / 5，const = 16 / (2 * 4)；pad 上的 99 不参与
assert loss_seq_mean(per_tok, mask) == 3
assert torch.allclose(loss_token_mean(per_tok, mask), torch.tensor(3.2))
assert loss_const_norm(per_tok, mask, 4) == 2

# 梯度就是每个 token 的权重：seq-mean 是 1 / (B * |o_i|)，短回答的 token 权重更大
grad, = torch.autograd.grad(loss_seq_mean(per_tok, mask), per_tok)
assert torch.allclose(grad, torch.tensor([[0.25, 0.25, 0.0], [1 / 6, 1 / 6, 1 / 6]]))

# token-mean 和常数归一下，每个有效 token 权重相同，pad 权重为 0
grad, = torch.autograd.grad(loss_token_mean(per_tok, mask), per_tok)
assert torch.allclose(grad, mask / 5)
grad, = torch.autograd.grad(loss_const_norm(per_tok, mask, 4), per_tok)
assert torch.allclose(grad, mask / 8)

# 全部被 mask：返回 0，梯度也全是 0，不出现 NaN
all_masked = torch.zeros_like(mask)
zero = loss_token_mean(per_tok, all_masked)
assert zero == 0
assert torch.all(torch.autograd.grad(zero, per_tok)[0] == 0)
assert loss_seq_mean(per_tok, all_masked) == 0

# 空回答在 seq-mean 里贡献 0 但仍计入 B：只剩第二条回答的平均 4，再除以 2
one_empty = torch.tensor([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
assert loss_seq_mean(per_tok, one_empty) == 2

# 非法输入：max_len 小于 T，或 per_tok 和 mask 形状不一致
expect_value_error(loss_const_norm, per_tok, mask, 2)
expect_value_error(loss_token_mean, per_tok, mask[:, :2])
```

### 复杂度与追问

设 batch 有 B 条回答、padding 后长度为 T。三个函数的时间都是 O(B·T)，seq-mean 额外存 B 个回答长度，空间 O(B)。

- 追问「梯度累积时 token-mean 怎么写」：不能把每个 micro-batch 各自的 token-mean 再平均。要先算出整个 global batch 的有效 token 总数，每个 micro-batch 的分子都除以这个全局数，见下文「梯度累积」。

## 题怎么来的

clip 和 advantage 写对之后，还剩最后一步：把 `[B, T]` 的 token loss 聚合成一个标量。这一步决定每个 token 的梯度权重，写错不会报错，只会让回答长度慢慢漂移。它和 `fireworks-grpo-sft-loss` 是同一类题，那道题管单个 token 的权重，这道题管 reduction。

## 故意错误的起始片段（用于找 bug）

下面是题目给出的起始代码，故意写错了，不是参考答案。对照上面的接口找出它偏离契约的地方，正确实现和测试见「完整编程练习」。

```python
def grpo_loss(per_tok, mask):
    # per_tok: [B, T] = -min(r * A, clip(r) * A)，A 已经广播到每个 token
    # mask:    [B, T] 1 = response token，0 = prompt / pad
    return per_tok.mean(dim=-1).mean()
```

## 错在哪

`mask` 根本没用上。pad 位置的 logprob 是模型在 pad 上随便算出来的，advantage 又被广播到了那里，所以 `per_tok` 在 pad 上不是 0，梯度会流进 pad。就算先乘上 mask 再平均，分母仍然是 $T$，还是不对：$T$ 是这个 batch 的 padding 长度，换一个 batch 就会变，loss 的尺度也跟着乱跳。

## 三种正确写法

记 $\ell_{i,t}$ 为第 $i$ 条回答第 $t$ 个 token 的 loss，$|o_i|$ 为这条回答的 response 长度。

**先在序列内平均，再对序列平均**（GRPO 原文）：

$$
L = \frac{1}{B}\sum_i \frac{1}{|o_i|}\sum_t \ell_{i,t}
$$

每个 token 的权重是 $1/(B|o_i|)$。同样是 $A<0$，长回答里每个 token 分到的惩罚更小；同样是 $A>0$，短回答里每个 token 分到的奖励更大。Dr. GRPO 论文指出，这会让模型在答错时倾向于写得更长。

**整个 batch 按 token 平均**（DAPO 的 token-level loss）：

$$
L = \frac{1}{\sum_i |o_i|}\sum_i\sum_t \ell_{i,t}
$$

每个 token 权重相同，长回答的整体贡献更大。这是有意为之：长推理里出错的 token 也应该被罚到。它的缺点是分母随 micro-batch 里的 token 数变化。

**除以常数**（Dr. GRPO）：

$$
L = \frac{1}{B\cdot L_{\max}}\sum_i\sum_t \ell_{i,t}
$$

$L_{\max}$ 是生成长度上限，不是这个 batch 的 padding 长度，所以权重和 batch 里有多少 token 无关。Dr. GRPO 同时还去掉了 advantage 里除以组内 std 的那一步。

## 直接看权重

对 `per_tok` 求梯度，得到的就是每个 token 的权重，长度偏置一眼就能看出来。练习里的例子中，seq-mean 给 2 个 token 的短回答每个 token $0.25$，给 3 个 token 的长回答每个 token $1/6$；token-mean 给每个有效 token $1/5$；常数归一（$L_{\max}=4$）给每个有效 token $1/8$。pad 位置的权重都是 0。

## 梯度累积

token-mean 最容易在 micro-batch 上写错。如果每个 micro-batch 除以自己的 token 数，再把几个 micro-batch 的 loss 相加或平均，结果并不等于整个 batch 的 token-mean：token 少的 micro-batch 被放大了。正确做法是先算出整个 global batch 的有效 token 数（多卡时做一次 all-reduce），每个 micro-batch 都除以这个全局数，然后直接累加梯度。梯度累积和数据并行怎么对齐见 `sys-grad-accum`。

## 追问

**选哪个？** 没有唯一答案。在长推理任务上，token-mean 和常数归一都比 seq-mean 稳，回答长度不会被 loss 本身推着走。常数归一的 loss 数值会随 batch 里有效 token 数变化，学习率要按这个尺度调。

**KL 项和 entropy 项也要这样聚合吗？** 要用同一种。policy loss 用 token-mean、KL 用 seq-mean，相当于给两项配了不同的长度权重，$\beta$ 的含义也跟着变了。

**全被 mask 掉的回答怎么办？** 被截断到长度 0 或被 overlong 过滤掉的回答，`mask.sum(-1)` 是 0，seq-mean 必须 clamp 分母，否则会出现 0/0。练习里的约定是让这条回答贡献 0、仍计入 $B$，这会把其他回答的权重一起稀释；更合理的做法通常是把它排除出 $B$，分母改用有效回答数。哪些位置应该是 0 见 `sys-adv-bcast`、`sys-eos-mask`。

## 相关题

- [[coding-loss-atlas]]：总览题，各种 loss 都写成「权重 × logprob」，这里讨论的聚合方式就是权重里的那个归一化因子。
- [[sys-adv-bcast]]：聚合之前的一步，序列级优势怎么铺到 token 上、哪些位置的 mask 必须是 0。
- [[coding-cispo]]：CISPO 沿用 DAPO 的 token-level 平均，那张讲它和 PPO clip 在出界 token 上的梯度差别。
- [[coding-gspo-seq-ratio]]：GSPO 把 ratio 和 clip 挪到序列级，长度归一化放在 log ratio 的均值里，和这里的长度偏置可以对照。
