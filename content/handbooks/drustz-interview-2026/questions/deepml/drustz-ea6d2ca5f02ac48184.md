---
id: drustz-ea6d2ca5f02ac48184
section: deepml
order: 168
level: A
title: Singular Value Decomposition (SVD)
quick: Deep-ML 练习 · Singular Value Decomposition (SVD)
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/12_singular-value-decomposition-svd/description.md
    type: primary
---
### description.md

Write a Python function called svd_2x2_singular_values(A) that finds an approximate singular value decomposition of a real 2 x 2 matrix using one Jacobi rotation.
Input
A: a NumPy array of shape (2, 2)

Rules
You may use basic NumPy operations (matrix multiplication, transpose, element wise math, etc.).
Do not call numpy.linalg.svd or any other high-level SVD routine.
Stick to a single Jacobi step no iterative refinements.

Return
A tuple (U, Σ,  $V_T$ ) where
U is a 2 x 2 orthogonal matrix,
Σ is a length 2 NumPy array containing the singular values, and
 $V_T$  is the transpose of the right-singular-vector matrix V.


### example.json

```json
{
  "input": "a = [[2, 1], [1, 2]]",
  "output": "(array([[-0.70710678, -0.70710678],\n                        [-0.70710678,  0.70710678]]),\n        array([3., 1.]),\n        array([[-0.70710678, -0.70710678],\n               [-0.70710678,  0.70710678]]))",
  "reasoning": "U is the first matrix sigma is the second vector and V is the third matrix"
}
```




### learn.md

## Learn Section — Deriving an SVD for a 2 x 2 Matrix

The singular-value decomposition (SVD) rewrites any real matrix $A\!\in\!\mathbb R^{m\times n}$ as

$$
A \;=\; U\,\Sigma\,V^{\!\top},
$$

where

- $U\!\in\!\mathbb R^{m\times m}$ and $V\!\in\!\mathbb R^{n\times n}$ are **orthogonal** ($U^{\!\top}U=I$ and $V^{\!\top}V=I$),
- $\Sigma$ is diagonal with **non-negative** entries $\sigma_1\ge\sigma_2\ge\cdots$ called **singular values**.

When $A$ is $2\times2$ the factorisation can be produced **analytically** with only one Givens (Jacobi) rotation.  
Below we walk through the math used in the `svd_2x2_singular_values` function.

---

### 1. From $A$ to a Symmetric Matrix

Because  
$$
A^{\!\top}A \;=\; V\,\Sigma^{\!\top}\Sigma\,V^{\!\top}
$$
is symmetric and positive-semidefinite, its eigenvectors form the right-singular vectors of $A$ and its eigenvalues are the squares of the singular values.

For a $2\times2$ matrix

$$
A \;=\; \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix},
\quad
A^{\!\top}A \;=\;
\begin{bmatrix}
a_{11}^2 + a_{21}^2 & a_{11}a_{12}+a_{21}a_{22}\\[4pt]
a_{11}a_{12}+a_{21}a_{22} & a_{12}^2 + a_{22}^2
\end{bmatrix}\!,
$$

which we label $B$ in the code (`a_2`).

---

### 2. A Single Jacobi Rotation

To diagonalise $B$ we seek a rotation matrix

$$
R(\theta)=
\begin{bmatrix}
\cos\theta & -\sin\theta\\
\sin\theta & \phantom{-}\cos\theta
\end{bmatrix},
$$

such that $R^{\!\top}BR$ is diagonal.

For $2\times2$ Jacobi iterations the optimal angle is

$$
\theta \;=\;
\begin{cases}
\dfrac{\pi}{4}, & B_{11}=B_{22},\\[8pt]
\dfrac12\,\arctan\!\bigl(\dfrac{2B_{12}}{B_{11}-B_{22}}\bigr), & \text{otherwise}.
\end{cases}
$$

The function computes this `theta`, builds $R$, and updates

$$
D \;=\; R^{\!\top}BR
$$

which now satisfies $D_{12}=D_{21}=0$.

Because we only need *one* rotation to zero the off-diagonal term, the loop runs exactly once.

---

### 3. Extracting Singular Values

