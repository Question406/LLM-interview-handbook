---
id: coding-weight-tying
section: coding
order: 11
level: A
title: 白板：embedding 与 lm_head 权重共享，梯度怎么流
quick: "直接让 `lm_head.weight` 引用 `embed.weight` 这个 $[V, D]$ Parameter，输入查表用 $E$，输出算 $hE^\\top$。Autograd 会把两条路径的梯度加到同一份 $E$，optimizer 只维护一份状态，因此省下 $VD$ 个参数；复制数值达不到共享的效果。"
tags:
  - 完整编程练习
  - Coding
  - Weight Tying
  - Embedding
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Using the Output Embedding to Improve Language Models (Press & Wolf)
    url: https://arxiv.org/abs/1608.05859
    type: primary
  - title: torch.nn.Embedding
    url: https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html
    type: primary
---

## 题目描述

实现一个 embedding 与输出投影共享权重的最小语言模型。既要支持返回各位置的词表 logits，也要支持给定目标 token 时计算忽略 padding 的 next-token 交叉熵。共享必须是同一个参数对象，而非仅初始化成相同数值。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `TiedLM(vocab, dim, pad=0)`：一个最小语言模型，`nn.Embedding` 和无 bias 的 `lm_head` 共享同一个 `[V, D]` 的 Parameter，中间只有一层 LayerNorm。
- `forward(ids, targets=None)`：`ids` 是 `[B, T]`。不给 `targets` 时返回 logits `[B, T, V]`；给 `targets` 时在内部做一次 shift（位置 `t` 的 logits 预测 `targets[:, t + 1]`），返回忽略 pad 的平均交叉熵。
- 约束：B ≥ 1，给 `targets` 时它和 `ids` 形状相同、T ≥ 2，且 shift 之后至少有一个非 pad 目标。

- logits 定义为 `LayerNorm(embed(ids)) @ embed.weight.T`；LayerNorm 使用默认 `eps=1e-5`，初始缩放为 1、偏移为 0。输入 token 均在 `[0,V)` 内。
### 示例

```text
model = TiedLM(7, 4, pad=0)
model.embed.weight is model.lm_head.weight          -> True
model.embed.weight[1] 改成全 3                       -> model.lm_head.weight[1] 也是全 3
将 model.embed.weight 全设为 0（LayerNorm 初始 gamma=1、beta=0）
model(ids=[[1, 2, 3]], targets=[[1, 2, 3]]) -> log(7) ≈ 1.945910
model(ids=[[1, 2, 3]]) -> 形状 [1,3,7] 的全 0 logits
```

## 解题思路与参考答案

我会把 lm_head.weight 直接绑定到 embedding 的 Parameter，再验证两者是同一个对象。比如改 embedding 的一行，输出投影同一行也应立刻改变。反向时不需要手动合并梯度，autograd 会累加两条路径；padding_idx 只屏蔽查表路径，输出路径仍可能更新 pad 行。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，CPU 上验证；没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `TiedLM(vocab, dim, pad=0)`：一个最小语言模型，`nn.Embedding` 和无 bias 的 `lm_head` 共享同一个 `[V, D]` 的 Parameter，中间只有一层 LayerNorm。
- `forward(ids, targets=None)`：`ids` 是 `[B, T]`。不给 `targets` 时返回 logits `[B, T, V]`；给 `targets` 时在内部做一次 shift（位置 `t` 的 logits 预测 `targets[:, t + 1]`），返回忽略 pad 的平均交叉熵。
- 约束：B ≥ 1，给 `targets` 时它和 `ids` 形状相同、T ≥ 2，且 shift 之后至少有一个非 pad 目标，否则抛 `ValueError`。

### 输入输出示例

```text
model = TiedLM(7, 4, pad=0)
model.embed.weight is model.lm_head.weight          -> True
model.embed.weight[1] 改成全 3                       -> model.lm_head.weight[1] 也是全 3
model(ids=[[1, 2, 3], [2, 4, 0]], targets=同上)      -> 有限的标量 loss，最后一个目标 0 被忽略
```

### 解题思路与正确性

