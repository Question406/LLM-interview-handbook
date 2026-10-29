---
id: drustz-eea1a7355ad4f0522d
section: forum-notes
order: 229
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Implement 1-NN with No Python Loops'
quick: >-
  作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Implement 1-NN with No Python
  Loops
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Part 1: Implement 1-NN with No Python Loops

Implement:

```python
import numpy as np


def one_nn_predict(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_query: np.ndarray,
) -> np.ndarray:
    pass
```



### Requirements

- Do **not** use `for` or `while`
- Use **NumPy vector operations only**
- Return the predicted label for each query point
- You may assume:

`X_train.shape == (n, d)`
- `y_train.shape == (n,)`
- `X_query.shape == (m, d)`

### Example

```python
X_train = np.array(
    [
        [0.0, 0.0],
        [2.0, 0.0],
        [0.0, 2.0],
    ]
)
y_train = np.array([0, 1, 1])

X_query = np.array(
    [
        [1.2, 0.1],
        [0.2, 1.6],
    ]
)

# nearest training rows are 1 and 2
assert np.array_equal(one_nn_predict(X_train, y_train, X_query), np.array([1, 1]))
```



### Key Vectorization Trick

For a query vector `q` and training vector `x_i`:

```text
||q - x_i||^2 = ||q||^2 + ||x_i||^2 - 2 q^T x_i
```



For all queries at once:

- `query_sq = np.sum(X_query * X_query, axis=1, keepdims=True)` has shape `(m, 1)`
- `train_sq = np.sum(X_train * X_train, axis=1)` has shape `(n,)`
- `cross = X_query @ X_train.T` has shape `(m, n)`
- `dist2 = query_sq + train_sq[None, :] - 2 * cross` has shape `(m, n)`
Then:

- `nn_idx = np.argmin(dist2, axis=1)` has shape `(m,)`
- `pred = y_train[nn_idx]` has shape `(m,)`
Because `np.argmin` returns the first minimum, ties are automatically resolved by the smallest index.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