The diagonal entries of $D$ are the **eigenvalues** $\lambda_1,\lambda_2$ of $B$.  
Singular values are their square-roots:

$$
\sigma_1 = \sqrt{\lambda_1}, \quad
\sigma_2 = \sqrt{\lambda_2},
\quad
\sigma_1\ge\sigma_2\ge 0.
$$

In code:

```python
s = np.sqrt([d[0, 0], d[1, 1]])
```



---

### 4. Building $U$

Given $V = R$ (or $V=VR$ after several rotations), the left-singular vectors are

$$
U \;=\; A\,V\,\Sigma^{-1},
$$

where $\Sigma^{-1}=\operatorname{diag}\!\bigl(\tfrac1{\sigma_1},\tfrac1{\sigma_2}\bigr)$.

The multiplication `a @ v @ s_inv` yields an orthogonal $U$.

---

### 5. Putting It All Together

The function finally returns the triple $(U,\; \sigma,\; V^{\!\top})$, giving the exact SVD of $A$:

```python
return (u, s, v.T)
```



---

### Why This Works

* **Eigen-trick** - Diagonalising $A^{\!\top}A$ exposes singular values.  
* **Jacobi rotation** - For $2\times2$ a **single** rotation nulls the off-diagonal term.  
* **Orthonormality** - Both $R$ and $U$ are orthogonal, preserving lengths and angles.

This compact derivation is highly instructive: it shows how SVD generalises *rotation + scaling* in $\mathbb R^2$ and illustrates numerically stable ways to compute the decomposition without heavy linear-algebra libraries.


### meta.json

```json
{
  "id": "12",
  "title": "Singular Value Decomposition (SVD)",
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
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch


def svd_2x2_singular_values(
    A: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Approximate the SVD of a 2×2 matrix A using one Jacobi rotation.
    Returns (U, S, Vt) where S is a 1-D tensor of singular values.
    """
    # compute AᵀA
    a2 = A.transpose(0, 1) @ A
    # initialize V
    V = torch.eye(2, dtype=A.dtype, device=A.device)
    # Jacobi rotation angle
    if torch.isclose(a2[0, 0], a2[1, 1]):
        theta = torch.tensor(torch.pi / 4, dtype=A.dtype, device=A.device)
    else:
        theta = 0.5 * torch.atan2(2 * a2[0, 1], a2[0, 0] - a2[1, 1])
    c = torch.cos(theta)
    s = torch.sin(theta)
    R = torch.stack([torch.stack([c, -s]), torch.stack([s, c])])
    # diagonalize
    D = R.transpose(0, 1) @ a2 @ R
    V = V @ R
    # singular values
    S = torch.sqrt(torch.tensor([D[0, 0], D[1, 1]], dtype=A.dtype, device=A.device))
    # compute U
    S_inv = torch.diag(1.0 / S)
    U = A @ V @ S_inv
    return U, S, V.transpose(0, 1)
```




### starter_code.py

```python
import torch


def svd_2x2_singular_values(
    A: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Approximate the SVD of a 2×2 matrix A using one Jacobi rotation.
    Returns (U, S, Vt) where S is a 1-D tensor of singular values.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nU, S, Vt = svd_2x2_singular_values(torch.tensor([[1.0, 0.0], [0.0, 1.0]]))\nprint(U.numpy().tolist(), S.numpy().tolist(), Vt.numpy().tolist())",
    "expected_output": "[[0.7071067690849304, -0.7071067690849304], [0.7071067690849304, 0.7071067690849304]] [1.0, 1.0] [[0.7071067690849304, 0.7071067690849304], [-0.7071067690849304, 0.7071067690849304]]"
  },
  {
    "test": "import torch\nU, S, Vt = svd_2x2_singular_values(torch.tensor([[2.0, 0.0], [0.0, 1.0]]))\nprint(U.numpy().tolist(), S.numpy().tolist(), Vt.numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 1.0]] [2.0, 1.0] [[1.0, 0.0], [0.0, 1.0]]"
  }
]
```




### solution.py

