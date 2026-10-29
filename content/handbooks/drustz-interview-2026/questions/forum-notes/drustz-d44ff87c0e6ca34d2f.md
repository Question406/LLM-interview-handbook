---
id: drustz-d44ff87c0e6ca34d2f
section: forum-notes
order: 231
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Reference Solution
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Reference Solution
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
## Reference Solution

### Part 1: Vectorized 1-NN

```python
import numpy as np


def one_nn_indices(X_train: np.ndarray, X_query: np.ndarray) -> np.ndarray:
    """
    Return the nearest training index for each query.

    X_train: (n, d)
    X_query: (m, d)
    Returns: (m,)
    """
    train_sq = np.sum(X_train * X_train, axis=1)  # (n,)
    query_sq = np.sum(X_query * X_query, axis=1, keepdims=True)  # (m, 1)
    cross = X_query @ X_train.T  # (m, n)

    dist2 = query_sq + train_sq[None, :] - 2.0 * cross  # (m, n)
    return np.argmin(dist2, axis=1)  # (m,)


def one_nn_predict(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_query: np.ndarray,
) -> np.ndarray:
    nn_idx = one_nn_indices(X_train, X_query)
    return y_train[nn_idx]
```



### Part 2: Neural Network Forward Pass

```python
import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = x - np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def one_nn_network_forward(
    X_train: np.ndarray,
    X_query: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
      probs:  (m, n) softmax over training exemplars
      nn_idx: (m,) nearest-neighbor index for each query
    """
    W = 2.0 * X_train.T  # (d, n)
    b = -np.sum(X_train * X_train, axis=1)  # (n,)

    logits = X_query @ W + b  # (m, n)
    probs = softmax(logits, axis=1)  # (m, n)
    nn_idx = np.argmax(probs, axis=1)  # (m,)
    return probs, nn_idx
```



### Sanity Check

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

pred = one_nn_predict(X_train, y_train, X_query)
assert np.array_equal(pred, np.array([1, 1]))

probs, idx = one_nn_network_forward(X_train, X_query)
assert np.array_equal(idx, np.array([1, 2]))
assert np.array_equal(y_train[idx], pred)
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
