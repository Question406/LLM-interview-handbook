---
id: drustz-fd9016a9cf41e1176c
section: deepml
order: 3
level: A
title: Adagrad Optimizer
quick: Deep-ML 练习 · Adagrad Optimizer
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/145_adagrad-optimizer/description.md
    type: primary
---
### description.md

Implement the Adagrad optimizer update step function. Your function should take the current parameter value, gradient, and accumulated squared gradients as inputs, and return the updated parameter value and new accumulated squared gradients. The function should also handle scalar and array inputs, and include proper input validation.

### example.json

```json
{
  "input": "parameter = 1.0, grad = 0.1, G = 1.0",
  "output": "(0.999, 1.01)",
  "reasoning": "The Adagrad optimizer computes updated values for the parameter and the accumulated squared gradients. With input values parameter=1.0, grad=0.1, and G=1.0, the updated parameter becomes 0.999 and the updated G becomes 1.01."
}
```




### learn.md

# Implementing Adagrad Optimizer

## Introduction
Adagrad (Adaptive Gradient Algorithm) is an optimization algorithm that adapts the learning rate to each parameter, performing larger updates for infrequent parameters and smaller updates for frequent ones. This makes it particularly well-suited for dealing with sparse data.

## Learning Objectives
- Understand how Adagrad optimizer works
- Learn to implement adaptive learning rates
- Gain practical experience with gradient-based optimization

## Theory
Adagrad adapts the learning rate for each parameter based on the historical gradients. The key equations are:

$G_t = G_{t-1} + g_t^2$ (Accumulated squared gradients)

$\theta_t = \theta_{t-1} - \dfrac{\alpha}{\sqrt{G_t} + \epsilon} \cdot g_t$ (Parameter update)

Where:
- $G_t$ is the sum of squared gradients up to time step t
- $\alpha$ is the initial learning rate
- $\epsilon$ is a small constant for numerical stability
- $g_t$ is the gradient at time step t

Read more at:

1. Duchi, J., Hazan, E., & Singer, Y. (2011). Adaptive subgradient methods for online learning and stochastic optimization. Journal of Machine Learning Research, 12, 2121–2159. [PDF](https://www.jmlr.org/papers/volume12/duchi11a/duchi11a.pdf)
2. Ruder, S. (2017). An overview of gradient descent optimization algorithms. [arXiv:1609.04747](https://arxiv.org/pdf/1609.04747)


## Problem Statement
Implement the Adagrad optimizer update step function. Your function should take the current parameter value, gradient, and accumulated squared gradients as inputs, and return the updated parameter value and new accumulated squared gradients.

### Input Format
The function should accept:
- parameter: Current parameter value
- grad: Current gradient
- G: Accumulated squared gradients
- learning_rate: Learning rate (default=0.01)
- epsilon: Small constant for numerical stability (default=1e-8)

### Output Format
Return tuple: (updated_parameter, updated_G)

## Example
```python
# Example usage:
parameter = 1.0
grad = 0.1
G = 1.0

new_param, new_G = adagrad_optimizer(parameter, grad, G)
```



## Tips
- Initialize G as zeros
- Use numpy for numerical operations
- Test with both scalar and array inputs

---


### meta.json

```json
{
  "id": "145",
  "title": "Adagrad Optimizer",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/mavleo96",
      "name": "Vijayabharathi Murugan"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def adagrad_optimizer(parameter, grad, G, learning_rate=0.01, epsilon=1e-8):
    """
    Update parameters using the Adagrad optimizer.
    Adapts the learning rate for each parameter based on the historical gradients.

    Args:
        parameter: Current parameter value
        grad: Current gradient
        G: Accumulated squared gradients
        learning_rate: Learning rate (default=0.01)
        epsilon: Small constant for numerical stability (default=1e-8)

    Returns:
        tuple: (updated_parameter, updated_G)
    """
    assert learning_rate > 0, "Learning rate must be positive"
    assert epsilon > 0, "Epsilon must be positive"
    assert all(G >= 0) if isinstance(G, np.ndarray) else G >= 0, (
        "G must be non-negative"
    )

    # Update accumulated squared gradients
    G = G + grad**2

    # Update parameters using adaptive learning rate
    update = learning_rate * grad / (np.sqrt(G) + epsilon)
    parameter = parameter - update

    return np.round(parameter, 5), np.round(G, 5)
```




### starter_code.py

```python
import numpy as np


def adagrad_optimizer(parameter, grad, G, learning_rate=0.01, epsilon=1e-8):
    """
    Update parameters using the Adagrad optimizer.
    Adapts the learning rate for each parameter based on the historical gradients.

    Args:
        parameter: Current parameter value
        grad: Current gradient
        G: Accumulated squared gradients
        learning_rate: Learning rate (default=0.01)
        epsilon: Small constant for numerical stability (default=1e-8)

    Returns:
        tuple: (updated_parameter, updated_G)
    """
    # Your code here
    return np.round(parameter, 5), np.round(G, 5)
```




### tests.json

```json
[
  {
    "test": "print(adagrad_optimizer(1., 0.5, 1., 0.01, 1e-8))",
    "expected_output": "(0.99553, 1.25)"
  },
  {
    "test": "print(adagrad_optimizer(np.array([1., 2.]), np.array([0.1, 0.2]), np.array([1., 1.]), 0.01, 1e-8))",
    "expected_output": "(array([0.999, 1.99804]), array([1.01, 1.04]))"
  },
  {
    "test": "print(adagrad_optimizer(np.array([1., 2.]), np.array([0., 0.2]), np.array([0., 1.]), 0.01, 1e-8))",
    "expected_output": "(array([1., 1.99804]), array([0., 1.04]))"
  },
  {
    "test": "print(adagrad_optimizer(np.array([1., 1.]), np.array([1., 1.]), np.array([10000., 1.]), 0.01, 1e-8))",
    "expected_output": "(array([0.9999, 0.99293]), array([10001., 2.]))"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/145_adagrad-optimizer/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/145_adagrad-optimizer/description.md)。Deep-ML：Educational Use Only License。
