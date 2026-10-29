---
id: apple-batched-token-selection
section: decoding
order: 1
level: S
title: "Batch token selection：greedy、top-k/top-p 与 Gumbel-max"
quick: "输入 [B,V]，每行独立做 mask、temperature、top-k、top-p，再返回 [B] 的 token IDs。支持每条请求不同参数；随机测试检查频率与 seed replay。"
companies:
  - apple
tags:
  - Apple
  - Decoding
  - Batch Inference
  - Batch Decoding 2026-10-28
  - 完整编程练习
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "PyTorch multinomial: independent distributions in matrix rows"
    url: "https://docs.pytorch.org/docs/2.14/generated/torch.multinomial.html"
    type: primary
  - title: "PyTorch stable sort"
    url: "https://docs.pytorch.org/docs/2.14/generated/torch.sort.html"
    type: primary
---

## 题目描述

来源：本手册原创编程练习。一个 batch 中有 B 条正在生成的请求，每条都有自己对下一 token 的预测。实现一次批量选择：greedy、temperature + top-k/top-p sampling，以及 Gumbel-max sampling。不能把整个矩阵 flatten 后只挑一个 token。

### 输入与接口

实现 `select_token(logits, temperature=1.0, top_k=None, top_p=1.0, allowed=None, method="multinomial", generator=None)`。

- `logits` 是 floating tensor `[B,V]`，B 可以为 0，V>0；每行对应一个独立请求，同一设备。值可为 `-inf`，不可为 NaN 或 `+inf`。
- `temperature`、`top_p` 是 scalar 或 `[B]`；temperature 有限且非负，top-p 在 `[0,1]`。`top_k` 为 None、正整数 scalar 或只含正整数的 `[B]`，大于 V 时当作 V。
- `allowed` 为 None 或同设备 bool `[B,V]`，True 表示可以生成。每个实际参与选择的 row 至少有一个允许且 finite 的 logit，否则报 `ValueError`。
- `method` 是 `greedy`、`multinomial` 或 `gumbel`。`generator` 是可选的 PyTorch RNG，设备应与 logits 一致。本练习以 CPU 验证；没有做 GPU/MPS 兼容性或 throughput 承诺。

### 输出与规则

返回同设备 long `[B]`，每行一个原 vocabulary token ID。不修改 logits 或 mask。

先做 allowed mask。Greedy 或该行 temperature=0、top-p=0 时，直接取合法最大 logit，同分取最小 ID；这些行不消耗 RNG。其他行依次做 temperature、top-k、重新 normalization、top-p、再次 normalization，最后使用 multinomial 或 Gumbel-max。Top-p 保留累计概率首次达到阈值的 token；p=1 保留所有 top-k survivors。同分始终按 token ID 升序。

### 输入输出示例

```text
logits=[[3,3,0],[4,1,2],[1,2,3]]
allowed=[[False,True,True],[True,True,True],[True,True,True]]
method="greedy" -> [1,0,2]

概率=[0.4,0.35,0.25]，p=0.5 -> 保留 IDs [0,1]，最终概率 [0.4/0.75,0.35/0.75,0]。
若先设 k=2，再设 p=0.5 -> top-k 后 [0.5333,0.4667]，只保留 ID 0，输出 0。
```

## 解题思路与参考答案

假设第一条请求禁止 token 0，第二条请求只想取最大值，第三条请求需要随机回答。它们可以共享一张 `[B,V]` 矩阵，但 mask、排序、累计概率和最终选择都必须沿每行的 V 维进行。

先把不合法位置设成 `-inf`，并检查每行是否仍有候选。确定性行先得到答案；随机行再独立处理。Stable sort 让同分规则可测试，原始 ID 则通过 gather 还原。Top-p 判断“加入当前 token 之前累计了多少”，这样不会误删跨越阈值的那个 token。

### 完整参考实现

`float64` 用来使教学例子的累计概率更易检查，会产生额外 memory 和计算成本；这是正确性参考实现，不是 fused serving kernel。Gumbel 只加在已经完成 temperature 与截断的分数上，不会再除一次温度。