绑定时直接把 `lm_head.weight` 赋值为 `embed.weight` 这个 Parameter 对象，而不是复制数值。这样两个模块引用同一块存储，`parameters()` 里只出现一次，optimizer 也只为它维护一份状态。

反向时，autograd 把两条路径的梯度累加到同一个 `.grad` 上：查表路径给出现过的 token 行加梯度，输出投影路径给所有行加梯度。测试里用两份数值相同但独立的参数做对照，验证共享梯度正好等于两条路径梯度之和。

`padding_idx` 只挡住查表那一路的梯度。输出投影那一路照样会给 pad 行梯度（softmax 会把概率分给 pad 这个类别），所以共享参数的 pad 行并不保证一直是 0。交叉熵用 `ignore_index=self.pad` 跳过 pad 目标，pad 不必是 0。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F
from torch import nn


class TiedLM(nn.Module):
    """embedding 和无 bias 的 lm_head 共享同一个 [V, D] Parameter 的最小语言模型。"""

    def __init__(self, vocab, dim, pad=0):
        super().__init__()
        self.pad = pad
        self.embed = nn.Embedding(vocab, dim, padding_idx=pad)
        self.ln = nn.LayerNorm(dim)
        self.lm_head = nn.Linear(dim, vocab, bias=False)
        self.lm_head.weight = self.embed.weight  # 共享同一个 Parameter，不是复制数值

    def forward(self, ids, targets=None):
        """ids: [B, T]。不给 targets 时返回 logits [B, T, V]；
        给 targets 时把位置 t 的 logits 和 targets[:, t + 1] 对齐，返回忽略 pad 的平均 CE。
        """
        hidden = self.ln(self.embed(ids))  # [B, T, D]
        logits = self.lm_head(hidden)      # [B, T, V]，即 hidden @ E^T
        if targets is None:
            return logits
        if targets.shape != ids.shape or ids.shape[1] < 2:
            raise ValueError("targets must match ids with T >= 2, got "
                             f"{tuple(targets.shape)} vs {tuple(ids.shape)}")
        shifted_targets = targets[:, 1:]
        if not (shifted_targets != self.pad).any():
            raise ValueError("no non-pad target after shifting")
        return F.cross_entropy(
            logits[:, :-1].reshape(-1, logits.size(-1)),
            shifted_targets.reshape(-1),
            ignore_index=self.pad,
        )
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert model.embed.weight is model.lm_head.weight` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("invalid input should raise ValueError")


torch.manual_seed(0)
torch.set_num_threads(1)
model = TiedLM(7, 4, pad=0)
ids = torch.tensor([[1, 2, 3], [2, 4, 0]])

# 两个模块拿的是同一个 Parameter，parameters() 里只出现一次
assert model.embed.weight is model.lm_head.weight
assert sum(p is model.embed.weight for p in model.parameters()) == 1

# 反向后两边看到的是同一份梯度
loss = model(ids, ids)
assert torch.isfinite(loss)
loss.backward()
assert model.embed.weight.grad is model.lm_head.weight.grad

# 共享梯度 = 查表路径梯度 + 输出投影路径梯度：用两份数值相同的独立参数对照
untied = TiedLM(7, 4, pad=0)
untied.load_state_dict(model.state_dict())
untied.lm_head.weight = nn.Parameter(model.embed.weight.detach().clone())
untied(ids, ids).backward()
path_sum = untied.embed.weight.grad + untied.lm_head.weight.grad
assert torch.allclose(model.embed.weight.grad, path_sum, atol=1e-6)

# padding_idx 只挡住查表那一路；输出那一路仍会给 pad 行梯度
assert torch.all(untied.embed.weight.grad[0] == 0)
assert untied.lm_head.weight.grad[0].abs().sum() > 0

# 改 embedding 的一行，lm_head 同一行跟着变：两者是同一块内存
with torch.no_grad():
    model.embed.weight[1].fill_(3)
assert torch.all(model.lm_head.weight[1] == 3)

# pad 不是 0 时也按 pad 忽略：只有 1 个有效目标，loss 等于这一项的 CE
model5 = TiedLM(7, 4, pad=5)
ids5 = torch.tensor([[1, 2, 5]])
logits = model5(ids5)
expected = F.cross_entropy(logits[0, :1], ids5[0, 1:2])
assert torch.allclose(model5(ids5, ids5), expected)

# 非法输入：T < 2；shift 之后全是 pad
expect_value_error(model, torch.tensor([[1]]), torch.tensor([[1]]))
expect_value_error(model, torch.tensor([[1, 0]]), torch.tensor([[1, 0]]))
```