```python
import numpy as np


def svd_2x2_singular_values(A: np.ndarray) -> tuple:
    # stick to lowercase
    a = A

    a_t = np.transpose(a)
    a_2 = a_t @ a

    v = np.eye(2)

    for _ in range(1):
        # Compute rotation angle for a 2x2 matrix
        if a_2[0, 0] == a_2[1, 1]:
            theta = np.pi / 4
        else:
            theta = 0.5 * np.arctan2(2 * a_2[0, 1], a_2[0, 0] - a_2[1, 1])

        # Create rotation matrix
        r = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

        # apply rotation
        d = np.transpose(r) @ a_2 @ r

        # update a_2
        a_2 = d

        # accumulate v
        v = v @ r

    # sigma is the diagonal elements squared
    s = np.sqrt([d[0, 0], d[1, 1]])
    s_inv = np.array([[1 / s[0], 0], [0, 1 / s[1]]])

    u = a @ v @ s_inv

    return (u, s, v.T)
```




### starter_code.py

```text
import numpy as np 
 def svd_2x2_singular_values(A: np.ndarray) -> tuple:
	return SVD
```




### tests.json

```json
[
  {
    "test": "print(svd_2x2_singular_values(np.array([[2, 1], [1, 2]])))",
    "expected_output": "(array([[ 0.70710678, -0.70710678],\n       [ 0.70710678,  0.70710678]]), array([3., 1.]), array([[ 0.70710678,  0.70710678],\n       [-0.70710678,  0.70710678]]))"
  },
  {
    "test": "print(svd_2x2_singular_values(np.array([[1, 2], [3, 4]])))",
    "expected_output": "array([[ 0.40455358, 0.9145143 ], [ 0.9145143 , -0.40455358]]), array([5.4649857 , 0.36596619]), array([[ 0.57604844, 0.81741556], [-0.81741556, 0.57604844]])"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def svd_2x2_singular_values_tg(A) -> tuple[Tensor, Tensor, Tensor]:
    """
    Approximate the SVD of a 2×2 matrix A using one Jacobi rotation in tinygrad.
    Returns (U, S, Vt) where S is a 1-D Tensor of singular values.
    """
    A_t = Tensor(A).float()
    # compute AᵀA
    a2 = A_t.T.matmul(A_t)
    V = Tensor([[1.0, 0.0], [0.0, 1.0]])
    # extract entries
    a_val = a2[0, 0].numpy()
    d_val = a2[1, 1].numpy()
    b_val = a2[0, 1].numpy()
    # compute rotation angle
    if np.isclose(a_val, d_val):
        theta = np.pi / 4
    else:
        theta = 0.5 * np.arctan2(2 * b_val, a_val - d_val)
    c, s = np.cos(theta), np.sin(theta)
    R = Tensor([[c, -s], [s, c]])
    D = R.T.matmul(a2).matmul(R)
    V = V.matmul(R)
    # singular values
    S = Tensor(np.sqrt([D[0, 0].numpy(), D[1, 1].numpy()]))
    # compute U
    S_inv = Tensor([[1.0 / S[0].numpy(), 0.0], [0.0, 1.0 / S[1].numpy()]])
    U = A_t.matmul(V).matmul(S_inv)
    return U, S, V.T
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def svd_2x2_singular_values_tg(A) -> tuple[Tensor, Tensor, Tensor]:
    """
    Approximate the SVD of a 2×2 matrix A using one Jacobi rotation in tinygrad.
    Returns (U, S, Vt) where S is a 1-D Tensor of singular values.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nU, S, Vt = svd_2x2_singular_values_tg([[1.0, 0.0], [0.0, 1.0]])\nprint(U.numpy().tolist(), S.numpy().tolist(), Vt.numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 1.0]] [1.0, 1.0] [[1.0, 0.0], [0.0, 1.0]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nU, S, Vt = svd_2x2_singular_values_tg([[2.0, 0.0], [0.0, 1.0]])\nprint(U.numpy().tolist(), S.numpy().tolist(), Vt.numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 1.0]] [2.0, 1.0] [[1.0, 0.0], [0.0, 1.0]]"
  }
]
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/12_singular-value-decomposition-svd/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/12_singular-value-decomposition-svd/description.md)。Deep-ML：Educational Use Only License。
