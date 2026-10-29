---
id: drustz-cbe7a34eb6db6711be
section: deepml
order: 139
level: A
title: Linear Regression Using Normal Equation
quick: Deep-ML 练习 · Linear Regression Using Normal Equation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/14_linear-regression-using-normal-equation/description.md
    type: primary
---
### description.md

Write a Python function that performs linear regression using the normal equation. The function should take a matrix X (features) and a vector y (target) as input, and return the coefficients of the linear regression model. Round your answer to four decimal places, -0.0 is a valid result for rounding a very small number.


### example.json

```json
{
  "input": "X = [[1, 1], [1, 2], [1, 3]], y = [1, 2, 3]",
  "output": "[0.0, 1.0]",
  "reasoning": "The linear model is y = 0.0 + 1.0*x, perfectly fitting the input data."
}
```




### learn.md


## Linear Regression Using the Normal Equation

Linear regression aims to model the relationship between a scalar dependent variable \( y \) and one or more explanatory variables (or independent variables) \( X \). The normal equation provides an analytical solution to find the coefficients \( \theta \) that minimize the cost function for linear regression.

Given a matrix \( X \) (with each row representing a training example and each column a feature) and a vector \( y \) (representing the target values), the normal equation is:
$$
\theta = (X^TX)^{-1}X^Ty
$$

### Explanation of Terms
1. \( X^T \) is the transpose of \( X \).
2. \( (X^TX)^{-1} \) is the inverse of the matrix \( X^TX \).
3. \( y \) is the vector of target values.

### Key Points
- **Feature Scaling**: This method does not require feature scaling.
- **Learning Rate**: There is no need to choose a learning rate.
- **Computational Cost**: Computing the inverse of \( X^TX \) can be computationally expensive if the number of features is very large.

### Practical Implementation
A practical implementation involves augmenting \( X \) with a column of ones to account for the intercept term and then applying the normal equation directly to compute \( \theta \).


### meta.json

```json
{
  "id": "14",
  "title": "Linear Regression Using Normal Equation",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "https://youtu.be/9hkQJxICZj8",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    },
    {
      "profile_link": "https://www.youtube.com/@StoatScript/videos",
      "name": "Stoatscript"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch


def linear_regression_normal_equation(X, y) -> torch.Tensor:
    """
    Solve linear regression via the normal equation using PyTorch.
    X: Tensor or convertible of shape (m,n); y: shape (m,) or (m,1).
    Returns a 1-D tensor of length n, rounded to 4 decimals.
    """
    X_t = torch.as_tensor(X, dtype=torch.float)
    y_t = torch.as_tensor(y, dtype=torch.float).reshape(-1, 1)
    # normal equation: theta = (XᵀX)⁻¹ Xᵀ y
    XtX = X_t.transpose(0, 1) @ X_t
    theta = torch.linalg.inv(XtX) @ (X_t.transpose(0, 1) @ y_t)
    theta = theta.flatten()
    return torch.round(theta * 10000) / 10000
```




### starter_code.py

```python
import torch


def linear_regression_normal_equation(X, y) -> torch.Tensor:
    """
    Solve linear regression via the normal equation using PyTorch.
    X: Tensor or convertible of shape (m,n); y: shape (m,) or (m,1).
    Returns a 1-D tensor of length n, rounded to 4 decimals.
    """
    X_t = torch.as_tensor(X, dtype=torch.float)
    y_t = torch.as_tensor(y, dtype=torch.float).reshape(-1, 1)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nX = torch.eye(2)\ny = torch.tensor([5.0, 3.0])\nres = linear_regression_normal_equation(X, y)\nprint(res.detach().numpy().tolist())",
    "expected_output": "[5.0, 3.0]"
  },
  {
    "test": "import torch\nX = torch.tensor([[1.0,1.0],[1.0,2.0],[1.0,3.0]])\ny = torch.tensor([1.0,2.0,3.0])\nres = linear_regression_normal_equation(X, y)\nprint(res.detach().numpy().tolist())",
    "expected_output": "[0.0, 1.0]"
  }
]
```




### solution.py

```python
import numpy as np


def linear_regression_normal_equation(
    X: list[list[float]], y: list[float]
) -> list[float]:
    X = np.array(X)
    y = np.array(y).reshape(-1, 1)
    X_transpose = X.T
    theta = np.linalg.inv(X_transpose.dot(X)).dot(X_transpose).dot(y)
    theta = np.round(theta, 4).flatten().tolist()
    return theta
```




### starter_code.py

```python
import numpy as np


def linear_regression_normal_equation(
    X: list[list[float]], y: list[float]
) -> list[float]:
    # Your code here, make sure to round
    return theta
```




### tests.json

```json
[
  {
    "test": "print(linear_regression_normal_equation([[1, 1], [1, 2], [1, 3]], [1, 2, 3]))",
    "expected_output": "[-0.0, 1.0]"
  },
  {
    "test": "print(linear_regression_normal_equation([[1, 3, 4], [1, 2, 5], [1, 3, 2]], [1, 2, 1]))",
    "expected_output": "[4.0, -1.0, -0.0]"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def linear_regression_normal_equation_tg(X, y) -> Tensor:
    """
    Solve linear regression via the normal equation using tinygrad.
    X: list, NumPy array, or Tensor of shape (m,n); y: shape (m,) or (m,1).
    Returns a 1-D Tensor of length n, rounded to 4 decimals.
    """
    X_np = np.array(X, dtype=float)
    y_np = np.array(y, dtype=float).reshape(-1, 1)
    theta = np.linalg.inv(X_np.T.dot(X_np)).dot(X_np.T).dot(y_np)
    theta = np.round(theta.flatten(), 4)
    return Tensor(theta)
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def linear_regression_normal_equation_tg(X, y) -> Tensor:
    """
    Solve linear regression via the normal equation using tinygrad.
    X: list, NumPy array, or Tensor of shape (m,n); y: shape (m,) or (m,1).
    Returns a 1-D Tensor of length n, rounded to 4 decimals.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = linear_regression_normal_equation_tg(\n    [[1.0,0.0],[0.0,1.0]],\n    [5.0,3.0]\n)\nprint(res.numpy().tolist())",
    "expected_output": "[5.0, 3.0]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nres = linear_regression_normal_equation_tg(\n    [[1.0,1.0],[1.0,2.0],[1.0,3.0]],\n    [1.0,2.0,3.0]\n)\nprint(res.numpy().tolist())",
    "expected_output": "[0.0, 1.0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/14_linear-regression-using-normal-equation/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/14_linear-regression-using-normal-equation/description.md)。Deep-ML：Educational Use Only License。
