---
id: drustz-2ccdb189b987569de5
section: deepml
order: 18
level: A
title: Calculate Covariance Matrix
quick: Deep-ML 练习 · Calculate Covariance Matrix
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/10_calculate-covariance-matrix/description.md
    type: primary
---
### description.md

Write a Python function to calculate the covariance matrix for a given set of vectors. The function should take a list of lists, where each inner list represents a feature with its observations, and return a covariance matrix as a list of lists. Additionally, provide test cases to verify the correctness of your implementation.


### example.json

```json
{
  "input": "[[1, 2, 3], [4, 5, 6]]",
  "output": "[[1.0, 1.0], [1.0, 1.0]]",
  "reasoning": "The covariance between the two features is calculated based on their deviations from the mean. For the given vectors, both covariances are 1.0, resulting in a symmetric covariance matrix."
}
```




### learn.md

## Understanding Covariance Matrix

The covariance matrix is a fundamental concept in statistics and machine learning, used to understand the relationship between multiple variables (features) in a dataset. It quantifies the degree to which two variables change together.

### Key Concepts

- **Covariance**: Measures the directional relationship between two random variables. A positive covariance indicates that the variables increase together, while a negative covariance indicates that one variable increases as the other decreases.
- **Covariance Matrix**: For a dataset with $n$ features, the covariance matrix is an $n \times n$ matrix where each element $(i, j)$ represents the covariance between the $i^{th}$ and $j^{th}$ features.

### Covariance Formula

The covariance between two variables $X$ and $Y$ is calculated as:

$$
\text{cov}(X, Y) = \frac{\sum_{k=1}^{m} (X_k - \bar{X})(Y_k - \bar{Y})}{m - 1}
$$

Where:

- $X_k$ and $Y_k$ are the individual observations of variables $X$ and $Y$.
- $\bar{X}$ and $\bar{Y}$ are the means of $X$ and $Y$.
- $m$ is the number of observations.

### Constructing the Covariance Matrix

Given a dataset with $n$ features, the covariance matrix is constructed as follows:

1. **Calculate the Mean**: Compute the mean of each feature.
2. **Compute Covariance**: For each pair of features, calculate the covariance using the formula above.
3. **Populate the Matrix**: Place the computed covariance values in the corresponding positions in the matrix. The diagonal elements represent the variance of each feature.

$$
\text{Covariance Matrix} =
\begin{bmatrix}
\text{cov}(X_1, X_1) & \text{cov}(X_1, X_2) & \cdots & \text{cov}(X_1, X_n) \\
\text{cov}(X_2, X_1) & \text{cov}(X_2, X_2) & \cdots & \text{cov}(X_2, X_n) \\
\vdots & \vdots & \ddots & \vdots \\
\text{cov}(X_n, X_1) & \text{cov}(X_n, X_2) & \cdots & \text{cov}(X_n, X_n) \\
\end{bmatrix}
$$

### Example Calculation

Consider the following dataset with two features:

$$
\begin{align*}
\text{Feature 1} &: [1, 2, 3] \\
\text{Feature 2} &: [4, 5, 6]
\end{align*}
$$

1. **Calculate Means**:
   $$
   \bar{X}_1 = \frac{1 + 2 + 3}{3} = 2.0 \\
   \bar{X}_2 = \frac{4 + 5 + 6}{3} = 5.0
   $$

2. **Compute Covariances**:
   $$
   \text{cov}(X_1, X_1) = \frac{(1-2)^2 + (2-2)^2 + (3-2)^2}{3-1} = 1.0 \\
   \text{cov}(X_1, X_2) = \frac{(1-2)(4-5) + (2-2)(5-5) + (3-2)(6-5)}{3-1} = 1.0 \\
   \text{cov}(X_2, X_2) = \frac{(4-5)^2 + (5-5)^2 + (6-5)^2}{3-1} = 1.0
   $$

3. **Covariance Matrix**:
   $$
   \begin{bmatrix}
   1.0 & 1.0 \\
   1.0 & 1.0 
   \end{bmatrix}
   $$

### Applications

Covariance matrices are widely used in various fields, including:

- **Principal Component Analysis (PCA)**: Reducing the dimensionality of datasets while preserving variance.
- **Portfolio Optimization**: Understanding the variance and covariance between different financial assets.
- **Multivariate Statistics**: Analyzing the relationships between multiple variables simultaneously.

Understanding the covariance matrix is crucial for interpreting the relationships in multivariate data and for performing advanced statistical analyses.


