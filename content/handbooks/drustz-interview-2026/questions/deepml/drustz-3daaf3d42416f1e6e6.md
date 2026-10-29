---
id: drustz-3daaf3d42416f1e6e6
section: deepml
order: 122
level: A
title: Implement the SELU Activation Function
quick: Deep-ML 练习 · Implement the SELU Activation Function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/103_implement-the-selu-activation-function/description.md
    type: primary
---
### description.md

Implement the SELU (Scaled Exponential Linear Unit) activation function, a self-normalizing variant of ELU. Your task is to compute the SELU value for a given input while ensuring numerical stability.


### example.json

```json
{
  "input": "selu(-1.0)",
  "output": "-1.1113",
  "reasoning": "For x = -1.0, the SELU activation is calculated using the formula $SELU(x) = \\lambda \\alpha (e^x - 1)$. Substituting the values of $\\lambda$ and $\\alpha$, we get $SELU(-1.0) = 1.0507 \\times 1.6733 \\times (e^{-1.0} - 1) = -1.1113$."
}
```




### learn.md

## Understanding the SELU Activation Function

The SELU (Scaled Exponential Linear Unit) activation function is a self-normalizing variant of the ELU activation function, introduced in 2017. It's particularly useful in deep neural networks as it automatically ensures normalized outputs with zero mean and unit variance.

### Mathematical Definition

The SELU function is defined as:

$$
SELU(x) = \lambda \begin{cases} 
x & \text{if } x > 0 \\
\alpha(e^x - 1) & \text{if } x \leq 0
\end{cases}
$$

Where:
- $\lambda \approx 1.0507$ is the scale parameter
- $\alpha \approx 1.6733$ is the alpha parameter

### Characteristics

- **Output Range:** The function maps inputs to $(-\lambda\alpha, \infty)$
- **Self-Normalizing:** Automatically maintains mean close to 0 and variance close to 1
- **Continuous:** The function is continuous and differentiable everywhere
- **Non-Linear:** Provides non-linearity while preserving gradients for negative values
- **Parameters:** Uses carefully chosen values for $\lambda$ and $\alpha$ to ensure self-normalization

### Advantages

1. **Self-Normalization:** Eliminates the need for batch normalization in many cases
2. **Robust Learning:** Helps prevent vanishing and exploding gradients
3. **Better Performance:** Often leads to faster training in deep neural networks
4. **Internal Normalization:** Maintains normalized activations throughout the network

### Use Cases

SELU is particularly effective in:
- Deep neural networks where maintaining normalized activations is crucial
- Networks that require self-normalizing properties
- Scenarios where batch normalization might be problematic or expensive


### meta.json

```json
{
  "id": "103",
  "title": "Implement the SELU Activation Function",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Haleshot",
      "name": "Haleshot"
    }
  ]
}
```




### solution.py

```python
import math


def selu(x: float) -> float:
    """
    Implements the SELU (Scaled Exponential Linear Unit) activation function.

    Args:
        x: Input value

    Returns:
        SELU activation value
    """
    alpha = 1.6732632423543772
    scale = 1.0507009873554804
    return round(scale * x if x > 0 else scale * alpha * (math.exp(x) - 1), 4)
```




### starter_code.py

```python
def selu(x: float) -> float:
    """
    Implements the SELU (Scaled Exponential Linear Unit) activation function.

    Args:
            x: Input value

    Returns:
            SELU activation value
    """
    alpha = 1.6732632423543772
    scale = 1.0507009873554804
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(round(selu(1.0), 4))",
    "expected_output": "1.0507"
  },
  {
    "test": "print(round(selu(0.0), 4))",
    "expected_output": "0.0"
  },
  {
    "test": "print(round(selu(-1.0), 4))",
    "expected_output": "-1.1113"
  },
  {
    "test": "print(round(selu(5.0), 4))",
    "expected_output": "5.2535"
  },
  {
    "test": "print(round(selu(-5.0), 4))",
    "expected_output": "-1.7463"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/103_implement-the-selu-activation-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/103_implement-the-selu-activation-function/description.md)。Deep-ML：Educational Use Only License。
