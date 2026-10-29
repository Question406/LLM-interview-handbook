---
id: drustz-fce05821ba388aa97a
section: deepml
order: 161
level: A
title: Scalar Multiplication of a Matrix
quick: Deep-ML 练习 · Scalar Multiplication of a Matrix
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/5_scalar-multiplication-of-a-matrix/description.md
    type: primary
---
### description.md

Write a Python function that multiplies a matrix by a scalar and returns the result.


### example.json

```json
{
  "input": "matrix = [[1, 2], [3, 4]], scalar = 2",
  "output": "[[2, 4], [6, 8]]",
  "reasoning": "Each element of the matrix is multiplied by the scalar."
}
```




### learn.md


## Scalar Multiplication of a Matrix

When a matrix $A$ is multiplied by a scalar $k$, the operation is defined as multiplying each element of $A$ by $k$.

Given a matrix $A$:
$$
A = \begin{pmatrix} 
a_{11} & a_{12} \\ 
a_{21} & a_{22} 
\end{pmatrix}
$$

And a scalar $k$, the result of the scalar multiplication $kA$ is:
$$
kA = \begin{pmatrix} 
ka_{11} & ka_{12} \\ 
ka_{21} & ka_{22} 
\end{pmatrix}
$$

This operation scales the matrix by $k$ without changing its dimension or the relative proportion of its elements.


### meta.json

```json
{
  "id": "5",
  "title": "Scalar Multiplication of a Matrix",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "https://youtu.be/iE2NvpvZRBk",
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


def scalar_multiply(matrix, scalar) -> torch.Tensor:
    """
    Multiply each element of a 2D matrix by a scalar using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a 2D tensor of the same shape.
    """
    m_t = torch.as_tensor(matrix, dtype=torch.float)
    return m_t * scalar
```




### starter_code.py

```python
import torch


def scalar_multiply(matrix, scalar) -> torch.Tensor:
    """
    Multiply each element of a 2D matrix by a scalar using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a 2D tensor of the same shape.
    """
    # Convert input to tensor
    m_t = torch.as_tensor(matrix, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = scalar_multiply(\n    torch.tensor([[1, 2], [3, 4]], dtype=torch.float),\n    3\n)\nprint(res.numpy().tolist())",
    "expected_output": "[[3.0, 6.0], [9.0, 12.0]]"
  },
  {
    "test": "import torch\nres = scalar_multiply(\n    torch.tensor([[1.5, 2.5], [3.0, 4.0]], dtype=torch.float),\n    2.0\n)\nprint(res.numpy().tolist())",
    "expected_output": "[[3.0, 5.0], [6.0, 8.0]]"
  }
]
```




### solution.py

```python
def scalar_multiply(
    matrix: list[list[int | float]], scalar: int | float
) -> list[list[int | float]]:
    return [[element * scalar for element in row] for row in matrix]
```




### starter_code.py

```python
def scalar_multiply(
    matrix: list[list[int | float]], scalar: int | float
) -> list[list[int | float]]:
    return result
```




### tests.json

```json
[
  {
    "test": "print(scalar_multiply([[1,2],[3,4]], 2))",
    "expected_output": "[[2, 4], [6, 8]]"
  },
  {
    "test": "print(scalar_multiply([[0,-1],[1,0]], -1))",
    "expected_output": "[[0, 1], [-1, 0]]"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor


def scalar_multiply_tg(matrix, scalar) -> Tensor:
    """
    Multiply each element of a 2D matrix by a scalar using tinygrad.
    Inputs can be Python lists, NumPy arrays, or tinygrad Tensors.
    Returns a 2D Tensor of the same shape.
    """
    m_t = Tensor(matrix)
    return m_t * scalar
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def scalar_multiply_tg(matrix, scalar) -> Tensor:
    """
    Multiply each element of a 2D matrix by a scalar using tinygrad.
    Inputs can be Python lists, NumPy arrays, or tinygrad Tensors.
    Returns a 2D Tensor of the same shape.
    """
    # Convert input to Tensor
    m_t = Tensor(matrix)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = scalar_multiply_tg(\n    [[1, 2], [3, 4]],\n    3\n)\nprint(res.numpy().tolist())",
    "expected_output": "[[3, 6], [9, 12]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = scalar_multiply_tg(\n    [[1.5, 2.5], [3.0, 4.0]],\n    2.0\n)\nprint(res.numpy().tolist())",
    "expected_output": "[[3.0, 5.0], [6.0, 8.0]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/5_scalar-multiplication-of-a-matrix/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/5_scalar-multiplication-of-a-matrix/description.md)。Deep-ML：Educational Use Only License。
