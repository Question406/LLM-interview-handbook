---
id: drustz-9fad2204105dba1bad
section: deepml
order: 156
level: A
title: Principal Component Analysis (PCA) Implementation
quick: Deep-ML 练习 · Principal Component Analysis (PCA) Implementation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/19_principal-component-analysis-pca-implementation/description.md
    type: primary
---
### description.md

Write a Python function that performs Principal Component Analysis (PCA) from scratch. The function should take a 2D NumPy array as input, where each row represents a data sample and each column represents a feature. The function should standardize the dataset, compute the covariance matrix, find the eigenvalues and eigenvectors, and return the principal components (the eigenvectors corresponding to the largest eigenvalues). The function should also take an integer k as input, representing the number of principal components to return.


### example.json

```json
{
  "input": "data = np.array([[1, 2], [3, 4], [5, 6]]), k = 1",
  "output": "[[0.7071], [0.7071]]",
  "reasoning": "After standardizing the data and computing the covariance matrix, the eigenvalues and eigenvectors are calculated. The largest eigenvalue's corresponding eigenvector is returned as the principal component, rounded to four decimal places."
}
```




### learn.md


## Understanding Eigenvalues in PCA

Principal Component Analysis (PCA) utilizes the concept of eigenvalues and eigenvectors to identify the principal components of a dataset. Here's how eigenvalues fit into the PCA process:

### Eigenvalues and Eigenvectors: The Foundation of PCA
For a given square matrix \( A \), representing the covariance matrix in PCA, eigenvalues \( \lambda \) and their corresponding eigenvectors \( v \) satisfy:
$$
Av = \lambda v
$$

### Calculating Eigenvalues
The eigenvalues of matrix \( A \) are found by solving the characteristic equation:
$$
\det(A - \lambda I) = 0
$$
where \( I \) is the identity matrix of the same dimension as \( A \). This equation highlights the relationship between a matrix, its eigenvalues, and eigenvectors.

### Role in PCA
In PCA, the covariance matrix's eigenvalues represent the variance explained by its eigenvectors. Thus, selecting the eigenvectors associated with the largest eigenvalues is akin to choosing the principal components that retain the most data variance.

### Eigenvalues and Dimensionality Reduction
The magnitude of an eigenvalue correlates with the importance of its corresponding eigenvector (principal component) in representing the dataset's variability. By selecting a subset of eigenvectors corresponding to the largest eigenvalues, PCA achieves dimensionality reduction while preserving as much of the dataset's variability as possible.

### Practical Application
1. **Standardize the Dataset**: Ensure that each feature has a mean of 0 and a standard deviation of 1.
2. **Compute the Covariance Matrix**: Reflects how features vary together.
3. **Find Eigenvalues and Eigenvectors**: Solve the characteristic equation for the covariance matrix.
4. **Select Principal Components**: Choose eigenvectors (components) with the highest eigenvalues for dimensionality reduction.

Through this process, PCA transforms the original features into a new set of uncorrelated features (principal components), ordered by the amount of original variance they explain.


### meta.json

```json
{
  "id": "19",
  "title": "Principal Component Analysis (PCA) Implementation",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/jon-rosen",
      "name": "jon-rosen"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch


def pca(data, k) -> torch.Tensor:
    """
    Perform PCA on `data`, returning the top `k` principal components as a tensor.
    Input: Tensor or convertible of shape (n_samples, n_features).
    Returns: a torch.Tensor of shape (n_features, k), with floats rounded to 4 decimals.
    """
    data_t = torch.as_tensor(data, dtype=torch.float)
    # Standardize
    mean = data_t.mean(dim=0, keepdim=True)
    std = data_t.std(dim=0, unbiased=False, keepdim=True)
    data_std = (data_t - mean) / std
    # Covariance
    cov = torch.cov(data_std.T)
    # Eigen decomposition
    eigenvalues, eigenvectors = torch.linalg.eig(cov)
    vals = eigenvalues.real
    vecs = eigenvectors.real
    # Sort by descending eigenvalue
    idx = torch.argsort(vals, descending=True)
    pcs = vecs[:, idx[:k]]
    # Round to 4 decimals
    pcs = torch.round(pcs * 10000) / 10000
    return pcs
```