```python
import math
import torch


def row_parameter(value, batch, device, dtype, name):
    result = torch.as_tensor(value, device=device, dtype=dtype)
    if result.ndim == 0:
        result = result.expand(batch)
    if result.shape != (batch,):
        raise ValueError(f"{name} must be scalar or [B]")
    return result


@torch.no_grad()
def select_token(
    logits,
    temperature=1.0,
    top_k=None,
    top_p=1.0,
    allowed=None,
    method="multinomial",
    generator=None,
):
    """[B,V] -> [B]; True means allowed. All filtering is per row."""
    if logits.ndim != 2 or logits.shape[1] == 0:
        raise ValueError("logits must have shape [B,V], V > 0")
    batch, vocab = logits.shape
    if method not in ("greedy", "multinomial", "gumbel"):
        raise ValueError("unknown selection method")
    scores = logits.to(torch.float64).clone()
    if torch.isnan(scores).any() or torch.isposinf(scores).any():
        raise ValueError("NaN and +inf logits are unsupported")
    if allowed is not None:
        if allowed.shape != scores.shape or allowed.dtype != torch.bool:
            raise ValueError("allowed must be bool [B,V]")
        scores.masked_fill_(~allowed, -torch.inf)
    if not torch.isfinite(scores).any(dim=-1).all():
        raise ValueError("every active row needs a finite allowed logit")
    temp = row_parameter(temperature, batch, scores.device, scores.dtype, "temperature")
    nucleus = row_parameter(top_p, batch, scores.device, scores.dtype, "top_p")
    if not torch.isfinite(temp).all() or (temp < 0).any():
        raise ValueError("temperature must be finite and >= 0")
    if not torch.isfinite(nucleus).all() or ((nucleus < 0) | (nucleus > 1)).any():
        raise ValueError("top_p must be finite and in [0,1]")
    if top_k is None:
        counts = torch.full((batch,), vocab, dtype=torch.long, device=scores.device)
    else:
        raw = row_parameter(top_k, batch, scores.device, scores.dtype, "top_k")
        if (
            not torch.isfinite(raw).all()
            or (raw < 1).any()
            or (raw != raw.floor()).any()
        ):
            raise ValueError("top_k must contain positive integers")
        counts = raw.clamp(max=vocab).long()
    result = scores.argmax(dim=-1)  # Ties: first (smallest) token ID.
    stochastic = (temp > 0) & (nucleus > 0)
    if method == "greedy" or not stochastic.any():
        return result
    # Only stochastic rows consume RNG; deterministic rows do not.
    rows = stochastic.nonzero(as_tuple=True)[0]
    work = scores[rows]
    work = (work - work.max(dim=-1, keepdim=True).values) / temp[rows, None]
    ordered, ids = torch.sort(work, dim=-1, descending=True, stable=True)
    rank = torch.arange(vocab, device=scores.device)[None, :]
    ordered.masked_fill_(rank >= counts[rows, None], -torch.inf)
    probs = ordered.softmax(dim=-1)  # Normalize AFTER top-k.
    cumulative = probs.cumsum(dim=-1)
    # Keep the crossing token too. p=1 explicitly keeps every top-k survivor.
    before = torch.cat(
        [torch.zeros_like(cumulative[:, :1]), cumulative[:, :-1]], dim=-1
    )
    keep = (before < nucleus[rows, None]) | (nucleus[rows, None] == 1)
    ordered.masked_fill_(~keep, -torch.inf)
    if method == "multinomial":
        picked = torch.multinomial(ordered.softmax(dim=-1), 1, generator=generator)
    else:
        u = torch.rand(
            ordered.shape,
            dtype=ordered.dtype,
            device=ordered.device,
            generator=generator,
        )
        eps = torch.finfo(u.dtype).eps
        noise = -torch.log(-torch.log(u.clamp(min=eps, max=1 - eps)))
        picked = (ordered + noise).argmax(dim=-1, keepdim=True)
    result[rows] = ids.gather(-1, picked).squeeze(-1)
    return result
```
## 简单测试怎么写

