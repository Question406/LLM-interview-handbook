---
id: coding-cross-entropy
section: coding
order: 2
level: S
title: 白板：从 logits 写 cross entropy，不要先 softmax 再 log
quick: >-
  直接在 log 域算 $\ell=-z_y+\mathrm{logsumexp}(z)$，先减行最大值，避免概率下溢后再取 log。先筛掉 ignore
  下标，再按有效 token 数平均；causal LM 只 shift 一次。
tags:
  - 完整编程练习
  - Coding
  - Cross Entropy
  - OpenAI
  - Numerical Stability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: torch.nn.functional.cross_entropy
    url: >-
      https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
    type: primary
  - title: torch.nn.functional.log_softmax
    url: >-
      https://pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html
    type: primary
---

## 题目描述

实现基于 logits 的 cross entropy，以及采用 next-token 对齐方式的语言模型 cross entropy，正确处理被忽略的位置。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `cross_entropy_logits(logits, target, ignore_index=-100) -> Tensor`：`logits` 形状 `[N, V]`，`target` 形状 `[N]`。返回未被忽略的样本上的平均 cross entropy。
- `lm_ce(logits, labels, ignore_index=-100) -> Tensor`：causal LM 版本，`logits` 形状 `[B, L, V]`，`labels` 形状 `[B, L]`；用位置 t 的 logits 预测位置 t+1 的 label，只 shift 一次。
- `ignore_index` 可以是任意整数，包括大于 V 的值，也必须被安全忽略；未被忽略的标签保证满足 `0 <= y < V`。
- 全部标签都被忽略，或者 LM 的序列长度 `L <= 1` 时，返回一个能 backpropagation、梯度为 0 的标量 0。

### 输入输出示例

```text
cross_entropy_logits([[0, 0], [0, 0]], target=[1, 99], ignore_index=99) -> ln 2 ≈ 0.693   # 第二行被忽略
cross_entropy_logits(logits, target=[99, 99], ignore_index=99)           -> 0，backward 后梯度全为 0
```

## 解题思路与参考答案

我会直接从 logits 算 log-softmax，再取目标类别的负 logprob。每行先减去最大值，再算 $\log\sum\exp$，全程不物化概率，就能避免概率下溢后出现 $\log 0$。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `cross_entropy_logits(logits, target, ignore_index=-100) -> Tensor`：`logits` 形状 `[N, V]`，`target` 形状 `[N]`。返回未被忽略的样本上的平均 cross entropy。
- `lm_ce(logits, labels, ignore_index=-100) -> Tensor`：causal LM 版本，`logits` 形状 `[B, L, V]`，`labels` 形状 `[B, L]`；用位置 t 的 logits 预测位置 t+1 的 label，只 shift 一次。
- `ignore_index` 可以是任意整数，包括大于 V 的值，也必须被安全忽略；只对没被忽略的标签检查 `0 <= y < V`，越界时抛 `ValueError`。
- 全部标签都被忽略，或者 LM 的序列长度 `L <= 1` 时，返回一个能 backpropagation、梯度为 0 的标量 0。

### 输入输出示例

```text
cross_entropy_logits([[0, 0], [0, 0]], target=[1, 99], ignore_index=99) -> ln 2 ≈ 0.693   # 第二行被忽略
cross_entropy_logits(logits, target=[99, 99], ignore_index=99)           -> 0，backward 后梯度全为 0
```

### 解题思路与正确性

被忽略的行要在 `gather` 之前筛掉。如果 `ignore_index` 是 99 而 V 只有 5，先 `gather` 再乘 mask 会直接索引越界。筛选后剩下的标签再做范围检查，平均也只在这些行上做。

