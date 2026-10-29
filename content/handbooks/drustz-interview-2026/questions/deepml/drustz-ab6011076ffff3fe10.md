---
id: drustz-ab6011076ffff3fe10
section: deepml
order: 72
level: A
title: Gaussian Elimination for Solving Linear Systems
quick: Deep-ML 练习 · Gaussian Elimination for Solving Linear Systems
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/58_gaussian-elimination-for-solving-linear-systems/description.md
    type: primary
---
### description.md

## Task: Implement the Gaussian Elimination Method

Your task is to implement the Gaussian Elimination method, which transforms a system of linear equations into an upper triangular matrix. This method can then be used to solve for the variables using backward substitution.

Write a function `gaussian_elimination(A, b)` that performs Gaussian Elimination with partial pivoting to solve the system \(Ax = b\).

The function should return the solution vector \(x\).

    


### example.json

```json
{
  "input": "A = np.array([[2,8,4], [2,5,1], [4,10,-1]], dtype=float)\nb = np.array([2,5,1], dtype=float)\n\nprint(gaussian_elimination(A, b))",
  "output": "[11.0, -4.0, 3.0]",
  "reasoning": "The Gaussian Elimination method transforms the system of equations into an upper triangular matrix and then uses backward substitution to solve for the variables."
}
```




### learn.md


## Understanding Gaussian Elimination

Gaussian Elimination is used to replace matrix coefficients with a row-echelon form matrix, which can be more easily solved via backwards substitution.

### Row-Echelon Form Criteria

- **Non-zero rows** are above any rows of all zeros.
- The **leading entry** of each non-zero row is to the right of the leading entry of the previous row.
- The **leading entry** in any non-zero row is 1, and all entries below it in the same column are zeros.

### Augmented Matrix

For a linear system $Ax = b$, an augmented matrix is a way of displaying all the numerical information in a linear system in a single matrix. This combines the coefficient matrix $A$ and vector source $b$ as follows:

$$
\begin{pmatrix} 
a_{11} & a_{21} & a_{31} & b_1\\ 
a_{12} & a_{22} & a_{32} & b_2\\ 
a_{31} & a_{32} & a_{33} & b_3 
\end{pmatrix}
$$

### Partial Pivoting

In linear algebra, diagonal elements of a matrix are referred to as the "pivot". To solve a linear system, the diagonal is used as a divisor for other elements within the matrix. This means that Gaussian Elimination will fail if there is a zero pivot.

In this case, pivoting is used to interchange rows, ensuring a non-zero pivot. Specifically, **partial pivoting** looks at all other rows in the current column to find the row with the highest absolute value. This row is then interchanged with the current row. This not only increases the numerical stability of the solution, but also reduces round-off errors caused by dividing by small entries.

### Gaussian Elimination Mathematical Formulation

**Gaussian Elimination:**

- For $k = 1$ to $ \text{number of rows} - 1$:
  - Apply partial pivoting to the current row.
  - For $i = k + 1$ to $ \text{number of rows}$:
    - $ m_{ik} = \frac{a_{ik}}{a_{kk}} $
    - For $j = k$ to $ \text{number of columns}$:
      - $ a_{ij} = a_{ij} - m_{ik} \times a_{kj} $
    - $ b_i = b_i - m_{ik} \times b_k $

**Backwards Substitution:**

- For $k = \text{number of rows}$ to $1$:
  - For $i = \text{number of columns} - 1$ to $1$:
    - $ b_k = b_k - a_{ki} \times b_i $
  - $ b_k = \frac{b_k}{a_{kk}} $

### Example Calculation

Let’s solve the system of equations:

$$
A = \begin{pmatrix} 
2 & 8 & 4\\ 
5 & 5 & 1 \\ 
4 & 10 & -1 
\end{pmatrix} 
\quad \text{and} \quad 
b = \begin{pmatrix} 
2 \\ 5 \\ 1 
\end{pmatrix} 
$$

1. Apply **partial pivoting** to increase the magnitude of the pivot. For $A_{11}$, calculate the factor for the elimination of $A_{12}$: 

$$ 
m_{12} = \frac{A_{12}}{A_{11}} = \frac{2}{5} = 0.4 
$$

2. Apply this scaling to row 1 and subtract this from row 2, eliminating $A_{12}$:

$$
A = \begin{pmatrix} 
5 & 5 & 1 \\ 
0 & 6 & 3.6 \\ 
4 & 10 & -1 
\end{pmatrix} 
\quad \text{and} \quad 
b = \begin{pmatrix} 
5 \\ 0 \\ 1 
\end{pmatrix} 
$$

After the full **Gaussian Elimination** process has been applied to $A$ and $b$, we get the following:

$$
A = \begin{pmatrix} 
5 & 5 & 1\\ 
0 & 6 & 3.6 \\ 
0 & 0 & -5.4 
\end{pmatrix} 
\quad \text{and} \quad 
b = \begin{pmatrix} 
5 \\ 0 \\ 3 
\end{pmatrix} 
$$

To calculate $x$, we apply **backward substitution** by substituting in the currently solved values and dividing by the pivot. This gives the following for the first iteration:

$$ 
x_3 = \frac{b_3}{A_{33}} = \frac{3}{-5.4} = -0.56 
$$

This process can be repeated iteratively for all rows to solve the linear system, substituting in the solved values for the rows below.

### Applications

Gaussian Elimination and linear solvers have a wide range of real-world applications, including their use in:

- Machine learning
- Computational fluid dynamics
- 3D graphics


### meta.json

```json
{
  "id": "58",
  "title": "Gaussian Elimination for Solving Linear Systems",
  "difficulty": "medium",
  "category": "Linear Algebra",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/paddywardle",
      "name": "paddywardle"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def partial_pivoting(A_aug, row_num, col_num):
    rows, cols = A_aug.shape
    max_row = row_num
    max_val = abs(A_aug[row_num, col_num])
    for i in range(row_num, rows):
        current_val = abs(A_aug[i, col_num])
        if current_val > max_val:
            max_val = current_val
            max_row = i
    if max_row != row_num:
        A_aug[[row_num, max_row]] = A_aug[[max_row, row_num]]
    return A_aug


def gaussian_elimination(A, b):
    rows, cols = A.shape
    A_aug = np.hstack((A, b.reshape(-1, 1)))

    for i in range(rows - 1):
        A_aug = partial_pivoting(A_aug, i, i)
        for j in range(i + 1, rows):
            A_aug[j, i:] -= (A_aug[j, i] / A_aug[i, i]) * A_aug[i, i:]

    x = np.zeros_like(b, dtype=float)
    for i in range(rows - 1, -1, -1):
        x[i] = (A_aug[i, -1] - np.dot(A_aug[i, i + 1 : cols], x[i + 1 :])) / A_aug[i, i]
    return x
```




### starter_code.py

```python
import numpy as np


def gaussian_elimination(A, b):
    """
    Solves the system Ax = b using Gaussian Elimination with partial pivoting.

    :param A: Coefficient matrix
    :param b: Right-hand side vector
    :return: Solution vector x
    """
    return np.zeros_like(b)
```




### tests.json

```json
[
  {
    "test": "import numpy as np\n\nA = np.array([[2,8,4], [2,5,1], [4,10,-1]], dtype=float)\nb = np.array([2,5,1], dtype=float)\nprint(gaussian_elimination(A, b))",
    "expected_output": "[11.0, -4.0, 3.0]"
  },
  {
    "test": "import numpy as np\n\nA = np.array([\n    [0, 2, 1, 0, 0, 0, 0],\n    [2, 6, 2, 1, 0, 0, 0],\n    [1, 2, 7, 2, 1, 0, 0],\n    [0, 1, 2, 8, 2, 1, 0],\n    [0, 0, 1, 2, 9, 2, 1],\n    [0, 0, 0, 1, 2, 10, 2],\n    [0, 0, 0, 0, 1, 2, 11]\n], dtype=float)\nb = np.array([1, 2, 3, 4, 5, 6, 7], dtype=float)\nprint(gaussian_elimination(A, b))",
    "expected_output": "[-0.4894027,   0.36169985,  0.2766003,   0.25540569,  0.31898951,  0.40387497, 0.53393278]"
  },
  {
    "test": "import numpy as np\n\nA = np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], dtype=float)\nb = np.array([8, -11, -3], dtype=float)\nprint(gaussian_elimination(A, b))",
    "expected_output": "[2.0, 3.0, -1.0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/58_gaussian-elimination-for-solving-linear-systems/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/58_gaussian-elimination-for-solving-linear-systems/description.md)。Deep-ML：Educational Use Only License。