### starter_code.py

```python
import torch


def pca(data, k) -> torch.Tensor:
    """
    Perform PCA on `data`, returning the top `k` principal components as a tensor.
    Input: Tensor or convertible of shape (n_samples, n_features).
    Returns: a torch.Tensor of shape (n_features, k), with floats rounded to 4 decimals.
    """
    data_t = torch.as_tensor(data, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "res = pca([[1.0,0.0],[0.0,1.0]], 2)\n# convert to Python list and round each value\nlst = res.tolist()\nrounded = [[round(val,4) for val in row] for row in lst]\nprint(rounded)",
    "expected_output": "[[0.7071, 0.7071], [-0.7071, 0.7071]]"
  },
  {
    "test": "res = pca([[1.0,1.0],[2.0,2.0],[3.0,3.0]], 1)\n# convert to Python list and round each value\nlst = res.tolist()\nrounded = [[round(val,4) for val in row] for row in lst]\nprint(rounded)",
    "expected_output": "[[0.7071], [0.7071]]"
  }
]
```




### solution.py

```python
import numpy as np


def pca(data, k):
    # Standardize the data
    data_standardized = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

    # Compute the covariance matrix
    covariance_matrix = np.cov(data_standardized, rowvar=False)

    # Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

    # Sort the eigenvectors by decreasing eigenvalues
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues_sorted = eigenvalues[idx]
    eigenvectors_sorted = eigenvectors[:, idx]

    # Select the top k eigenvectors (principal components)
    principal_components = eigenvectors_sorted[:, :k]

    return np.round(principal_components, 4)
```




### starter_code.py

```python
import numpy as np


def pca(data: np.ndarray, k: int) -> np.ndarray:
    # Your code here
    return np.round(principal_components, 4)
```




### tests.json

```json
[
  {
    "test": "print(pca(np.array([[4,2,1],[5,6,7],[9,12,1],[4,6,7]]),2))",
    "expected_output": "[[0.6855, 0.0776], [0.6202, 0.4586], [-0.3814, 0.8853]]"
  },
  {
    "test": "print(pca(np.array([[1, 2], [3, 4], [5, 6]]), k = 1))",
    "expected_output": " [[0.7071], [0.7071]]"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def pca_tg(data, k) -> Tensor:
    """
    Perform PCA on `data`, returning the top `k` principal components as a tinygrad Tensor.
    Input: list, NumPy array, or Tensor of shape (n_samples, n_features).
    Returns: a Tensor of shape (n_features, k), with floats rounded to 4 decimals.
    """
    arr = np.array(data, dtype=float)
    # Standardize
    arr_std = (arr - arr.mean(axis=0)) / arr.std(axis=0)
    # Covariance
    cov = np.cov(arr_std, rowvar=False)
    # Eigen decomposition
    vals, vecs = np.linalg.eig(cov)
    idx = np.argsort(vals)[::-1]
    pcs = vecs[:, idx[:k]]
    pcs = np.round(pcs, 4)
    return Tensor(pcs)
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def pca_tg(data, k) -> Tensor:
    """
    Perform PCA on `data`, returning the top `k` principal components as a tinygrad Tensor.
    Input: list, NumPy array, or Tensor of shape (n_samples, n_features).
    Returns: a Tensor of shape (n_features, k), with floats rounded to 4 decimals.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "res = pca_tg([[1.0,0.0],[0.0,1.0]], 2)\n# convert to Python list and round each value\nlst = res.numpy().tolist()\nrounded = [[round(val,4) for val in row] for row in lst]\nprint(rounded)",
    "expected_output": "[[1.0, 0.0], [0.0, 1.0]]"
  },
  {
    "test": "res = pca_tg([[1.0,1.0],[2.0,2.0],[3.0,3.0]], 1)\n# convert to Python list and round each value\nlst = res.numpy().tolist()\nrounded = [[round(val,4) for val in row] for row in lst]\nprint(rounded)",
    "expected_output": "[[0.7071], [0.7071]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/19_principal-component-analysis-pca-implementation/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/19_principal-component-analysis-pca-implementation/description.md)。Deep-ML：Educational Use Only License。