全部被忽略时返回 `logits.sum() * 0.0`，而不是新建的 `torch.tensor(0.0)`：前者仍连着计算图，`backward()` 能正常跑，梯度全为 0。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def cross_entropy_logits(logits, target, ignore_index=-100):
    """logits [N, V]，target [N] -> 未忽略样本上的平均 cross entropy（标量）。"""
    if logits.ndim != 2 or logits.shape[1] < 1 or target.shape != logits.shape[:1]:
        raise ValueError(
            f"expected logits [N, V] and target [N], got {tuple(logits.shape)} and {tuple(target.shape)}"
        )
    keep = target != ignore_index
    if not bool(keep.any()):
        return logits.sum() * 0.0  # 保留计算图，梯度为 0

    chosen = target[keep]
    num_classes = logits.shape[1]
    if bool(((chosen < 0) | (chosen >= num_classes)).any()):
        raise ValueError(f"target outside [0, {num_classes})")

    z = logits[keep].float()  # 低精度输入升到 fp32
    shifted = z - z.max(dim=-1, keepdim=True).values
    log_probs = shifted - shifted.exp().sum(dim=-1, keepdim=True).log()
    return -log_probs.gather(1, chosen[:, None]).mean()


def lm_ce(logits, labels, ignore_index=-100):
    """causal LM 损失：logits [B, L, V]，labels [B, L]；位置 t 预测 t+1，只 shift 一次。"""
    vocab = logits.size(-1)
    return cross_entropy_logits(
        logits[:, :-1].reshape(-1, vocab),
        labels[:, 1:].reshape(-1),
        ignore_index,
    )
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.isclose(cross_entropy_logits(uniform, torch.tensor([1, 99]), 99), torch.log(torch.tensor(2.0)))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(0)

# 两类均匀 logits：损失是 ln 2
uniform = torch.zeros(2, 2)
assert torch.isclose(
    cross_entropy_logits(uniform, torch.tensor([1, 99]), 99),
    torch.log(torch.tensor(2.0)),
)

# 与 PyTorch 一致；ignore_index 大于 V 也安全，被忽略的行梯度为 0
logits = torch.randn(4, 5, requires_grad=True)
target = torch.tensor([1, 99, 2, 99])
loss = cross_entropy_logits(logits, target, 99)
assert torch.allclose(loss, F.cross_entropy(logits, target, ignore_index=99))
loss.backward()
assert torch.all(logits.grad[[1, 3]] == 0)

# 全部忽略：返回 0，可以 backpropagation，梯度全为 0
logits = torch.randn(2, 3, requires_grad=True)
loss = cross_entropy_logits(logits, torch.tensor([99, 99]), 99)
loss.backward()
assert loss.item() == 0
assert torch.all(logits.grad == 0)

# 极端 logits 不会溢出成 inf / NaN
extreme = torch.tensor([[1000.0, -1000.0]])
assert torch.isclose(
    cross_entropy_logits(extreme, torch.tensor([0])), torch.tensor(0.0)
)
assert torch.isclose(
    cross_entropy_logits(extreme, torch.tensor([1])), torch.tensor(2000.0)
)

# causal LM：只 shift 一次
logits = torch.randn(2, 4, 5)
ids = torch.randint(0, 5, (2, 4))
expected = F.cross_entropy(logits[:, :-1].reshape(-1, 5), ids[:, 1:].reshape(-1))
assert torch.allclose(lm_ce(logits, ids), expected)

# 序列长度 1：没有可预测的位置，返回 0
assert lm_ce(torch.randn(2, 1, 5), torch.zeros(2, 1, dtype=torch.long)).item() == 0

