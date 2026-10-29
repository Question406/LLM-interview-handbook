---
id: drustz-93c91ccf926d60b3a1
section: deepml
order: 126
level: A
title: Implementation of Log Softmax Function
quick: Deep-ML 练习 · Implementation of Log Softmax Function
companies: []
tags:
  - DrustZ
  - Deep-ML 练习
  - Deep-ML · ML Coding
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/39_implementation-of-log-softmax-function/description.md
    type: primary
---
### description.md

In machine learning and statistics, the softmax function is a generalization of the logistic function that converts a vector of scores into probabilities. The log-softmax function is the logarithm of the softmax function, and it is often used for numerical stability when computing the softmax of large numbers.

Given a 1D numpy array of scores, implement a Python function to compute the log-softmax of the array.


### example.json

```json
{
  "input": "A = np.array([1, 2, 3])\nprint(log_softmax(A))",
  "output": "array([-2.4076, -1.4076, -0.4076])",
  "reasoning": "The log-softmax function is applied to the input array [1, 2, 3]. The output array contains the log-softmax values for each element."
}
```




### learn.md


## Understanding Log Softmax Function

The log softmax function is a numerically stable way of calculating the logarithm of the softmax function. The softmax function converts a vector of arbitrary values (logits) into a vector of probabilities, where each value lies between 0 and 1, and the values sum to 1.

### Softmax Function
The softmax function is given by:
$$
\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_{j=1}^n e^{x_j}}
$$

### Log Softmax Function
Directly applying the logarithm to the softmax function can lead to numerical instability, especially when dealing with large numbers. To prevent this, we use the log-softmax function, which incorporates a shift by subtracting the maximum value from the input vector:
$$
\text{log softmax}(x_i) = x_i - \max(x) - \log\left(\sum_{j=1}^n e^{x_j - \max(x)}\right)
$$

This formulation helps to avoid overflow issues that can occur when exponentiating large numbers. The log-softmax function is particularly useful in machine learning for calculating probabilities in a stable manner, especially when used with cross-entropy loss functions.


### meta.json

```json
{
  "id": "39",
  "title": "Implementation of Log Softmax Function",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/MKFMIKU",
      "name": "Kangfu MEI"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def log_softmax(scores: list) -> np.ndarray:
    # Subtract the maximum value for numerical stability
    scores = scores - np.max(scores)
    return scores - np.log(np.sum(np.exp(scores)))
```




### starter_code.py

```python
import numpy as np


def log_softmax(scores: list) -> np.ndarray:
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(log_softmax([1, 2, 3]))",
    "expected_output": "[-2.4076, -1.4076, -0.4076]"
  },
  {
    "test": "print(log_softmax([1, 1, 1]))",
    "expected_output": "[-1.0986, -1.0986, -1.0986]"
  },
  {
    "test": "print(log_softmax([1, 1, .0000001]))",
    "expected_output": "[-0.862, -0.862, -1.862]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/39_implementation-of-log-softmax-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/39_implementation-of-log-softmax-function/description.md)。Deep-ML：Educational Use Only License。
