---
id: drustz-07c23121b5fbad88db
section: deepml
order: 124
level: A
title: Implement the Softsign Activation Function
quick: Deep-ML 练习 · Implement the Softsign Activation Function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/100_implement-the-softsign-activation-function/description.md
    type: primary
---
### description.md

Implement the Softsign activation function, a smooth activation function used in neural networks. Your task is to compute the Softsign value for a given input, ensuring the output is bounded between -1 and 1.


### example.json

```json
{
  "input": "softsign(1)",
  "output": "0.5",
  "reasoning": "For x = 1, the Softsign activation is calculated as $\\frac{x}{1 + |x|}$."
}
```




### learn.md

## Understanding the Softsign Activation Function

The Softsign activation function is a smooth, non-linear activation function used in neural networks. It’s similar to the hyperbolic tangent (tanh) function but with different properties, particularly in its tails which approach their limits more slowly.

### Mathematical Definition

The Softsign function is mathematically defined as:

$$
Softsign(x) = \frac{x}{1 + |x|}
$$

Where:
- $x$ is the input to the function
- $|x|$ represents the absolute value of $x$

### Characteristics

- **Output Range:** The output is bounded between -1 and 1, approaching these values asymptotically as $x$ approaches $\pm \infty$.
- **Shape:** The function has an S-shaped curve, similar to tanh but with a smoother approach to its asymptotes.
- **Gradient:** The gradient is smoother and more gradual compared to tanh, which can help prevent vanishing gradient problems in deep networks.
- **Symmetry:** The function is symmetric around the origin $(0,0)$.

### Key Properties

- **Bounded Output:** Unlike ReLU, Softsign naturally bounds its output between -1 and 1.
- **Smoothness:** The function is continuous and differentiable everywhere.
- **No Saturation:** The gradients approach zero more slowly than in tanh or sigmoid functions.
- **Zero-Centered:** The function crosses through the origin, making it naturally zero-centered.

This activation function can be particularly useful in scenarios where you need bounded outputs with more gradual saturation compared to tanh or sigmoid functions.


### meta.json

```json
{
  "id": "100",
  "title": "Implement the Softsign Activation Function",
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
  ],
  "marimo_link": "https://open-deep-ml.github.io/DML-OpenProblem/problem-softsign"
}
```




### solution.py

```python
def softsign(x: float) -> float:
    """
    Implements the Softsign activation function.

    Args:
        x (float): Input value

    Returns:
        float: The Softsign of the input, calculated as x/(1 + |x|)
    """
    return round(x / (1 + abs(x)), 4)
```




### starter_code.py

```python
def softsign(x: float) -> float:
    """
    Implements the Softsign activation function.

    Args:
            x (float): Input value

    Returns:
            float: The Softsign of the input"""
    # Your code here
    pass
    return round(val, 4)
```




### tests.json

```json
[
  {
    "test": "print(softsign(0))",
    "expected_output": "0.0"
  },
  {
    "test": "print(softsign(1))",
    "expected_output": "0.5"
  },
  {
    "test": "print(softsign(-1))",
    "expected_output": "-0.5"
  },
  {
    "test": "print(softsign(100))",
    "expected_output": "0.9901"
  },
  {
    "test": "print(softsign(-100))",
    "expected_output": "-0.9901"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/100_implement-the-softsign-activation-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/100_implement-the-softsign-activation-function/description.md)。Deep-ML：Educational Use Only License。