将上面实现与下面测试按顺序保存为 `solution.py`，在安装 PyTorch 的环境运行 `python solution.py`。先核对三行 greedy 结果，再检查 top-p 跨阈值、top-k 后 normalization、mask、seed replay。随机部分使用重复样本检验频率，不能用一次输出证明分布正确。

```python
# Run implementation + these tests in the same file.
torch.set_num_threads(1)
scores = torch.tensor([[3.0, 3.0, 0.0], [4.0, 1.0, 2.0], [1.0, 2.0, 3.0]])
allowed = torch.tensor([[False, True, True], [True, True, True], [True, True, True]])
original = scores.clone()
assert select_token(scores, method="greedy", allowed=allowed).tolist() == [1, 0, 2]
assert torch.equal(scores, original)
# Per-row deterministic branches and top-k.
out = select_token(scores, temperature=[0, 1, 1], top_p=[1, 0, 1], top_k=1)
assert out.tolist() == [0, 0, 2]
assert select_token(torch.zeros(2, 4), top_k=1).tolist() == [0, 0]
for method in ("multinomial", "gumbel"):
    g1, g2 = torch.Generator().manual_seed(9), torch.Generator().manual_seed(9)
    a = select_token(scores, method=method, generator=g1)
    b = select_token(scores, method=method, generator=g2)
    assert torch.equal(a, b)
    # Different row distributions: [0.8,0.2,0] and [0,0.25,0.75].
    distribution = torch.tensor(
        [[0.8, 0.2, 0.0], [0.0, 0.25, 0.75]], dtype=torch.float64
    )
    logits = distribution.log().repeat_interleave(10000, dim=0)
    sampled = select_token(
        logits, method=method, generator=torch.Generator().manual_seed(41)
    )
    freq = torch.stack([(sampled[:10000] == i).double().mean() for i in range(3)])
    other = torch.stack([(sampled[10000:] == i).double().mean() for i in range(3)])
    assert torch.allclose(freq, distribution[0], atol=0.025, rtol=0)
    assert torch.allclose(other, distribution[1], atol=0.025, rtol=0)
# p=.5 crosses at token 1: keep IDs 0 and 1 (not just 0).
logits = torch.tensor([[0.4, 0.35, 0.25]], dtype=torch.float64).log().expand(4000, -1)
chosen = select_token(logits, top_p=0.5, generator=torch.Generator().manual_seed(12))
assert set(chosen.tolist()) == {0, 1}
assert abs((chosen == 0).double().mean().item() - 0.4 / 0.75) < 0.035
# top-k FIRST: [.4,.35] normalizes to [.533,.467], so p=.5 keeps only 0.
assert select_token(logits[:4], top_k=2, top_p=0.5).tolist() == [0, 0, 0, 0]
# p=1 must keep all tied top-k survivors.
assert set(
    select_token(
        torch.zeros(3000, 3), top_p=1, generator=torch.Generator().manual_seed(3)
    ).tolist()
) == {0, 1, 2}
assert select_token(torch.empty(0, 3)).shape == (0,)
assert select_token(torch.tensor([[1.0, 0.0]]), temperature=1e-12).item() == 0
try:
    select_token(scores, allowed=torch.zeros_like(allowed))
except ValueError:
    pass
else:
    raise AssertionError("all-masked active rows must fail")
print("Batched token selection: tests passed")
```
## 复杂度与追问

完整排序的时间为 `O(B V log V)`，工作空间为 `O(BV)`。代码未按行调用 Python sampling；检查非法输入和是否全部结束会触发设备同步，不能据此声称 GPU 性能最优。

**同一个 seed 是否让 batch 与逐条 sampling 完全相同？** 不保证。Batch 顺序、active rows 与抽样次数改变时，共享 RNG 的消耗顺序也会改变。本题只承诺相同设备、输入、batch 顺序和调用路径下的 seed replay；独立请求需要独立 RNG stream 或 counter-based 设计。

下一步做 [[apple-batched-generation]]，把一次选择接入完整生成循环。原来的 [[coding-topk-nucleus]] 保留 `[V]` 入门接口。
