---
id: drustz-6461fe200fb7eff17a
section: deepml
order: 42
level: A
title: Deep-ML legacy · 134 cross entropy loss
quick: Deep-ML 练习 · Deep-ML legacy · 134 cross entropy loss
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/134_cross_entropy_loss/learn.md
    type: primary
---
### learn.md

## Multi-class Cross-Entropy Loss Implementation

Cross-entropy loss, also known as log loss, measures the performance of a classification model whose output is a probability value between 0 and 1. For multi-class classification tasks, we use the categorical cross-entropy loss.

### Mathematical Background

For a single sample with C classes, the categorical cross-entropy loss is defined as:

$L = -\sum_{c=1}^{C} y_c \log(p_c)$

where:

- $y_c$ is a binary indicator (0 or 1) if class label c is the correct classification for the sample
- $p_c$ is the predicted probability that the sample belongs to class c
- $C$ is the number of classes

### Implementation Requirements

Your task is to implement a function that computes the average cross-entropy loss across multiple samples:

$L_{batch} = -\frac{1}{N}\sum_{n=1}^{N}\sum_{c=1}^{C} y_{n,c} \log(p_{n,c})$

where N is the number of samples in the batch.

### Important Considerations

- Handle numerical stability by adding a small epsilon to avoid log(0)
- Ensure predicted probabilities sum to 1 for each sample
- Return average loss across all samples
- Handle invalid inputs appropriately

The function should take predicted probabilities and true labels as input and return the average cross-entropy loss.


### solution.py

```python
import numpy as np


def compute_cross_entropy_loss(
    predicted_probs: np.ndarray, true_labels: np.ndarray
) -> float:

    # Given
    epsilon = 1e-15
    predicted_probs = np.clip(predicted_probs, epsilon, 1 - epsilon)

    # Write your code here
    log_probs = np.log(predicted_probs)
    loss = -np.sum(true_labels * log_probs, axis=1)
    return float(np.mean(loss))


def test_compute_cross_entropy_loss():
    # Test case 1: Perfect predictions
    pred1 = np.array([[1, 0, 0], [0, 1, 0]])
    true1 = np.array([[1, 0, 0], [0, 1, 0]])
    expected1 = 0.0
    assert np.isclose(compute_cross_entropy_loss(pred1, true1), expected1), (
        "Test case 1 failed"
    )

    # Test case 2: Completely wrong predictions
    pred2 = np.array([[0.1, 0.8, 0.1], [0.8, 0.1, 0.1]])
    true2 = np.array([[0, 0, 1], [0, 1, 0]])
    expected2 = -np.mean([np.log(0.1), np.log(0.1)])
    assert np.isclose(compute_cross_entropy_loss(pred2, true2), expected2), (
        "Test case 2 failed"
    )

    # Test case 3: Typical predictions
    pred3 = np.array([[0.7, 0.2, 0.1], [0.3, 0.6, 0.1]])
    true3 = np.array([[1, 0, 0], [0, 1, 0]])
    expected3 = -np.mean([np.log(0.7), np.log(0.6)])
    assert np.isclose(compute_cross_entropy_loss(pred3, true3), expected3), (
        "Test case 3 failed"
    )


if __name__ == "__main__":
    test_compute_cross_entropy_loss()
    print("All test cases passed!")
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/Problems/134_cross_entropy_loss/learn.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/134_cross_entropy_loss/learn.md)。Deep-ML：Educational Use Only License。
