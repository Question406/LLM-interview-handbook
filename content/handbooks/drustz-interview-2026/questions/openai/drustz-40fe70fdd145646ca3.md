---
id: drustz-40fe70fdd145646ca3
section: openai
order: 100
level: A
title: Implement Softmax Cross-Entropy Loss and Backprop (NumPy)
quick: >-
  original-structured-preparation-guide · Implement Softmax Cross-Entropy Loss
  and Backprop (NumPy)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/ce840bf0-d07d-422c-a8d0-36045dd3bb1a
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# NumPy：Softmax Cross-Entropy 与backpropagation

> 旧页面引用的是宽泛 ML debugging 材料。下面给出标题所指向的标准、数值稳定实现。

## 前向

输入 logits 形状为 `(batch, classes)`，labels 是每行的正确类别下标。先对每行减去最大值，避免 `exp` 溢出：

```python
import numpy as np


def softmax_cross_entropy(logits, labels):
    logits = np.asarray(logits, dtype=np.float64)
    labels = np.asarray(labels)
    if logits.ndim != 2 or labels.shape != (logits.shape[0],):
        raise ValueError("invalid shapes")

    shifted = logits - logits.max(axis=1, keepdims=True)
    exp_values = np.exp(shifted)
    probabilities = exp_values / exp_values.sum(axis=1, keepdims=True)

    batch = logits.shape[0]
    loss = -np.log(probabilities[np.arange(batch), labels]).mean()

    gradient = probabilities.copy()
    gradient[np.arange(batch), labels] -= 1.0
    gradient /= batch
    return loss, gradient
```



更稳定的 loss 可直接用 log-sum-exp 计算，避免正确类别概率下溢到 0。

## 为什么梯度正确

单个样本对 logit `z_j` 的梯度是：

```text
dL/dz_j = p_j - 1[j == correct_class]
```



batch 取 mean 时再除以 batch size。如果 loss 取 sum，则不能除。

## 复杂度与边界

时间和输出梯度空间都是 `O(batch × classes)`。需要处理空 batch、label 越界、只有一个类别、float16 精度、ignore index / padding mask，以及 one-hot label 与 index label 两种 API 不要混用。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ce840bf0-d07d-422c-a8d0-36045dd3bb1a)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
