---
id: drustz-076818dc40f34efff5
section: deepml
order: 13
level: A
title: Calculate 2x2 Matrix Inverse
quick: Deep-ML 练习 · Calculate 2x2 Matrix Inverse
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/8_calculate-2x2-matrix-inverse/description.md
    type: primary
---
### description.md

Write a Python function that calculates the inverse of a 2x2 matrix. Return 'None' if the matrix is not invertible.


### example.json

```json
{
  "input": "matrix = [[4, 7], [2, 6]]",
  "output": "[[0.6, -0.7], [-0.2, 0.4]]",
  "reasoning": "The inverse of a 2x2 matrix [a, b], [c, d] is given by (1/(ad-bc)) * [d, -b], [-c, a], provided ad-bc is not zero."
}
```




### learn.md


## Calculating the Inverse of a 2x2 Matrix

The inverse of a matrix \( A \) is another matrix, often denoted \( A^{-1} \), such that:
$$
AA^{-1} = A^{-1}A = I
$$
where \( I \) is the identity matrix. For a 2x2 matrix:
$$
A = \begin{pmatrix} 
a & b \\ 
c & d 
\end{pmatrix}
$$

The inverse is given by:
$$
A^{-1} = \frac{1}{\det(A)} \begin{pmatrix} 
d & -b \\ 
-c & a 
\end{pmatrix}
$$

provided that the determinant \( \det(A) = ad - bc \) is non-zero. If \( \det(A) = 0 \), the matrix does not have an inverse.

### Importance
Calculating the inverse of a matrix is essential in various applications, such as solving systems of linear equations, where the inverse is used to find solutions efficiently.


### meta.json

```json
{
  "id": "8",
  "title": "Calculate 2x2 Matrix Inverse",
  "difficulty": "medium",
  "category": "Linear Algebra",
  "video": "https://youtu.be/-fhFySMHPZk",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    },
    {
      "profile_link": "https://www.youtube.com/@StoatScript/videos",
      "name": "StoatScript"
    }
  ],
  "tinygrad_difficulty": "easy",
  "pytorch_difficulty": "easy"
}
```




### solution.py

```python
import torch


def inverse_2x2(matrix) -> torch.Tensor | None:
    """
    Compute inverse of a 2×2 matrix using PyTorch.
    Input can be Python list, NumPy array, or torch Tensor.
    Returns a 2×2 tensor or None if the matrix is singular.
    """
    m = torch.as_tensor(matrix, dtype=torch.float)
    a, b = m[0, 0], m[0, 1]
    c, d = m[1, 0], m[1, 1]
    det = a * d - b * c
    if det == 0:
        return None
    inv = torch.stack(
        [torch.stack([d / det, -b / det]), torch.stack([-c / det, a / det])]
    )
    return inv
```




### starter_code.py

```python
import torch


def inverse_2x2(matrix) -> torch.Tensor | None:
    """
    Compute inverse of a 2×2 matrix using PyTorch.
    Input can be Python list, NumPy array, or torch Tensor.
    Returns a 2×2 tensor or None if the matrix is singular.
    """
    m = torch.as_tensor(matrix, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = inverse_2x2(torch.tensor([[1.0, 0.0], [0.0, 1.0]]))\nprint(res.numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 1.0]]"
  },
  {
    "test": "import torch\nres = inverse_2x2(torch.tensor([[1.0, 2.0], [3.0, 4.0]]))\nprint(res.numpy().tolist())",
    "expected_output": "[[-2.0, 1.0], [1.5, -0.5]]"
  },
  {
    "test": "import torch\nres = inverse_2x2(torch.tensor([[1.0, 2.0], [2.0, 4.0]]))\nprint(res)",
    "expected_output": "None"
  }
]
```




### solution.py

```python
def inverse_2x2(matrix: list[list[float]]) -> list[list[float]]:
    a, b, c, d = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
    determinant = a * d - b * c
    if determinant == 0:
        return None
    inverse = [[d / determinant, -b / determinant], [-c / determinant, a / determinant]]
    return inverse
```




### starter_code.py

```python
def inverse_2x2(matrix: list[list[float]]) -> list[list[float]]:
    return inverse
```




### tests.json

```json
[
  {
    "test": "print(inverse_2x2([[4, 7], [2, 6]]))",
    "expected_output": "[[0.6, -0.7], [-0.2, 0.4]]"
  },
  {
    "test": "print(inverse_2x2([[2, 1], [6, 2]]))",
    "expected_output": "[[-1.0, 0.5], [3.0, -1.0]]"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor


def inverse_2x2_tg(matrix) -> Tensor | None:
    """
    Compute inverse of a 2×2 matrix using tinygrad.
    Input can be Python list, NumPy array, or tinygrad Tensor.
    Returns a 2×2 Tensor or None if the matrix is singular.
    """
    m = Tensor(matrix).float()
    a, b = m[0, 0], m[0, 1]
    c, d = m[1, 0], m[1, 1]
    det = a * d - b * c
    if det.numpy() == 0:
        return None
    inv = Tensor([[d, -b], [-c, a]]) / det
    return inv
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def inverse_2x2_tg(matrix) -> Tensor | None:
    """
    Compute inverse of a 2×2 matrix using tinygrad.
    Input can be Python list, NumPy array, or tinygrad Tensor.
    Returns a 2×2 Tensor or None if the matrix is singular.
    """
    m = Tensor(matrix).float()
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = inverse_2x2_tg([[1.0, 0.0], [0.0, 1.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 1.0]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = inverse_2x2_tg([[1.0, 2.0], [3.0, 4.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[[-2.0, 1.0], [1.5, -0.5]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = inverse_2x2_tg([[1.0, 2.0], [2.0, 4.0]])\nprint(res)",
    "expected_output": "None"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/8_calculate-2x2-matrix-inverse/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/8_calculate-2x2-matrix-inverse/description.md)。Deep-ML：Educational Use Only License。
