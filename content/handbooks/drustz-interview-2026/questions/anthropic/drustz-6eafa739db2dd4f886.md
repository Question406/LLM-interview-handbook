---
id: drustz-6eafa739db2dd4f886
section: anthropic
order: 8
level: A
title: Ml Programming Screen
quick: original-structured-preparation-guide · Ml Programming Screen
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/ml-programming-screen
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# ML Programming Screen：Scaled Dot-Product Attention

> 修正说明：旧正文只是候选人的 OA 流程和 Why Anthropic，未包含公开摘要指出的 sequence model / attention 编程任务，已经移除。

## 题目方向

这一轮约 40 分钟，要求阅读数学表达式并使用 NumPy 或类似工具实现 sequence-model 操作。公开摘要明确提到了 scaled dot-product attention 和 `einsum`，但没有公开唯一函数签名。

给定：

```text
Q: (..., query_len, d)
K: (..., key_len, d)
V: (..., key_len, value_dim)
mask: 可选，True 表示允许关注
```



计算：

```text
softmax(Q K^T / sqrt(d)) V
```



## NumPy 参考实现

```python
import numpy as np


def scaled_dot_product_attention(Q, K, V, mask=None):
    if Q.shape[-1] != K.shape[-1]:
        raise ValueError("Q and K must share the head dimension")
    if K.shape[-2] != V.shape[-2]:
        raise ValueError("K and V must share the key length")

    scores = Q @ np.swapaxes(K, -1, -2)
    scores = scores / np.sqrt(Q.shape[-1])

    if mask is not None:
        scores = np.where(mask, scores, -np.inf)

    row_max = np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(scores - row_max)
    if mask is not None:
        exp_scores = np.where(mask, exp_scores, 0.0)
    denominator = exp_scores.sum(axis=-1, keepdims=True)
    weights = np.divide(
        exp_scores,
        denominator,
        out=np.zeros_like(exp_scores),
        where=denominator != 0,
    )
    return weights @ V
```



多头 batch 也可用：

```python
scores = np.einsum("...qd,...kd->...qk", Q, K)
output = np.einsum("...qk,...kv->...qv", weights, V)
```



## 复杂度

设 batch 与 head 的合并数量为 `B`，query 长度 `Qn`、key 长度 `Kn`、head 维度 `d`。score 和输出计算时间约为 `O(B × Qn × Kn × d)`；attention matrix 空间为 `O(B × Qn × Kn)`。

## 边界

全被 mask 的一行、causal mask 方向、padding mask 广播、`float16` 的 `-inf`、shape 不匹配、`d = 0`，以及 softmax 必须沿 key 维而不是其他维度。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/ml-programming-screen)
- [相关来源](https://www.1point3acres.com/bbs/thread-1137418-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
