---
id: drustz-c153845fcc7cce325b
section: deepml
order: 135
level: A
title: Leaky ReLU Activation Function
quick: Deep-ML 练习 · Leaky ReLU Activation Function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/44_leaky-relu-activation-function/description.md
    type: primary
---
### description.md

Write a Python function `leaky_relu` that implements the Leaky Rectified Linear Unit (Leaky ReLU) activation function. The function should take a float `z` as input and an optional float `alpha`, with a default value of 0.01, as the slope for negative inputs. The function should return the value after applying the Leaky ReLU function.


### example.json

```json
{
  "input": "print(leaky_relu(0)) \nprint(leaky_relu(1))\nprint(leaky_relu(-1)) \nprint(leaky_relu(-2, alpha=0.1))",
  "output": "0\n1\n-0.01\n-0.2",
  "reasoning": "- For z = 0, the output is 0.\n- For z = 1, the output is 1.\n- For z = -1, the output is -0.01 (0.01 * -1).\n- For z = -2 with alpha = 0.1, the output is -0.2 (0.1 * -2)."
}
```




### learn.md


## Understanding the Leaky ReLU Activation Function

The Leaky ReLU (Leaky Rectified Linear Unit) activation function is a variant of the ReLU function used in neural networks. It addresses the "dying ReLU" problem by allowing a small, non-zero gradient when the input is negative. This small slope for negative inputs helps keep the function active and prevents neurons from becoming inactive.

### Mathematical Definition
The Leaky ReLU function is mathematically defined as:
$$
f(z) = \begin{cases} 
z & \text{if } z > 0 \\ 
\alpha z & \text{if } z \leq 0 
\end{cases}
$$
where $z$ is the input to the function and $\alpha$ is a small positive constant, typically $\alpha = 0.01$.

In this definition, the function returns $z$ for positive values, and for negative values, it returns $\alpha z$, allowing a small gradient to pass through.

### Characteristics
- **Output Range**: The output is in the range $(-\infty, \infty)$. Positive values are retained, while negative values are scaled by the factor $\alpha$, allowing them to be slightly negative.
- **Shape**: The function has a similar "L" shaped curve as ReLU, but with a small negative slope on the left side for negative $z$, creating a small gradient for negative inputs.
- **Gradient**: The gradient is 1 for positive values of $z$ and $\alpha$ for non-positive values. This allows the function to remain active even for negative inputs, unlike ReLU, where the gradient is zero for negative inputs.

This function is particularly useful in deep learning models as it mitigates the issue of "dead neurons" in ReLU by ensuring that neurons can still propagate a gradient even when the input is negative, helping to improve learning dynamics in the network.


### meta.json

```json
{
  "id": "44",
  "title": "Leaky ReLU Activation Function",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "https://youtu.be/V817IRW07vs",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/atharva-gite",
      "name": "atharva-gite"
    },
    {
      "profile_link": "https://www.youtube.com/@StoatScript/videos",
      "name": "StoatScript"
    }
  ],
  "marimo_link": "https://open-deep-ml.github.io/DML-OpenProblem/problem-4"
}
```




### solution.py

```python
def leaky_relu(z: float, alpha: float = 0.01) -> float | int:
    return z if z > 0 else alpha * z
```




### starter_code.py

```python
def leaky_relu(z: float, alpha: float = 0.01) -> float | int:
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(leaky_relu(5))",
    "expected_output": "5"
  },
  {
    "test": "print(leaky_relu(1))",
    "expected_output": "1"
  },
  {
    "test": "print(leaky_relu(-1))",
    "expected_output": "-0.01"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/44_leaky-relu-activation-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/44_leaky-relu-activation-function/description.md)。Deep-ML：Educational Use Only License。
