---
id: drustz-9c2f7cc07e8db0aa62
section: deepml
order: 170
level: A
title: Solve Linear Equations using Jacobi Method
quick: Deep-ML 练习 · Solve Linear Equations using Jacobi Method
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/11_solve-linear-equations-using-jacobi-method/description.md
    type: primary
---
### description.md

Write a Python function that uses the Jacobi method to solve a system of linear equations given by Ax = b. The function should iterate n times, rounding each intermediate solution to four decimal places, and return the approximate solution x.


### example.json

```json
{
  "input": "A = [[5, -2, 3], [-3, 9, 1], [2, -1, -7]], b = [-1, 2, 3], n=2",
  "output": "[0.146, 0.2032, -0.5175]",
  "reasoning": "The Jacobi method iteratively solves each equation for x[i] using the formula x[i] = (1/a_ii) * (b[i] - sum(a_ij * x[j] for j != i)), where a_ii is the diagonal element of A and a_ij are the off-diagonal elements."
}
```




### learn.md


## Solving Linear Equations Using the Jacobi Method

The Jacobi method is an iterative algorithm used for solving a system of linear equations \( Ax = b \). This method is particularly useful for large systems where direct methods, such as Gaussian elimination, are computationally expensive.


### Algorithm Overview

For a system of equations represented by \( Ax = b \), where \( A \) is a matrix and \( x \) and \( b \) are vectors, the Jacobi method involves the following steps:

1. **Initialization**: Start with an initial guess for \( x \).

2. **Iteration**: For each equation \( i \), update \( x[i] \) using:
   $$
   x[i] = \frac{1}{a_{ii}} \left(b[i] - \sum_{j \neq i} a_{ij} x[j]\right)
   $$
   where \( a_{ii} \) are the diagonal elements of \( A \), and \( a_{ij} \) are the off-diagonal elements.

3. **Convergence**: Repeat the iteration until the changes in \( x \) are below a certain tolerance or until a maximum number of iterations is reached.

This method assumes that all diagonal elements of \( A \) are non-zero and that the matrix is diagonally dominant or properly conditioned for convergence.

### Practical Considerations

- The method may not converge for all matrices.
- Choosing a good initial guess can improve convergence.
- Diagonal dominance of \( A \) ensures the convergence of the Jacobi method.


### meta.json

```json
{
  "id": "11",
  "title": "Solve Linear Equations using Jacobi Method",
  "difficulty": "medium",
  "category": "Linear Algebra",
  "video": "https://youtu.be/Y7WSn7K092g",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    },
    {
      "profile_link": "https://github.com/Haleshot",
      "name": "Haleshot"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch


def solve_jacobi(A, b, n) -> torch.Tensor:
    """
    Solve Ax = b using the Jacobi iterative method for n iterations.
    A: (m,m) tensor; b: (m,) tensor; n: number of iterations.
    Returns a 1-D tensor of length m, rounded to 4 decimals.
    """
    A_t = torch.as_tensor(A, dtype=torch.float)
    b_t = torch.as_tensor(b, dtype=torch.float)
    d = torch.diag(A_t)
    nda = A_t - torch.diag(d)
    x = torch.zeros_like(b_t)
    for _ in range(n):
        x = (b_t - nda.matmul(x)) / d
    return torch.round(x * 10000) / 10000
```




### starter_code.py

```python
import torch


def solve_jacobi(A, b, n) -> torch.Tensor:
    """
    Solve Ax = b using the Jacobi iterative method for n iterations.
    A: (m,m) tensor; b: (m,) tensor; n: number of iterations.
    Returns a 1-D tensor of length m, rounded to 4 decimals.
    """
    A_t = torch.as_tensor(A, dtype=torch.float)
    b_t = torch.as_tensor(b, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = solve_jacobi(\n    torch.tensor([[4.0,1.0],[2.0,3.0]]),\n    torch.tensor([1.0,2.0]),\n    10\n)\nprint(res.numpy().tolist())",
    "expected_output": "[0.1, 0.6]"
  },
  {
    "test": "import torch\nres = solve_jacobi(\n    torch.tensor([[3.0,0.0],[0.0,3.0]]),\n    torch.tensor([3.0,6.0]),\n    5\n)\nprint(res.numpy().tolist())",
    "expected_output": "[1.0, 2.0]"
  }
]
```




### solution.py

```python
import numpy as np


def solve_jacobi(A: np.ndarray, b: np.ndarray, n: int) -> list:
    d_a = np.diag(A)
    nda = A - np.diag(d_a)
    x = np.zeros(len(b))
    x_hold = np.zeros(len(b))
    for _ in range(n):
        for i in range(len(A)):
            x_hold[i] = (1 / d_a[i]) * (b[i] - sum(nda[i] * x))
        x = x_hold.copy()
    return np.round(x, 4).tolist()
```




### starter_code.py

```python
import numpy as np


def solve_jacobi(A: np.ndarray, b: np.ndarray, n: int) -> list:
    return x
```




### tests.json

```json
[
  {
    "test": "print(solve_jacobi(np.array([[5, -2, 3], [-3, 9, 1], [2, -1, -7]]), np.array([-1, 2, 3]),2))",
    "expected_output": "[0.146, 0.2032, -0.5175]"
  },
  {
    "test": "print(solve_jacobi(np.array([[4, 1, 2], [1, 5, 1], [2, 1, 3]]), np.array([4, 6, 7]),5))",
    "expected_output": "[-0.0806, 0.9324, 2.4422]"
  },
  {
    "test": "print(solve_jacobi(np.array([[4,2,-2],[1,-3,-1],[3,-1,4]]), np.array([0,7,5]),3))",
    "expected_output": "[1.7083, -1.9583, -0.7812]"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def solve_jacobi_tg(A, b, n) -> Tensor:
    """
    Solve Ax = b using the Jacobi iterative method for n iterations in tinygrad.
    A: list of lists or Tensor; b: list or Tensor; n: number of iterations.
    Returns a 1-D Tensor of length m, rounded to 4 decimals.
    """
    A_t = Tensor(A).float()
    b_t = Tensor(b).float()
    m = A_t.shape[0]
    # extract diagonal
    d_list = [A_t[i, i] for i in range(m)]
    d = Tensor(d_list)
    # build remainder matrix
    nda_list = [[A_t[i, j] if i != j else 0 for j in range(m)] for i in range(m)]
    nda = Tensor(nda_list).float()
    x = Tensor([0.0] * m).float()
    for _ in range(n):
        x = (b_t - nda.matmul(x)) / d
    res = x.numpy()
    return Tensor(np.round(res, 4))
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def solve_jacobi_tg(A, b, n) -> Tensor:
    """
    Solve Ax = b using the Jacobi iterative method for n iterations in tinygrad.
    A: list of lists or Tensor; b: list or Tensor; n: number of iterations.
    Returns a 1-D Tensor of length m, rounded to 4 decimals.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = solve_jacobi_tg(\n    [[4.0,1.0],[2.0,3.0]],\n    [1.0,2.0],\n    10\n)\nprint(res.numpy().tolist())",
    "expected_output": "[0.1, 0.6]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = solve_jacobi_tg(\n    [[3.0,0.0],[0.0,3.0]],\n    [3.0,6.0],\n    5\n)\nprint(res.numpy().tolist())",
    "expected_output": "[1.0, 2.0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/11_solve-linear-equations-using-jacobi-method/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/11_solve-linear-equations-using-jacobi-method/description.md)。Deep-ML：Educational Use Only License。
