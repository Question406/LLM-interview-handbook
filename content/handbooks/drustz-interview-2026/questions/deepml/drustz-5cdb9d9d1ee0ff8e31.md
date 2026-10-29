---
id: drustz-5cdb9d9d1ee0ff8e31
section: deepml
order: 57
level: A
title: Determinant of a 4x4 Matrix using Laplace's Expansion (hard)
quick: Deep-ML 练习 · Determinant of a 4x4 Matrix using Laplace's Expansion (hard)
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/13_determinant-of-a-4x4-matrix-using-laplace-s-expans/description.md
    type: primary
---
### description.md

Write a Python function that calculates the determinant of a 4x4 matrix using Laplace's Expansion method. The function should take a single argument, a 4x4 matrix represented as a list of lists, and return the determinant of the matrix. The elements of the matrix can be integers or floating-point numbers. Implement the function recursively to handle the computation of determinants for the 3x3 minor matrices.


### example.json

```json
{
  "input": "a = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]",
  "output": "0",
  "reasoning": "Using Laplace's Expansion, the determinant of a 4x4 matrix is calculated by expanding it into minors and cofactors along any row or column. Given the symmetrical and linear nature of this specific matrix, its determinant is 0. The calculation for a generic 4x4 matrix involves more complex steps, breaking it down into the determinants of 3x3 matrices."
}
```




### learn.md


## Determinant of a 4x4 Matrix using Laplace's Expansion

Laplace's Expansion, also known as cofactor expansion, is a method to calculate the determinant of a square matrix of any size. For a 4x4 matrix \( A \), this method involves expanding \( A \) into minors and cofactors along a chosen row or column.

Consider a 4x4 matrix \( A \):
$$
A = \begin{pmatrix}
a_{11} & a_{12} & a_{13} & a_{14} \\
a_{21} & a_{22} & a_{23} & a_{24} \\
a_{31} & a_{32} & a_{33} & a_{34} \\
a_{41} & a_{42} & a_{43} & a_{44}
\end{pmatrix}
$$

The determinant of \( A \), \( \det(A) \), can be calculated by selecting any row or column (e.g., the first row) and using the formula that involves the elements of that row (or column), their corresponding cofactors, and the determinants of the 3x3 minor matrices obtained by removing the row and column of each element. This process is recursive, as calculating the determinants of the 3x3 matrices involves further expansions.

The expansion formula for the first row is:
$$
\det(A) = a_{11}C_{11} - a_{12}C_{12} + a_{13}C_{13} - a_{14}C_{14}
$$

### Explanation of Terms
- **Cofactor \( C_{ij} \)**: The cofactor of element \( a_{ij} \) is given by:
  $$
  C_{ij} = (-1)^{i+j} \det(\text{Minor of } a_{ij})
  $$
  where the minor of \( a_{ij} \) is the determinant of the 3x3 matrix obtained by removing the \( i \)th row and \( j \)th column from \( A \).

### Notes
- The choice of row or column for expansion can be based on convenience, often selecting one with the most zeros to simplify calculations.
- The process is recursive, breaking down the determinant calculation into smaller 3x3 determinants until reaching 2x2 determinants, which are simpler to compute.

This method is fundamental in linear algebra and provides a systematic approach for determinant calculation, especially for matrices larger than 3x3.


### meta.json

```json
{
  "id": "13",
  "title": "Determinant of a 4x4 Matrix using Laplace's Expansion (hard)",
  "difficulty": "hard",
  "category": "Linear Algebra",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ],
  "tinygrad_difficulty": "easy",
  "pytorch_difficulty": "easy"
}
```




### solution.py

```python
import torch


def determinant_4x4(matrix) -> float:
    """
    Compute the determinant of a 4×4 matrix using PyTorch.
    Input can be a Python list, NumPy array, or torch Tensor of shape (4,4).
    Returns a Python float.
    """
    m = torch.as_tensor(matrix, dtype=torch.float)
    # use built-in determinant
    return torch.linalg.det(m).item()
```




### starter_code.py

```python
import torch


def determinant_4x4(matrix) -> float:
    """
    Compute the determinant of a 4×4 matrix using PyTorch.
    Input can be a Python list, NumPy array, or torch Tensor of shape (4,4).
    Returns a Python float.
    """
    # Convert to tensor
    m = torch.as_tensor(matrix, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nprint(determinant_4x4(torch.eye(4)))",
    "expected_output": "1.0"
  },
  {
    "test": "import torch\nprint(determinant_4x4(torch.diag(torch.tensor([2.0,3.0,4.0,5.0]))))",
    "expected_output": "120.0"
  },
  {
    "test": "import torch\nm = torch.tensor([[1.0,2.0,3.0,4.0],[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0],[9.0,10.0,11.0,12.0]])\nprint(determinant_4x4(m))",
    "expected_output": "0.0"
  }
]
```




### solution.py

```python
def determinant_4x4(matrix: list[list[int | float]]) -> float:
    # Base case: If the matrix is 1x1, return its single element
    if len(matrix) == 1:
        return matrix[0][0]
    # Recursive case: Calculate determinant using Laplace's Expansion
    det = 0
    for c in range(len(matrix)):
        minor = [row[:c] + row[c + 1 :] for row in matrix[1:]]  # Remove column c
        cofactor = ((-1) ** c) * determinant_4x4(minor)  # Compute cofactor
        det += matrix[0][c] * cofactor  # Add to running total
    return det
```




### starter_code.py

```python
def determinant_4x4(matrix: list[list[int | float]]) -> float:
    # Your recursive implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "print(determinant_4x4([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]))",
    "expected_output": "0"
  },
  {
    "test": "print(determinant_4x4([[4, 3, 2, 1], [3, 2, 1, 4], [2, 1, 4, 3], [1, 4, 3, 2]]))",
    "expected_output": "-160"
  },
  {
    "test": "print(determinant_4x4([[0, 1, 2, 3], [1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]))",
    "expected_output": "0"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def determinant_4x4_tg(matrix) -> Tensor:
    """
    Compute the determinant of a 4×4 matrix using tinygrad.
    Input can be a Python list, NumPy array, or tinygrad Tensor of shape (4,4).
    Returns a 0-D Tensor containing the determinant.
    """
    # convert to NumPy array
    if isinstance(matrix, Tensor):
        arr = matrix.numpy()
    else:
        arr = np.array(matrix, dtype=float)
    det = float(np.linalg.det(arr))
    return Tensor(det)
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def determinant_4x4_tg(matrix) -> Tensor:
    """
    Compute the determinant of a 4×4 matrix using tinygrad.
    Input can be a Python list, NumPy array, or tinygrad Tensor of shape (4,4).
    Returns a 0-D Tensor containing the determinant.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nprint(determinant_4x4_tg(Tensor(np.eye(4))).numpy().item())",
    "expected_output": "1.0"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nprint(determinant_4x4_tg([[2.0,0,0,0],[0,3.0,0,0],[0,0,4.0,0],[0,0,0,5.0]]).numpy().item())",
    "expected_output": "120.0"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nm = [[1.0,2.0,3.0,4.0],[1.0,2.0,3.0,4.0],[5.0,6.0,7.0,8.0],[9.0,10.0,11.0,12.0]]\nprint(determinant_4x4_tg(Tensor(m)).numpy().item())",
    "expected_output": "0.0"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/13_determinant-of-a-4x4-matrix-using-laplace-s-expans/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/13_determinant-of-a-4x4-matrix-using-laplace-s-expans/description.md)。Deep-ML：Educational Use Only License。
