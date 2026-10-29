---
id: afm-web-attention-code
section: tensor
order: 700
level: S
title: Self-Attention Coding：实现 batched causal attention，并处理全 padding 行
quick: >-
  计算 scaled dot-product scores，组合 causal 与 padding mask，在 softmax 前处理全不可见行，最后将无效
  query 输出置零。
companies:
  - apple
tags:
  - Apple
  - AFM 网站参考题
  - AFM Web References 2026-10-27
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: Deep-ML — Implement Self-Attention Mechanism
    url: 'https://www.deep-ml.com/problems/53'
    type: reference
  - title: PyTorch — scaled_dot_product_attention
    url: >-
      https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题目描述

参考 [Deep-ML 的 Self-Attention 编程练习](https://www.deep-ml.com/problems/53)。本题增加 batched input、causal mask、padding 和全空行；这些是手册练习约定。建议限时 25 分钟。

### 接口与输入含义

q、k、v 分别是已计算好的 query、key、value vectors，valid 表示每个 token 是否真实存在。它们不是 token IDs，本题不需要训练或投影出 Q/K/V。

实现 `causal_attention(q, k, v, valid)`：前三项分别是同设备、同 dtype 的 floating tensors，形状为 `[B,T,D]`、`[B,T,D]`、`[B,T,Dv]`；`valid` 是同设备 bool `[B,T]`。允许任意 padding 位置与全 padding 行。`B,T,D,Dv` 均为正整数，输入有限且缩放后的 scores 不溢出，练习只要求 float32 / float64。

### 输出与可见性规则

对 query i、key j，score 为点积除以 sqrt(D)；在所有可见 keys 上做 softmax，再以概率对 values 加权求和。

返回 `[B,T,Dv]`。每个有效 query 只能读取同 batch 中有效且位置不晚于自己的 key；无效 query 输出全零。不得修改输入，不用逐 token 循环或内置 attention，允许 matmul、mask 和 softmax；不含 dropout、projection、multi-head 或 KV cache。

### 输入输出示例

`q=k=zeros([1,3,1])`，`v=[[[2],[4],[8]]]`，`valid=[[True,True,False]]`，输出为 `[[[2],[3],[0]]]`。因为有效 scores 都为零，第二个 query 对前两个 values 取平均。

## 解题思路与参考答案

先计算 $QK^T/\sqrt{D}$，可见性同时满足 query 有效、key 有效和 causal 条件。全不可见行不能直接 softmax 全负无穷；先替换成零，再将不可见位置的 weights 全部置零。

```python
import math
import torch


def causal_attention(q, k, v, valid):
    length = q.shape[1]
    indices = torch.arange(length, device=q.device)
    causal = indices[:, None] >= indices[None, :]
    keep = valid[:, :, None] & valid[:, None, :] & causal
    scores = (q @ k.transpose(-2, -1)) / math.sqrt(q.shape[-1])
    masked = scores.masked_fill(~keep, float('-inf'))
    has_key = keep.any(dim=-1, keepdim=True)
    safe_scores = torch.where(has_key, masked, torch.zeros_like(masked))
    weights = torch.softmax(safe_scores, dim=-1).masked_fill(~keep, 0.0)
    return weights @ v
```

Mask 的 `[query,key]` 方向必须明确。由于有效 query 至少能看到自己，它不会出现没有 key 的情况；无效 query 则通过安全分支产生零输出。稠密 scores 和 mask 空间为 $O(BT^2)$，计算为 $O(BT^2(D+D_v))$。生产环境通常应考虑成熟的 fused attention 实现，本题用于展示机制。

## 简单测试怎么写

把实现和下面测试放在 `solution.py`，在安装 PyTorch 的环境运行 `python3 solution.py`。第一个 expected 来自手算平均；第二个检查全 padding；第三个用显式循环独立参考，并检查 backward。

```python
q = torch.zeros(1, 3, 1)
k = torch.zeros_like(q)
v = torch.tensor([[[2.0], [4.0], [8.0]]])
valid = torch.tensor([[True, True, False]])
before = v.clone()
out = causal_attention(q, k, v, valid)
assert out.shape == (1, 3, 1)
assert torch.allclose(out, torch.tensor([[[2.0], [3.0], [0.0]]]))
assert torch.equal(v, before)
assert torch.equal(
    causal_attention(q, k, v, torch.zeros_like(valid)), torch.zeros_like(v)
)

torch.manual_seed(7)
q = torch.randn(2, 4, 3, dtype=torch.float64, requires_grad=True)
k = torch.randn(2, 4, 3, dtype=torch.float64, requires_grad=True)
v = torch.randn(2, 4, 2, dtype=torch.float64, requires_grad=True)
valid = torch.tensor([[False, True, False, True], [False, False, False, False]])
out = causal_attention(q, k, v, valid)
expected = torch.zeros_like(out)
with torch.no_grad():
    for b in range(2):
        for t in range(4):
            if valid[b, t]:
                keys = [j for j in range(t + 1) if valid[b, j]]
                logits = torch.stack(
                    [(q[b, t] * k[b, j]).sum() / math.sqrt(3) for j in keys]
                )
                expected[b, t] = torch.softmax(logits, 0) @ v[b, keys]
assert torch.allclose(out, expected, atol=1e-10)
assert torch.isfinite(out).all()
out.sum().backward()
for tensor in (q, k, v):
    assert torch.isfinite(tensor.grad).all()
# A future value cannot affect an earlier query.
v_changed = v.detach().clone()
v_changed[0, 3] += 1000
changed = causal_attention(q.detach(), k.detach(), v_changed, valid)
assert torch.allclose(changed[0, 1], out.detach()[0, 1])
```

## 面试追问

**只用 loss mask 行不行？** 不行。loss mask 决定哪些位置受监督，attention mask 决定输入依赖，不能阻止 future-token leakage。

**为什么不把 mask 乘在 logits 上？** 零 logits 仍然有正的 softmax 权重；需要在 normalization 前排除不可见位置。

**是否支持 float16？** 本题契约不包含它；扩展时需考虑 accumulation precision、overflow、kernel 行为与数值测试，不能只改 dtype 声称等价。

