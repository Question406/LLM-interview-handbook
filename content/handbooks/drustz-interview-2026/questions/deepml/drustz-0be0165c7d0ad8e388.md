---
id: drustz-0be0165c7d0ad8e388
section: deepml
order: 20
level: A
title: Calculate Eigenvalues of a Matrix
quick: Deep-ML 练习 · Calculate Eigenvalues of a Matrix
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/6_calculate-eigenvalues-of-a-matrix/description.md
    type: primary
---
### description.md

Write a Python function that calculates the eigenvalues of a 2x2 matrix. The function should return a list containing the eigenvalues, sort values from highest to lowest.


### example.json

```json
{
  "input": "matrix = [[2, 1], [1, 2]]",
  "output": "[3.0, 1.0]",
  "reasoning": "The eigenvalues of the matrix are calculated using the characteristic equation of the matrix, which for a 2x2 matrix is $\\lambda^2 - \ttrace(A)\\lambda + \tdet(A) = 0$, where $\\lambda$ are the eigenvalues."
}
```




### learn.md


## Calculate Eigenvalues

Eigenvalues of a matrix offer significant insight into the matrix's behavior, particularly in the context of linear transformations and systems of linear equations.

### Definition
For a square matrix $A$, eigenvalues are scalars $\lambda$ that satisfy the equation for some non-zero vector $v$ (eigenvector):
$$
Av = \lambda v
$$

### Calculation for a 2x2 Matrix
The eigenvalues of a 2x2 matrix $A$, given by:
$$
A = \begin{pmatrix} 
a & b \\ 
c & d 
\end{pmatrix}
$$
are determined by solving the characteristic equation:
$$
\det(A - \lambda I) = 0
$$

This simplifies to a quadratic equation:
$$
\lambda^2 - \text{tr}(A) \lambda + \det(A) = 0
$$

Here, the trace of $A$, denoted as $\text{tr}(A)$, is $a + d$, and the determinant of $A$, denoted as $\det(A)$, is $ad - bc$. Solving this equation yields the eigenvalues, $\lambda$.

### Significance
Understanding eigenvalues is essential for analyzing the effects of linear transformations represented by the matrix. They are crucial in various applications, including stability analysis, vibration analysis, and Principal Component Analysis (PCA) in machine learning.


### meta.json

```json
{
  "id": "6",
  "title": "Calculate Eigenvalues of a Matrix",
  "difficulty": "medium",
  "category": "Linear Algebra",
  "video": "https://youtu.be/AMCFzIaHc4Y",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ],
  "tinygrad_difficulty": "easy",
  "pytorch_difficulty": "easy",
  "marimo_link": ""
}
```




### solution.py

```python
import torch


def calculate_eigenvalues(matrix: torch.Tensor) -> torch.Tensor:
    """
    Compute eigenvalues of a 2×2 matrix using PyTorch.
    Input: 2×2 tensor; Output: 1-D tensor with the two eigenvalues in ascending order.
    """
    a = matrix[0, 0]
    b = matrix[0, 1]
    c = matrix[1, 0]
    d = matrix[1, 1]
    trace = a + d
    det = a * d - b * c
    disc = trace * trace - 4 * det
    sqrt_disc = torch.sqrt(disc)
    lambda1 = (trace + sqrt_disc) / 2
    lambda2 = (trace - sqrt_disc) / 2
    eig = torch.stack([lambda1, lambda2])
    return torch.sort(eig).values
```




### starter_code.py

```python
import torch


def calculate_eigenvalues(matrix: torch.Tensor) -> torch.Tensor:
    """
    Compute eigenvalues of a 2×2 matrix using PyTorch.
    Input: 2×2 tensor; Output: 1-D tensor with the two eigenvalues in ascending order.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = calculate_eigenvalues(torch.tensor([[2.0,0.0],[0.0,3.0]]))\nprint(res.detach().numpy().tolist())",
    "expected_output": "[2.0, 3.0]"
  },
  {
    "test": "import torch\nres = calculate_eigenvalues(torch.tensor([[0.0,1.0],[1.0,0.0]]))\nprint(res.detach().numpy().tolist())",
    "expected_output": "[-1.0, 1.0]"
  },
  {
    "test": "import torch\nres = calculate_eigenvalues(torch.tensor([[4.0,2.0],[1.0,3.0]]))\nprint(res.detach().numpy().tolist())",
    "expected_output": "[2.0, 5.0]"
  }
]
```




### solution.py

```python
def calculate_eigenvalues(matrix: list[list[float]]) -> list[float]:
    a, b, c, d = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
    trace = a + d
    determinant = a * d - b * c
    # Calculate the discriminant of the quadratic equation
    discriminant = trace**2 - 4 * determinant
    # Solve for eigenvalues
    lambda_1 = (trace + discriminant**0.5) / 2
    lambda_2 = (trace - discriminant**0.5) / 2
    return [lambda_1, lambda_2]
```




### starter_code.py

```python
def calculate_eigenvalues(matrix: list[list[float | int]]) -> list[float]:
    return eigenvalues
```




### tests.json

```json
[
  {
    "test": "print(calculate_eigenvalues([[2, 1], [1, 2]]))",
    "expected_output": "[3.0, 1.0]"
  },
  {
    "test": "print(calculate_eigenvalues([[4, -2], [1, 1]]))",
    "expected_output": "[3.0, 2.0]"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor


def calculate_eigenvalues_tg(matrix) -> Tensor:
    """
    Compute eigenvalues of a 2×2 matrix using tinygrad.
    Input: 2×2 list, NumPy array, or Tensor; Output: 1-D Tensor with eigenvalues in ascending order.
    """
    m = Tensor(matrix).float()
    a = m[0, 0]
    b = m[0, 1]
    c = m[1, 0]
    d = m[1, 1]
    trace = a + d
    det = a * d - b * c
    disc = trace * trace - 4 * det
    sqrt_disc = disc.pow(0.5)
    lambda1 = (trace + sqrt_disc) / 2
    lambda2 = (trace - sqrt_disc) / 2
    vals = sorted([lambda1.numpy(), lambda2.numpy()])
    return Tensor(vals)
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def calculate_eigenvalues_tg(matrix) -> Tensor:
    """
    Compute eigenvalues of a 2×2 matrix using tinygrad.
    Input: 2×2 list, NumPy array, or Tensor; Output: 1-D Tensor with eigenvalues in ascending order.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = calculate_eigenvalues_tg([[2.0,0.0],[0.0,3.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[2.0, 3.0]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = calculate_eigenvalues_tg([[0.0,1.0],[1.0,0.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[-1.0, 1.0]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = calculate_eigenvalues_tg([[4.0,2.0],[1.0,3.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[2.0, 5.0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/6_calculate-eigenvalues-of-a-matrix/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/6_calculate-eigenvalues-of-a-matrix/description.md)。Deep-ML：Educational Use Only License。
