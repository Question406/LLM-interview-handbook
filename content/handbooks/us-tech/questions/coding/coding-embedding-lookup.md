---
id: coding-embedding-lookup
section: coding
order: 14
level: S
title: 白板：embedding lookup + padding mask，大 vocabulary 显存
quick: >-
  用 `E[ids]` 把 $[B,T]$ 的 id 查成 $[B,T,D]$，另把 pad 位置转成 attention
  mask。`padding_idx` 只控制 pad 行的向量和梯度，不能让 softmax 自动忽略它；整张 vocabulary 按 $V\cdot
  D$ 占显存。
tags:
  - 完整编程练习
  - Coding
  - Embedding
  - Memory
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: torch.nn.Embedding
    url: 'https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html'
    type: primary
  - title: scaled_dot_product_attention
    url: >-
      https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题目描述

实现 token embedding 查询及 padding mask，并提供一个最小 PyTorch 模块，使 padding 对应的 embedding 不参与梯度更新。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `embed_forward(embed, ids, pad_id=0) -> (x, pad)`：用 `ids: [B, T]` 查表得到 `x: [B, T, D]`，同时返回 `pad: [B, T]`，pad 位置为 True。
- `attn_pad_mask(pad) -> [B, 1, 1, S]`：把 pad 标记变成能广播到 scores `[B, H, T, S]` 的 key mask。True 表示屏蔽这个 key，和 keep-mask 的约定相反。
- `SmallLM(vocab, dim, pad=0)`：用 `nn.Embedding(..., padding_idx=pad)` 建表，`forward(ids)` 返回 `(x, pad)`。`padding_idx` 那一行梯度恒为 0。
- 约束：`ids` 都是合法的 vocabulary 下标，`pad_id` 在 vocabulary 范围内。

### 输入输出示例

```text
embedding 表 = [[0, 0], [1, 2], [3, 4]], pad_id = 0
ids = [[1, 0]]
embed_forward(embed, ids, 0)
-> x = [[[1, 2], [0, 0]]], pad = [[False, True]]
attn_pad_mask(pad) -> [[[[False, True]]]]
```

## 解题思路与参考答案

embedding 先按 id 查表，再用单独的 attention mask 屏蔽 pad key。`padding_idx` 让 pad 那一行固定为 0 向量、梯度为 0；key mask 让 attention 不去看 pad 位置。只有前者不够：零向量 key 和 $q$ 的点积是 0，softmax 之后仍有正的权重，必须在 scores 上把 pad key 填成 $-\infty$。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `embed_forward(embed, ids, pad_id=0) -> (x, pad)`：用 `ids: [B, T]` 查表得到 `x: [B, T, D]`，同时返回 `pad: [B, T]`，pad 位置为 True。
- `attn_pad_mask(pad) -> [B, 1, 1, S]`：把 pad 标记变成能广播到 scores `[B, H, T, S]` 的 key mask。True 表示屏蔽这个 key，和 keep-mask 的约定相反。
- `SmallLM(vocab, dim, pad=0)`：用 `nn.Embedding(..., padding_idx=pad)` 建表，`forward(ids)` 返回 `(x, pad)`。`padding_idx` 那一行梯度恒为 0。
- 约束：`ids` 都是合法的 vocabulary 下标，`pad_id` 在 vocabulary 范围内。

### 输入输出示例

```text
SmallLM(vocab=5, dim=3, pad=0), ids = [[1, 0], [2, 0]]
x.shape            -> (2, 2, 3)，x[:, 1] 全为 0
attn_pad_mask(pad) -> 形状 (2, 1, 1, 2)，第 2 个 key 为 True
```

### 解题思路与正确性

key mask 只屏蔽 pad 当 key 的情况，pad 位置作为 query 算出的输出它不会替你处理；后续层和损失里的 `ignore_index` 要另外管。

### 完整参考实现（Python 3）