### 复杂度与追问

设词表大小为 V、隐藏维度为 D。参数量从不绑定时的约 2·V·D 降到 V·D。logits 仍是 `[B, T, V]`，计算 O(B·T·V·D)，激活 O(B·T·V)，共享权重省不掉输出激活。

- 追问「pad 不是 0 时要注意什么」：`ignore_index` 必须跟着 `pad` 走。如果写死成 0，`pad=5` 时会把真实的 token 0 当成 pad 忽略，反而把 pad 算进 loss。测试里有 `pad=5` 的例子。

## 题怎么来的

Press & Wolf 和 Inan et al. 提出把输入 embedding 和输出投影绑成同一个矩阵。GPT-2 / GPT-3 风格的模型默认绑定；Llama 2/3 的公开实现不绑，`lm_head` 是一个独立的 $[V, D]$ 矩阵。OpenAI 和 Google 的白板喜欢问「省了什么、梯度会不会算两遍」。查表本身的显存见 `coding-embedding-lookup`。

## 同一份 $E$：lookup 进，inner product 出

`nn.Embedding(V, D).weight` 的形状是 $[V, D]$，`nn.Linear(D, V, bias=False).weight` 也是 $[V, D]$，因为 PyTorch 的 Linear 按 $[out, in]$ 存权重。绑定之后：

$$
x = E_{\mathrm{id}},\qquad \mathrm{logits} = h E^\top \in \mathbb{R}^{V}.
$$

不需要再额外存一份转置的参数。`self.lm_head.weight = self.embed.weight` 是引用，不是复制。optimizer 只看到一个参数，状态里不要再给 head 单独开一套 $m,v$。

判断是否真的绑上了，看两者的 `data_ptr` 是否相同。如果 `load_state_dict` 之后又执行了 `lm_head = Linear(...)` 重建，引用就断了，模型又变成两份权重。

## 梯度：两条路加到同一块

$E$ 在前向里被用了两次：第 $t$ 个 token 对应的那一行被取出来作为 hidden 的输入；同一个 $E$ 又和 $h$ 做点积得到 logits。反向时：

- 交叉熵损失（CE）经过 logits $= h E^\top$ 传到 $E$ 的梯度是 $\sum_t (\partial L/\partial \mathrm{logits}_t)^\top h_t$，每个 token 行都会收到；
- embedding 查表只给出现过的那些行累加 $\partial L/\partial x_t$。

autograd 会把两部分累加到同一块存储上。不要自己再乘 2，也不要 `detach` 掉其中一条路。`padding_idx` 只让查表这一路不更新 pad 行；输出投影那一路仍然会给 pad 行梯度，所以绑定后 pad 行一般会被更新（练习里的测试验证了这一点）。输出层如果有 bias $b\in\mathbb{R}^{V}$，它不需要绑定；GPT-2 的 lm_head 没有 bias。

显存上，不绑定要存两份 $V\times D$。以 $V=128256$、$D=4096$ 为例，bf16 下一份约 1 GB，绑定能省下一份。FSDP 或张量并行下，两处用到的必须是同一种切分方式，否则 all-gather 对不上。Llama 不绑定是出于质量和实现上的选择，并不是说 tying 有问题。

## 追问

**logits 为什么是 $h E^\top$ 而不是 $h E$？**
$E$ 的每一行是一个 token 的向量，$h$ 和某一行做点积才得到这个 token 的 logit。写成 $h E$ 形状对不上。
**AdamW 的 $m,v$ 怎么处理？**
一份权重对应一份状态。绑定了却给 head 再建一套状态，weight decay 和更新就会作用到一个并不存在的参数上。
**扩词表时要注意什么？**
embedding 和 head 一起扩，新 id 在两边的初始化是同一行。只扩 embedding 不扩 head，在 tying 下会直接出现 shape 冲突。
