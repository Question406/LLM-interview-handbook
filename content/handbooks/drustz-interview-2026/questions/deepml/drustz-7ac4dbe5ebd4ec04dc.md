---
id: drustz-7ac4dbe5ebd4ec04dc
section: deepml
order: 142
level: A
title: Matrix-Vector Dot Product
quick: Deep-ML 练习 · Matrix-Vector Dot Product
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/1_matrix-vector-dot-product/description.md
    type: primary
---
### description.md

Write a Python function that computes the dot product of a matrix and a vector. The function should return a list representing the resulting vector if the operation is valid, or -1 if the matrix and vector dimensions are incompatible. A matrix (a list of lists) can be dotted with a vector (a list) only if the number of columns in the matrix equals the length of the vector. For example, an n x m matrix requires a vector of length m.


### example.json

```json
{
  "input": "a = [[1, 2], [2, 4]], b = [1, 2]",
  "output": "[5, 10]",
  "reasoning": "Row 1: (1 * 1) + (2 * 2) = 1 + 4 = 5; Row 2: (1 * 2) + (2 * 4) = 2 + 8 = 10"
}
```




### learn.md


## Matrix-Vector Dot Product

Consider a matrix $A$ and a vector $v$:

**Matrix $A$ (n x m):**
$$
A = \begin{pmatrix}
a_{11} & a_{12} & \cdots & a_{1m} \\
a_{21} & a_{22} & \cdots & a_{2m} \\
\vdots & \vdots & \ddots & \vdots \\
a_{n1} & a_{n2} & \cdots & a_{nm}
\end{pmatrix}
$$

**Vector $v$ (length m):**
$$
v = \begin{pmatrix}
v_1 \\
v_2 \\
\vdots \\
v_m
\end{pmatrix}
$$

The dot product $A \cdot v$ produces a new vector of length $n$:
$$
A \cdot v = \begin{pmatrix}
a_{11}v_1 + a_{12}v_2 + \cdots + a_{1m}v_m \\
a_{21}v_1 + a_{22}v_2 + \cdots + a_{2m}v_m \\
\vdots \\
a_{n1}v_1 + a_{n2}v_2 + \cdots + a_{nm}v_m
\end{pmatrix}
$$

### Key Requirement:
The number of columns in the matrix ($m$) must equal the length of the vector ($m$). If not, the operation is undefined, and the function should return -1.


### meta.json

```json
{
  "id": "1",
  "title": "Matrix-Vector Dot Product",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "https://youtu.be/DNoLs5tTGAw?si=vpkPobZMA8YY10WY",
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


def matrix_dot_vector(a, b) -> torch.Tensor:
    """
    Compute the product of matrix `a` and vector `b` using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a 1-D tensor of length m, or tensor(-1) if dimensions mismatch.
    """
    a_t = torch.as_tensor(a, dtype=torch.float)
    b_t = torch.as_tensor(b, dtype=torch.float)
    if a_t.size(1) != b_t.size(0):
        return torch.tensor(-1)
    return torch.matmul(a_t, b_t)
```




### starter_code.py

```python
import torch


def matrix_dot_vector(a, b) -> torch.Tensor:
    """
    Compute the product of matrix `a` and vector `b` using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a 1-D tensor of length m, or tensor(-1) if dimensions mismatch.
    """
    a_t = torch.as_tensor(a, dtype=torch.float)
    b_t = torch.as_tensor(b, dtype=torch.float)
    # Dimension mismatch check
    if a_t.size(1) != b_t.size(0):
        return torch.tensor(-1)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = matrix_dot_vector(\n    torch.tensor([[1,2,3],[2,4,5],[6,8,9]], dtype=torch.float),\n    torch.tensor([1,2,3], dtype=torch.float)\n)\nprint(res.numpy().tolist())",
    "expected_output": "[14.0, 25.0, 49.0]"
  },
  {
    "test": "import torch\nres = matrix_dot_vector(\n    torch.tensor([[1,2,3],[2,4,5]], dtype=torch.float),\n    torch.tensor([1,2], dtype=torch.float)\n)\nprint(res.numpy().tolist())",
    "expected_output": "-1"
  }
]
```




### solution.py

```python
def matrix_dot_vector(
    a: list[list[int | float]], b: list[int | float]
) -> list[int | float]:
    if len(a[0]) != len(b):
        return -1
    result = []
    for row in a:
        total = 0
        for i in range(len(row)):
            total += row[i] * b[i]
        result.append(total)
    return result
```




### starter_code.py

```python
def matrix_dot_vector(
    a: list[list[int | float]], b: list[int | float]
) -> list[int | float]:
    # Return a list where each element is the dot product of a row of 'a' with 'b'.
    # If the number of columns in 'a' does not match the length of 'b', return -1.
    pass
```




### tests.json

```json
[
  {
    "test": "print(matrix_dot_vector([[1, 2, 3], [2, 4, 5], [6, 8, 9]], [1, 2, 3]))",
    "expected_output": "[14, 25, 49]"
  },
  {
    "test": "print(matrix_dot_vector([[1, 2], [2, 4], [6, 8], [12, 4]], [1, 2, 3]))",
    "expected_output": "-1"
  },
  {
    "test": "print(matrix_dot_vector([[1.5, 2.5], [3.0, 4.0]], [2, 1]))",
    "expected_output": "[5.5, 10.0]"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor


def matrix_dot_vector_tg(a: Tensor, b: Tensor) -> Tensor:
    """
    Compute the product of matrix `a` and vector `b` using tinygrad.
    Inputs will be tinygrad Tensors.
    Returns a 1-D Tensor of length m, or Tensor(-1) if dimensions mismatch.
    """
    if len(a[0]) != len(b):
        return Tensor(-1)
    return a @ b
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def matrix_dot_vector_tg(a: Tensor, b: Tensor) -> Tensor:
    """
    Compute the product of matrix `a` and vector `b` using tinygrad.
    Will be tinygrad Tensors.
    Returns a 1-D Tensor of length m, or Tensor(-1) if dimensions mismatch.
    """
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = matrix_dot_vector_tg(\n    Tensor([[1,2,3],[2,4,5],[6,8,9]]),\n    Tensor([1,2,3])\n)\nprint(res.numpy().tolist())",
    "expected_output": "[14.0, 25.0, 49.0]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = matrix_dot_vector_tg(\n    Tensor([[1,2,3],[2,4,5]]),\n    Tensor([1,2])\n)\nprint(res.numpy().tolist())",
    "expected_output": "-1"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = matrix_dot_vector_tg(\n    Tensor([[1, 2], [2, 4]]),\n    Tensor([1, 2])\n)\nprint(res.numpy().tolist())",
    "expected_output": "[5, 10]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/1_matrix-vector-dot-product/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/1_matrix-vector-dot-product/description.md)。Deep-ML：Educational Use Only License。