```python
import torch
from torch import nn


def embed_forward(embed, ids, pad_id=0):
    """查表并标出 pad 位置。

    ids: [B, T] 合法 vocabulary 下标 -> (x: [B, T, D], pad: [B, T] bool，True 表示 pad)。
    """
    x = embed(ids)
    pad = ids.eq(pad_id)
    return x, pad


def attn_pad_mask(pad):
    """把 pad: [B, S] 变成可广播到 scores [B, H, T, S] 的 key mask [B, 1, 1, S]。

    True 表示屏蔽这个 key（和 keep-mask 的约定相反），用法：scores.masked_fill(mask, -inf)。
    """
    return pad[:, None, None, :]


class SmallLM(nn.Module):
    """只有 embedding 的最小模型：padding_idx 那一行保持 0，梯度也为 0。"""

    def __init__(self, vocab, dim, pad=0):
        super().__init__()
        self.pad = pad
        self.embed = nn.Embedding(vocab, dim, padding_idx=pad)

    def forward(self, ids):
        x, pad = embed_forward(self.embed, ids, self.pad)
        # 后续 attention 里：scores = scores.masked_fill(attn_pad_mask(pad), float("-inf"))
        return x, pad
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert x.shape == (2, 2, 3)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
torch.set_num_threads(1)
model = SmallLM(5, 3, pad=0)
ids = torch.tensor([[1, 0], [2, 0]])

# 输出形状 [B, T, D]，pad 位置的向量是 0
x, pad = model(ids)
assert x.shape == (2, 2, 3)
assert torch.all(x[:, 1] == 0)
assert pad.tolist() == [[False, True], [False, True]]

# key mask 能广播到 [B, H, T, S]
mask = attn_pad_mask(pad)
assert mask.shape == (2, 1, 1, 2)

# 零向量 key 不加 mask 仍会分到正的 attention 权重；加 mask 后为 0
scores = torch.zeros(2, 1, 2, 2)
assert torch.all(scores.softmax(-1)[..., 1] > 0)
masked = scores.masked_fill(mask, float("-inf")).softmax(-1)
assert torch.all(masked[..., 1] == 0)

# padding_idx 那一行梯度为 0；其他被查到一次的行梯度为 1
x.sum().backward()
assert torch.all(model.embed.weight.grad[0] == 0)
assert torch.all(model.embed.weight.grad[1] == 1)

# 没被查到的行梯度为 0（反向只累加出现过的行）
assert torch.all(model.embed.weight.grad[3:] == 0)
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$、vocabulary 大小 $V$、维度 $D$。查表是 $O(BTD)$，vocabulary 参数是 $O(VD)$。本 batch 只查了少量 token，也不能忽略整张表的显存：参数、梯度缓冲和优化器状态都按 $V\times D$ 分配。

- 追问「反向的代价」：梯度只累加到出现过的行，计算量是 $O(BTD)$；但 dense 梯度张量本身仍是 $V\times D$，除非用 `sparse=True`。

## 题怎么来的

这题看起来像 API 题，常见的坑有两个：把 pad 和 mask 当成一件事，以及把大 vocabulary 的 embedding 矩阵当成一张「小表」。NVIDIA 会问显存，Apple 会问端侧 vocabulary，OpenAI 的 debug 题常常漏掉 padding mask，让 pad 位置进了 softmax。权重共享见 `coding-weight-tying`。

## Lookup：按行 gather，不是 matmul

设 $E\in\mathbb{R}^{V\times D}$，`ids` 形状为 `[B, T]`，输出是

$$
x_{b,t}=E_{\mathrm{ids}[b,t]}\in\mathbb{R}^{D},\qquad x\ \mathrm{shape}\ [B,T,D].
$$

实现上是按下标取行，不是拿 one-hot 矩阵 $U$ 去乘 $E$。设 `padding_idx=p` 时，第 $p$ 行初始化为 0，每次 backward 都把这一行的梯度清零，所以它学不到东西。这只保证 pad token 的向量固定为 0，并不保证 attention 忽略它（原因见上面的解题思路），pad key 必须在 scores 上打成 $-\infty$，见 `apple-mha-code`、`coding-softmax-stable`。

损失里的 `ignore_index=pad` 和 attention mask 也各管一件事：前者不训练 pad 位置的预测目标，后者不让模型关注 pad key。两个都要有。

## 大 vocabulary 显存

$$
\mathrm{bytes}(E)=V\cdot D\cdot b,\quad b=2\ \mathrm{(bf16/fp16)},\ 4\ \mathrm{(fp32)}.
$$

Llama 3 的 vocabulary $V\approx 128256$，$D=4096$，bf16 一份约 1.05 GB。训练时 AdamW 的 $m$、$v$ 用 fp32 存，每个参数再多 8 字节，是 bf16 参数本身的 4 倍，约 4.2 GB。权重共享（tying）把 lm_head 那份矩阵省掉，优化器状态也只留一套。vocabulary 并行按 $V$ 切开，lookup 前要对 id 做 all-to-all，那属于系统设计题；白板上先报出 1 GB 这个量级。

Apple 端侧的问题是：vocabulary 大，ANE 上的 gather 访存不连续，所以常把 embedding 压成 int8，或者缩小 $V$。不要假设「embedding 和 70B 参数比起来可以忽略」：逐 token 生成（decode）时，embedding 和 lm_head 仍是 $V$ 维的 gather 和大 GEMM。扩 vocabulary 时要同时改 tokenizer 的 id 和 $E$ 的行数，并说明新行怎么初始化（用均值、用零，或复制相近 token 的向量）。

## 追问

**零向量为什么还要 mask？**
softmax($[\ldots,0]$) 仍会给 pad 正的 attention 权重，必须填 $-\infty$。
**`padding_idx` 的梯度是什么？**
PyTorch 每步把这一行的 grad 置 0，行向量一直保持 0。不要指望它学出「pad 的语义」。
**和 one-hot matmul 有什么区别？**
结果等价，但浪费计算。Lookup 是稀疏 gather，反向只对出现过的行累加梯度。
