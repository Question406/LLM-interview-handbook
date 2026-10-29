---
id: drustz-e41aa0f92759f9ec3c
section: deepml
order: 35
level: A
title: Compute the Cross Product of Two 3D Vectors
quick: Deep-ML 练习 · Compute the Cross Product of Two 3D Vectors
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/118_compute-the-cross-product-of-two-3d-vectors/description.md
    type: primary
---
### description.md

Implement a function to compute the cross product of two 3-dimensional vectors. The cross product of two vectors results in a third vector that is perpendicular to both and follows the right-hand rule. This concept is fundamental in physics, engineering, and 3D graphics.


### example.json

```json
{
  "input": "cross_product([1, 0, 0], [0, 1, 0])",
  "output": "[0, 0, 1]",
  "reasoning": "The cross product of two orthogonal unit vectors [1, 0, 0] and [0, 1, 0] is [0, 0, 1], pointing in the positive z-direction as per the right-hand rule."
}
```




### learn.md

## Understanding the Cross Product

The **cross product** of two vectors $\vec{a}$ and $\vec{b}$ in 3D space is a vector that is perpendicular to both $\vec{a}$ and $\vec{b}$.

### Properties
- Defined only in 3 dimensions.
- The result $\vec{c} = \vec{a} \times \vec{b}$ is perpendicular to both $\vec{a}$ and $\vec{b}$.
- Follows the right-hand rule.

### Mathematical Formula

Given:
- $\vec{a} = [a_1, a_2, a_3]$
- $\vec{b} = [b_1, b_2, b_3]$

The cross product is:

$$
\vec{a} \times \vec{b} = [a_2 b_3 - a_3 b_2,\ a_3 b_1 - a_1 b_3,\ a_1 b_2 - a_2 b_1]
$$

### Use Cases
- Calculating normals in 3D graphics.
- Determining torque and angular momentum in physics.
- Verifying orthogonality in machine learning geometry.

### Example
For $\vec{a} = [1, 0, 0]$ and $\vec{b} = [0, 1, 0]$:

$$
\vec{a} \times \vec{b} = [0, 0, 1]
$$

The result points in the $z$-axis direction, confirming perpendicularity to both $\vec{a}$ and $\vec{b}$.


### meta.json

```json
{
  "id": "118",
  "title": "Compute the Cross Product of Two 3D Vectors",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def cross_product(a, b):
    """
    Compute the cross product of two 3D vectors a and b.
    Parameters:
        a (array-like): A 3-element vector.
        b (array-like): A 3-element vector.
    Returns:
        numpy.ndarray: The cross product vector.
    """
    a = np.array(a)
    b = np.array(b)

    if a.shape != (3,) or b.shape != (3,):
        raise ValueError("Both input vectors must be of length 3.")

    cross = np.array(
        [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ]
    )
    return cross
```




### starter_code.py

```python
import numpy as np


def cross_product(a, b):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(cross_product([1, 0, 0], [0, 1, 0]))",
    "expected_output": "[0, 0, 1]"
  },
  {
    "test": "print(cross_product([0, 1, 0], [0, 0, 1]))",
    "expected_output": "[1, 0, 0]"
  },
  {
    "test": "print(cross_product([1, 2, 3], [4, 5, 6]))",
    "expected_output": "[-3, 6, -3]"
  },
  {
    "test": "print(cross_product([1, 0, 0], [1, 0, 0]))",
    "expected_output": "[0, 0, 0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/118_compute-the-cross-product-of-two-3d-vectors/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/118_compute-the-cross-product-of-two-3d-vectors/description.md)。Deep-ML：Educational Use Only License。
