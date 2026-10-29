---
id: code-alibi
section: coding
order: 45
level: A
title: 手写 ALiBi：斜率怎么排，bias 加在 scores 上，decode 用绝对距离
quick: "ALiBi 不动 $Q,K$，只在 softmax 前给 scores 加一个线性距离惩罚 $-m_h(q-k)$，第 $h$ 个头的斜率是 $m_h=2^{-8h/H}$。decode 时 query 的位置要用当前的绝对位置，当成 0 的话 bias 会整个反过来。"
tags:
  - ALiBi
  - Position
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Train Short, Test Long: Attention with Linear Biases"
    url: https://arxiv.org/abs/2108.12409
    type: primary
---

## 题目描述

为 attention 分数生成 ALiBi 的按头线性位置偏置。位置使用序列中的绝对位置；本题只生成偏置，不自行添加因果或 padding mask。

### 接口与数值约定

- `alibi_bias(q_pos, k_pos, slopes)`：输入分别为 `[Tq]`、`[Tk]` 的整数位置，以及 `[H]` 的正斜率。返回 `[H,Tq,Tk]`，第 h 个头、query i、key j 的值定义为 `-slopes[h] * (q_pos[i] - k_pos[j])`。
- `alibi_slopes(n_heads)`：返回长度为 H 的浮点斜率。H 为 2 的幂时，第 i 项（i 从 0 开始）为 `2 ** (-8*(i+1)/H)`；否则先取不超过 H 的最大 2 的幂 n 的完整斜率，再追加 2n 头序列下标 1、3、5……中的前 H-n 项。这是本卡现有实现采用的斜率约定，不能把它误写成另一套序列。

### 示例

```text
q_pos = [2], k_pos = [0,1,2], slopes = [0.5]
alibi_bias(...) -> [[[-1.0,-0.5,0.0]]]
alibi_slopes(2) -> [0.0625,0.00390625]
```

小型 CPU 练习只需验证形状与数值，不涉及实际长上下文模型的训练。

## 解题思路与参考答案

ALiBi 不改 $Q,K$，只在 softmax 之前给 scores 加一个和距离成正比的惩罚 $-m_h(q-k)$，每个头一个斜率，离得越远扣得越多。面试常拿它和 RoPE 对比：RoPE 旋转 $Q,K$，ALiBi 只改 logits。BLOOM 和 MPT 用的就是 ALiBi。

写错通常在两处。一是把距离写成 $|q-k|$，结果 causal 场景下未来位置也拿到一个有限的分数；未来位置应该先被 $-\infty$ 打掉。二是 decode 时把 query 位置当成 0，比如 cache 里已经有 $S$ 个 token，对它们的 bias 本该是 $-(S-1)m,\ldots,-m,0$，却变成了 $0,-m,-2m,\ldots$ 的反序，最近的 token 被扣得最重。

## 斜率与 bias

$H$ 是 2 的幂时：

$$
m_h=2^{-8h/H},\quad h=1,\ldots,H.
$$

$H=8$ 时就是 $1/2,1/4,\ldots,1/256$。$H$ 不是 2 的幂时，按论文附录的做法从 $2H$ 那组斜率里抽奇数项补齐，白板上提一句就行。

$$
b_{h,q,k}=-m_h\cdot(q-k).
$$

causal 下 $q\ge k$，距离非负，越远越负。这个 bias 加在 $QK^\top/\sqrt{d}$ 之后、softmax 之前。

```python
import math
import torch


def alibi_slopes(n_heads):
    n = 2 ** int(math.floor(math.log2(n_heads)))
    step = 2 ** (-8 / n)
    slopes = [step ** (i + 1) for i in range(n)]
    if n < n_heads:
        extra = alibi_slopes(2 * n)[1::2][: n_heads - n]
        slopes = slopes + extra.tolist()
    return torch.tensor(slopes[:n_heads])


def alibi_bias(q_pos, k_pos, slopes):
    # slopes: [H]；q_pos: [Tq], k_pos: [Tk] → [H, Tq, Tk]
    dist = q_pos[:, None] - k_pos[None, :]
    return -slopes[:, None, None] * dist.to(slopes.dtype)
```

Prefill 处理输入并建立缓存时，`q_pos = k_pos = arange(T)`。decode 时 `q_pos = [S-1]`，`k_pos = arange(S)`。KV cache 里的 K 不用重新乘斜率，因为 bias 每次现场算。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

先用显式斜率 0.5 手算距离惩罚，位置差 0、1、2 对应 0、-0.5、-1。斜率生成另外检查非 2 的幂次头数的长度和正值。

```python
bias = alibi_bias(torch.tensor([2]), torch.tensor([0, 1, 2]), torch.tensor([0.5]))
torch.testing.assert_close(bias, torch.tensor([[[-1.0, -0.5, 0.0]]]))
slopes = alibi_slopes(3)
assert slopes.shape == (3,) and torch.isfinite(slopes).all() and (slopes > 0).all()
print("simple tests passed")
```

## 追问

**为什么能外推？**
距离是相对的。训练 1k、推理 8k，只是距离更大、惩罚更重，没有模型没见过的绝对位置 id。

**能和 RoPE 一起用吗？**
一般二选一，叠在一起会把距离编码两遍。

**head 0 的斜率最大吗？**
是的，斜率大的头只看近处，attention 更尖；斜率小的头看得更远。