### meta.json

```json
{
  "id": "10",
  "title": "Calculate Covariance Matrix",
  "difficulty": "easy",
  "category": "Statistics",
  "video": "https://youtu.be/Mmuz3a4idg4",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    },
    {
      "profile_link": "https://github.com/Selbl",
      "name": "Selbl"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "easy"
}
```




### solution.py

```python
import torch


def calculate_covariance_matrix(vectors) -> torch.Tensor:
    """
    Calculate the covariance matrix for given feature vectors using PyTorch.
    Input: 2D array-like of shape (n_features, n_observations).
    Returns a tensor of shape (n_features, n_features).
    """
    v_t = torch.as_tensor(vectors, dtype=torch.float)
    # use built-in covariance
    return torch.cov(v_t)
```




### starter_code.py

```python
import torch


def calculate_covariance_matrix(vectors) -> torch.Tensor:
    """
    Calculate the covariance matrix for given feature vectors using PyTorch.
    Input: 2D array-like of shape (n_features, n_observations).
    Returns a tensor of shape (n_features, n_features).
    """
    v_t = torch.as_tensor(vectors, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nv = [[1.0,2.0,3.0],[4.0,5.0,6.0]]\ncov = calculate_covariance_matrix(v)\nprint(cov.detach().numpy().tolist())",
    "expected_output": "[[1.0, 1.0], [1.0, 1.0]]"
  },
  {
    "test": "import torch\nv = [[1.0,2.0,3.0],[3.0,3.0,3.0]]\ncov = calculate_covariance_matrix(v)\nprint(cov.detach().numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 0.0]]"
  }
]
```




### solution.py

```python
import numpy as np


def calculate_covariance_matrix(vectors: list[list[float]]) -> list[list[float]]:
    n_observations = len(vectors)
    n_features = len(vectors[0])
    covariance_matrix = [
        [0 for _ in range(n_observations)] for _ in range(n_observations)
    ]

    means = [sum(feature) / n_features for feature in vectors]

    for i in range(n_observations):
        for j in range(i, n_observations):
            covariance = sum(
                (vectors[i][k] - means[i]) * (vectors[j][k] - means[j])
                for k in range(n_features)
            ) / (n_features - 1)
            covariance_matrix[i][j] = covariance_matrix[j][i] = covariance

    return covariance_matrix
```




### starter_code.py

```python
def calculate_covariance_matrix(vectors: list[list[float]]) -> list[list[float]]:
    # Your code here
    return []
```




### tests.json

```json
[
  {
    "test": "print(calculate_covariance_matrix([[1, 2, 3], [4, 5, 6]]))",
    "expected_output": "[[1.0, 1.0], [1.0, 1.0]]"
  },
  {
    "test": "print(calculate_covariance_matrix([[1, 5, 6], [2, 3, 4], [7, 8, 9]]))",
    "expected_output": "[[7.0, 2.5, 2.5], [2.5, 1.0, 1.0], [2.5, 1.0, 1.0]]"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor


def calculate_covariance_matrix_tg(vectors) -> Tensor:
    """
    Calculate the covariance matrix for given feature vectors using tinygrad.
    Input: 2D array-like of shape (n_features, n_observations).
    Returns a Tensor of shape (n_features, n_features).
    """
    v_t = Tensor(vectors).float()
    n_features, n_obs = v_t.shape
    # compute feature means
    means = v_t.sum(axis=1).reshape(n_features, 1) / n_obs
    centered = v_t - means
    cov = centered.matmul(centered.transpose(0, 1)) / (n_obs - 1)
    return cov
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def calculate_covariance_matrix_tg(vectors) -> Tensor:
    """
    Calculate the covariance matrix for given feature vectors using tinygrad.
    Input: 2D array-like of shape (n_features, n_observations).
    Returns a Tensor of shape (n_features, n_features).
    """
    v_t = Tensor(vectors).float()
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = calculate_covariance_matrix_tg([[1.0,2.0,3.0],[4.0,5.0,6.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[[1.0, 1.0], [1.0, 1.0]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = calculate_covariance_matrix_tg([[1.0,2.0,3.0],[3.0,3.0,3.0]])\nprint(res.numpy().tolist())",
    "expected_output": "[[1.0, 0.0], [0.0, 0.0]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/10_calculate-covariance-matrix/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/10_calculate-covariance-matrix/description.md)。Deep-ML：Educational Use Only License。