# 未忽略的标签越界、形状不符
expect_value_error(cross_entropy_logits, torch.randn(2, 3), torch.tensor([0, 3]))
expect_value_error(cross_entropy_logits, torch.randn(2, 3), torch.tensor([0]))
```

### 复杂度与追问

设样本数为 N、类别数为 V。时间和临时空间都是 O(NV)。

- 追问「全部忽略时 PyTorch 返回什么」：`F.cross_entropy` 在 mean reduction 下对空输入返回 NaN（0/0）。这里返回 0 是练习显式约定的，不要声称和所有库一致。
- 追问「vocabulary 很大时显存怎么办」：O(NV) 的中间张量来自 `shifted` 和 `exp`。可以按行或按 vocabulary 分块算 logsumexp，见 `coding-fused-ce`。

## 题怎么来的

这是研究岗和 MLE 白板上默认的损失。OpenAI 给带 bug 的训练 loop 时，常见的植入就是 `F.softmax` 之后再 `log` 再 NLL，fp16 下一训练就 NaN。Apple 电面手写完 attention 之后，也会跟一句「训练时 logits 怎么接 CE」。PyTorch 的 `cross_entropy` 内部是 log-softmax + NLL，白板对齐这个契约就行，不要自己造一条会下溢的路径。稳定 softmax 见 `coding-softmax-stable`。

## 公式：NLL 在 log 域一次做完

对一条样本的 logits $z$ 和类别 $y$：

$$
\ell=-z_y+\mathrm{logsumexp}(z),\qquad
\mathrm{logsumexp}(z)=m+\log\sum_j e^{z_j-m},
$$

其中 $m=\max_j z_j$。结果等于 $-\log\mathrm{softmax}(z)_y$，但始终不算出 $p_y$ 本身。$p_y$ 一旦下溢成 0，$\log 0=-\infty$，梯度也没了。

做 label smoothing 时目标不再是 one-hot，要对整个目标分布 $q$ 算 $-q\cdot\log\pi$，不能只 gather 一列。

均匀初始化时 $\ell\approx\log V$，十万 vocabulary 大约是 $11.5$。可以用这个数判断第一步的 loss 对不对。

不要对 pad 位置算出损失再乘 0，却仍然除以 $N$。平均只能在有效位置上做。

## 序列：shift、ignore 和分母

Causal LM 用 `logits[:, :-1]` 对 `labels[:, 1:]`。HuggingFace 传入 `labels=` 时内部会自己 shift，手写时只能 shift 一次。面试官想听你说出分母是有效 token 数，而不是 batch 里的所有格子；否则 pad 多的 batch，loss 会被人为拉低。

fp16 下即使减了 max，极端值仍可能溢出，这一步升到 fp32 的成本可以忽略。OpenAI 的 debug 题思路是：先固定 greedy 和 `eval()`，再看 cross entropy loss（CE）是不是 NaN，不要同时开着 dropout 和 sampling，见 `openai-transformer-debug`。

## 追问

**为什么禁止先 softmax 再 log？**
正确类的 logit 很小或 vocabulary 很大时，$e^{z_y}/\sum e^{z}$ 会下溢成 0，取 log 就是 $-\infty$。log-sum-exp 的写法全程都是有限值。
**`F.nll_loss(F.log_softmax(z), y)` 可以吗？**
可以，这就是 `cross_entropy` 的做法。错的是 `nll_loss(softmax(z).log(), y)`。
**label smoothing 怎么算？**
$q=(1-\varepsilon)e_y+\varepsilon/V$，loss 是对 $q$ 的 CE。PyTorch 的 `label_smoothing` 参数就是这么算的，不是只改 $y$ 那一列。
**和 KL 是什么关系？**
$\mathrm{CE}(q,\pi)=H(q)+\mathrm{KL}(q\|\pi)$。$q$ 是 one-hot 时 $H(q)=0$，CE 就等于 NLL，也等于 KL。不要把分布自身的熵和 CE 混成一个数，见 `openai-entropy-l1`。

## 相关题

- [[coding-logsumexp]]：同一个恒等式 $\ell=\mathrm{logsumexp}(z)-z_y$ 从 log-sum-exp 这一侧讲，重点是减 max 和整行 $-\infty$ 的 edge case。
- [[p3a-openai-masked-cross-entropy-loss]]：OpenAI 的 NumPy 版本，要手写梯度、label smoothing 和全被 mask 时返回 0，契约比这里多。
- [[coding-fused-ce]]：把这里的 CE 和 lm_head 融合，沿 vocabulary 分块，不物化 `[N, V]` logits。
- [[coding-z-loss]]：在这个 CE 上再加 $(\log Z)^2$，讲 CE 对 logits 平移不变带来的漂移问题。
- [[openai-entropy-l1]]：算的是分布自身的熵而不是 CE，还要把 L1 的梯度传回 logits，容易和这题混。
