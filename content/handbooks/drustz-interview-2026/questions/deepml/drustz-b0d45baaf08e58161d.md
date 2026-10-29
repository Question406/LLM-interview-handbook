---
id: drustz-b0d45baaf08e58161d
section: deepml
order: 33
level: A
title: Compute Orthonormal Basis for 2D Vectors
quick: Deep-ML 练习 · Compute Orthonormal Basis for 2D Vectors
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/117_compute-orthonormal-basis-for-2d-vectors/description.md
    type: primary
---
### description.md

Implement a function that computes an orthonormal basis for the subspace spanned by a list of 2D vectors using the Gram-Schmidt process. The function should take a list of 2D vectors and a tolerance value (tol) to determine linear independence, returning a list of orthonormal vectors (unit length and orthogonal to each other) that span the same subspace. This is a fundamental concept in linear algebra with applications in machine learning, such as feature orthogonalization.


### example.json

```json
{
  "input": "orthonormal_basis([[1, 0], [1, 1]])",
  "output": "[array([1., 0.]), array([0., 1.])]",
  "reasoning": "Start with [1, 0], normalize to [1, 0]. For [1, 1], subtract its projection onto [1, 0] (which is [1, 0]), leaving [0, 1]. Check if norm > 1e-10 (it is 1), then normalize to [0, 1]. The result is an orthonormal basis."
}
```




### learn.md

## Understanding the Gram-Schmidt Process

The Gram-Schmidt process transforms a set of vectors into an orthonormal basis vectors that are orthogonal (perpendicular) and have unit length for the subspace they span.

### Mathematical Definition

Given vectors $v_1, v_2, \ldots$, the process constructs an orthonormal set $u_1, u_2, \ldots$ as follows:
1. $u_1 = \frac{v_1}{\|v_1\|}$ (normalize the first vector).
2. For subsequent vectors $v_k$:
   - Subtract projections: $$w_k = v_k - \sum_{i=1}^{k-1} \text{proj}_{u_i}(v_k),$$ where $\text{proj}_{u_i}(v_k) = (v_k \cdot u_i) u_i$.
   - Normalize: $$u_k = \frac{w_k}{\|w_k\|},$$ if $\|w_k\| > \text{tol}$.

### Why Orthonormal Bases?

- Orthogonal vectors simplify computations (e.g., their dot product is zero).
- Unit length ensures equal scaling, useful in $PCA$, $QR$ decomposition, and neural network optimization.

### Special Case

If a vector's norm is less than or equal to $\text{tol}$ (default $1e-10$), it's considered linearly dependent and excluded from the basis.

### Example

For vectors `[[1, 0], [1, 1]]` with $\text{tol} = 1e-10$:
1. $v_1 = [1, 0]$, $\|v_1\| = 1$, so $u_1 = [1, 0]$.
2. $v_2 = [1, 1]$, projection on $u_1$: $(v_2 \cdot u_1) u_1 = 1 \cdot [1, 0] = [1, 0]$.
   - $w_2 = [1, 1] - [1, 0] = [0, 1]$.
   - $\|w_2\| = 1 > 1e-10$, so $u_2 = [0, 1]$.

Result: `[[1, 0], [0, 1]]`, rounded to 4 decimal places.


### meta.json

```json
{
  "id": "117",
  "title": "Compute Orthonormal Basis for 2D Vectors",
  "difficulty": "medium",
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


def orthonormal_basis(
    vectors: list[list[float]], tol: float = 1e-10
) -> list[np.ndarray]:
    basis = []
    for v in vectors:
        v = np.array(v, dtype=float)
        for b in basis:
            v = v - np.dot(v, b) * b
        norm = np.sqrt(np.dot(v, v))
        if norm > tol:
            v = v / norm
            basis.append(v)
    return basis
```




### starter_code.py

```python
import numpy as np


def orthonormal_basis(
    vectors: list[list[float]], tol: float = 1e-10
) -> list[np.ndarray]:
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "basis = orthonormal_basis([[1, 0], [1, 1]]); print([b.round(4) for b in basis])",
    "expected_output": "[array([1., 0.]), array([0., 1.])]"
  },
  {
    "test": "basis = orthonormal_basis([[2, 0], [4, 0]], tol=1e-10); print([b.round(4) for b in basis])",
    "expected_output": "[array([1., 0.])]"
  },
  {
    "test": "basis = orthonormal_basis([[1, 1], [1, -1]], tol=1e-5); print([b.round(4) for b in basis])",
    "expected_output": "[array([0.7071, 0.7071]), array([0.7071, -0.7071])]"
  },
  {
    "test": "basis = orthonormal_basis([[0, 0]], tol=1e-10); print([b.round(4) for b in basis])",
    "expected_output": "[]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/117_compute-orthonormal-basis-for-2d-vectors/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/117_compute-orthonormal-basis-for-2d-vectors/description.md)。Deep-ML：Educational Use Only License。
