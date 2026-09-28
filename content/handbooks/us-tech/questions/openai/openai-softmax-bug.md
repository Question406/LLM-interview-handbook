---
id: openai-softmax-bug
section: openai
order: 6
level: S
title: OpenAI：attention 里 softmax 轴和 mask 用 0 会怎样，怎么单测
quick: >-
  softmax 必须沿 key 长度，`dim=-1` 让 `[B,H,T,S]` 的最后一维求和为 1。因果 mask 要在 softmax 前打成
  $-\infty$，用 $0$ 乘过的位置 $e^{0}=1$，未来 token 仍分到正质量。单测查质量和、未来位是否精确 0。
tags:
  - OpenAI
  - Attention
  - Softmax
  - Debug
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Experience (2025)
    url: https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2
    type: candidate-first-hand
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer / MLE
- 轮次：给一份带 bug 的 Transformer，公开复述里 softmax 维和因果 mask 是高频植入点
- 来源：Exponent 2025 报告；总查法见 `openai-transformer-debug`

这类 bug 不会 NaN，生成「看起来像语言」，所以不能靠 loss 曲线找。我会用 shape 和一块小矩阵把错误钉死。

## 题怎么来的

Attention 论文写的是 $\mathrm{softmax}(QK^\top / \sqrt{d_k})$。实现落到四维张量之后，softmax 的 `dim` 和 mask 的填充值都有好几种「能跑」的写法。OpenAI 这轮要你证明你知道哪一种在数学上是注意力。和 `openai-entropy-l1` 一样，先得到合法分布，再谈数值。

## 两个错法，两种失败模式

scores 是 `[B, H, T, S]`，$T$ 是 query 长，$S$ 是 key 长。

**轴错了。** `softmax(scores, dim=0)` 或 `dim=1` 会在 batch / head 上归一。每个 query 对 key 的权重和不为一，跨样本的质量搅在一起。短序列偶然能过肉眼检查，一上 batch 就乱。正确是 `dim=-1`（或 `dim=3`），不变量：

$$
\sum_{s=1}^{S} a_{bhts} = 1.
$$

**mask 用 0。** 有人写 `scores = scores * causal`，未来位置变成 0。但 $\mathrm{softmax}$ 里 $e^{0}=1$，未来位仍占一块正概率。位置越靠前、未遮蔽的 logit 越接近 0 时，泄漏越大。必须是 softmax 之前 `masked_fill(..., -inf)`，让 $e^{-\infty}=0$。加法 mask 用 $-1\mathrm{e}9$ 在 fp16 里可能 overflow 或不够负，优先真的 $-\infty$，softmax 内部减 max 仍然稳定。

缩放漏了 $1/\sqrt{d_k}$ 是第三类：fp16 点积方差随 $d_k$ 涨，softmax 饱和成 one-hot，或者直接 inf。和轴 / mask 分开测。

## 我会写的最小单测

```python
def test_causal_mask_zero_leaks():
    s = torch.tensor([[[[2.0, 1.0, 0.5]]]])          # [1,1,1,3]
    future = torch.tensor([[[[False, False, True]]]])
    bad = torch.softmax(s * (~future).float(), dim=-1)
    good = torch.softmax(s.masked_fill(future, float("-inf")), dim=-1)
    assert bad[0, 0, 0, 2] > 0
    assert good[0, 0, 0, 2].item() == 0.0
    assert torch.allclose(good.sum(dim=-1), torch.ones(1, 1, 1))

def test_softmax_axis():
    x = torch.randn(2, 4, 3, 5)
    a = torch.softmax(x, dim=-1)
    assert a.shape == x.shape
    assert torch.allclose(a.sum(dim=-1), torch.ones(2, 4, 3), atol=1e-5)
```

再加一条序列级：`T=4` 的下三角 mask，位置 $t$ 只能看见 $s\le t$。把未来位的注意力抽出来，应当全 0。greedy 有/无 cache 对齐是更强的端到端网，见 `openai-kv-cache-impl`。

先 `eval()` + 固定 seed，再断言，不要用「生成看起来对了」当测试。

## 追问

- **padding mask 和因果 mask 谁先？** 都在 softmax 前，逻辑或之后一次 fill。padding 的 key 也必须是 $-\infty$，否则短序列会看 pad。
- **为什么减 max？** 防止 `exp` overflow。轴要对：`max` 沿 key 维，`keepdims=True`，不要对整个 batch 减同一个标量。
- **decode 一步还要 mask 吗？** 单 token 且 cache 已是前缀，通常不必。一次多个新 token 仍要相对 cache 的因果块。
