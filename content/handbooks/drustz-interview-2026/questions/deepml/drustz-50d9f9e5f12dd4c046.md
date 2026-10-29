---
id: drustz-50d9f9e5f12dd4c046
section: deepml
order: 119
level: A
title: Implement the Hard Sigmoid Activation Function
quick: Deep-ML 练习 · Implement the Hard Sigmoid Activation Function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/96_implement-the-hard-sigmoid-activation-function/description.md
    type: primary
---
### description.md

Implement the Hard Sigmoid activation function, a computationally efficient approximation of the standard sigmoid function. Your function should take a single input value and return the corresponding output based on the Hard Sigmoid definition.


### example.json

```json
{
  "input": "hard_sigmoid(0.0)",
  "output": "0.5",
  "reasoning": "The input 0.0 falls in the linear region of the Hard Sigmoid function. Using the formula $HardSigmoid(x) = 0.2x + 0.5$, the output is $0.2 \\times 0.0 + 0.5 = 0.5$."
}
```




### learn.md

## Understanding the Hard Sigmoid Activation Function

The Hard Sigmoid is a piecewise linear approximation of the sigmoid activation function. It's computationally more efficient than the standard sigmoid function while maintaining similar characteristics. This function is particularly useful in neural networks where computational efficiency is crucial.

### Mathematical Definition

The Hard Sigmoid function is mathematically defined as:

$$
HardSigmoid(x) = \begin{cases} 
0 & \text{if } x \leq -2.5 \\ 
0.2x + 0.5 & \text{if } -2.5 < x < 2.5 \\ 
1 & \text{if } x \geq 2.5 
\end{cases}
$$

Where $x$ is the input to the function.

### Characteristics

- **Output Range:** The output is always bounded in the range $[0, 1]$
- **Shape:** The function consists of three parts:
  - A constant value of 0 for inputs <= -2.5
  - A linear segment with slope 0.2 for inputs between -2.5 and 2.5
  - A constant value of 1 for inputs >= 2.5
- **Gradient:** The gradient is 0.2 in the linear region and 0 in the saturated regions

### Advantages in Neural Networks

This function is particularly useful in neural networks as it provides:
- Computational efficiency compared to standard sigmoid
- Bounded output range similar to sigmoid
- Simple gradient computation


### meta.json

```json
{
  "id": "96",
  "title": "Implement the Hard Sigmoid Activation Function",
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
  "marimo_link": "https://open-deep-ml.github.io/deepml-notebooks/96/"
}
```




### solution.py

```python
def hard_sigmoid(x: float) -> float:
    """
    Implements the Hard Sigmoid activation function.

    Args:
        x (float): Input value

    Returns:
        float: The Hard Sigmoid of the input
    """
    if x <= -2.5:
        return 0.0
    elif x >= 2.5:
        return 1.0
    else:
        return 0.2 * x + 0.5
```




### starter_code.py

```python
def hard_sigmoid(x: float) -> float:
    """
    Implements the Hard Sigmoid activation function.

    Args:
            x (float): Input value

    Returns:
            float: The Hard Sigmoid of the input
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(hard_sigmoid(.56))",
    "expected_output": "0.612"
  },
  {
    "test": "print(hard_sigmoid(3.0))",
    "expected_output": "1.0"
  },
  {
    "test": "print(hard_sigmoid(0.0))",
    "expected_output": "0.5"
  },
  {
    "test": "print(hard_sigmoid(1.0))",
    "expected_output": "0.7"
  },
  {
    "test": "print(hard_sigmoid(-1.0))",
    "expected_output": "0.3"
  },
  {
    "test": "print(hard_sigmoid(2.5))",
    "expected_output": "1.0"
  },
  {
    "test": "print(hard_sigmoid(-2.5))",
    "expected_output": "0.0"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/96_implement-the-hard-sigmoid-activation-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/96_implement-the-hard-sigmoid-activation-function/description.md)。Deep-ML：Educational Use Only License。
