---
id: drustz-add56978adcef931e5
section: deepml
order: 152
level: A
title: Phi Transformation for Polynomial Features
quick: Deep-ML 练习 · Phi Transformation for Polynomial Features
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/84_phi-transformation-for-polynomial-features/description.md
    type: primary
---
### description.md

Write a Python function to perform a Phi Transformation that maps input features into a higher-dimensional space by generating polynomial features. The transformation allows models like linear regression to fit nonlinear data by introducing new feature dimensions that represent polynomial combinations of the original input features. The function should take a list of numerical data and a degree as inputs, and return a nested list where each inner list represents the transformed features of a data point. If the degree is less than 0, the function should return an empty list.


### example.json

```json
{
  "input": "data = [1.0, 2.0], degree = 2",
  "output": "[[1.0, 1.0, 1.0], [1.0, 2.0, 4.0]]",
  "reasoning": "The Phi Transformation generates polynomial features for each data point up to the specified degree. For data = [1.0, 2.0] and degree = 2, the transformation creates a nested list where each row contains powers of the data point from 0 to 2."
}
```




### learn.md

## Phi Transformation

The Phi Transformation maps input features into a higher-dimensional space by generating polynomial features. This allows models like linear regression to fit nonlinear data by introducing new feature dimensions that represent polynomial combinations of the original input features.

### Why Use Phi Transformation?

- To increase the expressive power of simple models such as linear models.
- To enable better fitting of nonlinear relationships in the data.

### Equations

For an input value $x$, the Phi Transformation expands it as:

$$
\Phi(x) = [1, x, x^2, x^3, \dots, x^d]
$$

Where $d$ is the specified degree, and $\Phi(x)$ represents the transformed feature vector.

### Example 1: Polynomial Expansion for One Value

Given $x = 3$ and $d = 3$, the Phi Transformation is:

$$
\Phi(3) = [1, 3, 9, 27]
$$

### Example 2: Transformation for Multiple Values

For $\text{data} = [1, 2]$ and $d = 2$, the Phi Transformation is:

$$
\Phi([1, 2]) = \begin{bmatrix} 1 & 1 & 1 \\ 1 & 2 & 4 \end{bmatrix}
$$


### meta.json

```json
{
  "id": "84",
  "title": "Phi Transformation for Polynomial Features",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/changyy06",
      "name": "changyy06"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def phi_transform(data: list[float], degree: int) -> list[list[float]]:
    """
    Perform a Phi Transformation to map input features into a higher-dimensional space by generating polynomial features.

    Args:
            data (list[float]): A list of numerical values to transform.
            degree (int): The degree of the polynomial expansion.

    Returns:
            list[list[float]]: A nested list where each inner list represents the transformed features of a data point.
    """
    if degree < 0 or not data:
        return []
    return np.array([[x**i for i in range(degree + 1)] for x in data]).tolist()
```




### starter_code.py

```python
import numpy as np


def phi_transform(data: list[float], degree: int) -> list[list[float]]:
    """
    Perform a Phi Transformation to map input features into a higher-dimensional space by generating polynomial features.

    Args:
            data (list[float]): A list of numerical values to transform.
            degree (int): The degree of the polynomial expansion.

    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(phi_transform([], 2))",
    "expected_output": "[]"
  },
  {
    "test": "print(phi_transform([1.0, 2.0], -1))",
    "expected_output": "[]"
  },
  {
    "test": "print(phi_transform([1.0, 2.0], 2))",
    "expected_output": "[[1.0, 1.0, 1.0], [1.0, 2.0, 4.0]]"
  },
  {
    "test": "print(phi_transform([1.0, 3.0], 3))",
    "expected_output": "[[1.0, 1.0, 1.0, 1.0], [1.0, 3.0, 9.0, 27.0]]"
  },
  {
    "test": "print(phi_transform([2.0], 4))",
    "expected_output": "[[1.0, 2.0, 4.0, 8.0, 16.0]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/84_phi-transformation-for-polynomial-features/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/84_phi-transformation-for-polynomial-features/description.md)。Deep-ML：Educational Use Only License。
