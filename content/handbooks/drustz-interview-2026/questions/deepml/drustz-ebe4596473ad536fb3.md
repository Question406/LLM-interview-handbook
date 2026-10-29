---
id: drustz-ebe4596473ad536fb3
section: deepml
order: 180
level: A
title: Transpose of a Matrix
quick: Deep-ML 练习 · Transpose of a Matrix
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/2_transpose-of-a-matrix/description.md
    type: primary
---
### description.md

Write a Python function that computes the transpose of a given matrix.


### example.json

```json
{
  "input": "a = [[1,2,3],[4,5,6]]",
  "output": "[[1,4],[2,5],[3,6]]",
  "reasoning": "The transpose of a matrix is obtained by flipping rows and columns."
}
```




### learn.md


## Transpose of a Matrix

Let's consider a matrix $M$ and its transpose $M^T$:

**Original Matrix $M$:**
$$
M = \begin{pmatrix} 
a & b & c \\ 
d & e & f 
\end{pmatrix}
$$

**Transposed Matrix $M^T$:**
$$
M^T = \begin{pmatrix} 
a & d \\ 
b & e \\ 
c & f 
\end{pmatrix}
$$

### Explanation:
Transposing a matrix involves converting its rows into columns and vice versa. This operation is fundamental in linear algebra for various computations and transformations.


### meta.json

```json
{
  "id": "2",
  "title": "Transpose of a Matrix",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "https://youtu.be/fj0ZJ2gTSmI?si=vG8VSqASjyG0eNLY",
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


def transpose_matrix(a) -> torch.Tensor:
    """
    Transpose a 2D matrix `a` using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a transposed tensor.
    """
    a_t = torch.as_tensor(a)
    return a_t.T
```




### starter_code.py

```python
import torch


def transpose_matrix(a) -> torch.Tensor:
    """
    Transpose a 2D matrix `a` using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a transposed tensor.
    """
    a_t = torch.as_tensor(a)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = transpose_matrix(torch.tensor([[1,2,3],[4,5,6]]))\nprint(res.numpy().tolist())",
    "expected_output": "[[1, 4], [2, 5], [3, 6]]"
  },
  {
    "test": "import torch\nres = transpose_matrix(torch.tensor([[1,2],[3,4]]))\nprint(res.numpy().tolist())",
    "expected_output": "[[1, 3], [2, 4]]"
  }
]
```




### solution.py

```python
def transpose_matrix(a: list[list[int | float]]) -> list[list[int | float]]:
    return [list(i) for i in zip(*a)]
```




### starter_code.py

```python
def transpose_matrix(a: list[list[int | float]]) -> list[list[int | float]]:
    return b
```




### tests.json

```json
[
  {
    "test": "print(transpose_matrix([[1,2],[3,4],[5,6]]))",
    "expected_output": "[[1, 3, 5], [2, 4, 6]]"
  },
  {
    "test": "print(transpose_matrix([[1,2,3],[4,5,6]]))",
    "expected_output": "[[1, 4], [2, 5], [3, 6]]"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor


def transpose_matrix_tg(a) -> Tensor:
    """
    Transpose a 2D matrix `a` using tinygrad.
    Inputs are tinygrad Tensors.
    Returns a transposed Tensor.
    """
    return a.T
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def transpose_matrix_tg(a: Tensor) -> Tensor:
    """
    Transpose a 2D matrix `a` using tinygrad.
    Inputs are tinygrad Tensors.
    Returns a transposed Tensor.
    """
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = transpose_matrix_tg(Tensor([[1,2,3],[4,5,6]]))\nprint(res.numpy().tolist())",
    "expected_output": "[[1, 4], [2, 5], [3, 6]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = transpose_matrix_tg(Tensor([[1,2],[3,4]]))\nprint(res.numpy().tolist())",
    "expected_output": "[[1, 3], [2, 4]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/2_transpose-of-a-matrix/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/2_transpose-of-a-matrix/description.md)。Deep-ML：Educational Use Only License。
