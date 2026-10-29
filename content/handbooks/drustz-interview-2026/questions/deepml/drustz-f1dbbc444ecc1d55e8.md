---
id: drustz-f1dbbc444ecc1d55e8
section: deepml
order: 138
level: A
title: Linear Regression Using Gradient Descent
quick: Deep-ML 练习 · Linear Regression Using Gradient Descent
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/15_linear-regression-using-gradient-descent/description.md
    type: primary
---
### description.md

Write a Python function that performs linear regression using gradient descent. The function should take NumPy arrays X (features with a column of ones for the intercept) and y (target) as input, along with learning rate alpha and the number of iterations, and return the coefficients of the linear regression model as a NumPy array. Round your answer to four decimal places. -0.0 is a valid result for rounding a very small number.


### example.json

```json
{
  "input": "X = np.array([[1, 1], [1, 2], [1, 3]]), y = np.array([1, 2, 3]), alpha = 0.01, iterations = 1000",
  "output": "np.array([0.1107, 0.9513])",
  "reasoning": "The linear model is y = 0.0 + 1.0*x, which fits the input data after gradient descent optimization."
}
```




### learn.md


## Linear Regression Using Gradient Descent

Linear regression can also be performed using a technique called gradient descent, where the coefficients (or weights) of the model are iteratively adjusted to minimize a cost function (usually mean squared error). This method is particularly useful when the number of features is too large for analytical solutions like the normal equation or when the feature matrix is not invertible.

The gradient descent algorithm updates the weights by moving in the direction of the negative gradient of the cost function with respect to the weights. The updates occur iteratively until the algorithm converges to a minimum of the cost function.

The update rule for each weight is given by:
$$
\theta_j := \theta_j - \alpha \frac{1}{m} \sum_{i=1}^{m} \left( h_{\theta}(x^{(i)}) - y^{(i)} \right)x_j^{(i)}
$$

### Explanation of Terms
1. $\alpha$ is the learning rate.
2. $m$ is the number of training examples.
3. $h_{\theta}(x^{(i)})$ is the hypothesis function at iteration $i$.
4. $x^{(i)}$ is the feature vector of the $i^{\text{th}}$ training example.
5. $y^{(i)}$ is the actual target value for the $i^{\text{th}}$ training example.
6. $x_j^{(i)}$ is the value of feature $j$ for the $i^{\text{th}}$ training example.

### Key Points
- **Learning Rate**: The choice of learning rate is crucial for the convergence and performance of gradient descent. 
  - A small learning rate may lead to slow convergence.
  - A large learning rate may cause overshooting and divergence.
- **Number of Iterations**: The number of iterations determines how long the algorithm runs before it converges or stops.

### Practical Implementation
Implementing gradient descent involves:
1. Initializing the weights theta ($\theta$), with 0s in our case, 
2. Compute the predicted values for all training examples using the current weights
3. Computing the gradient for each iteration step by aggregating the errors over all training examples and scaling it by the learning rate,
4. and iteratively updating the weights according to the update rule.


### meta.json

```json
{
  "id": "15",
  "title": "Linear Regression Using Gradient Descent",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "https://youtu.be/rHJ-DfFvpkQ",
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
    },
    {
      "profile_link": "https://www.youtube.com/@StoatScript/videos",
      "name": "StoatScript"
    },
    {
      "profile_link": "https://github.com/ana-baltaretu",
      "name": "anisca22"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch


def linear_regression_gradient_descent(X, y, alpha, iterations) -> torch.Tensor:
    """
    Solve linear regression via gradient descent using PyTorch autograd.
    X: Tensor or convertible shape (m,n); y: shape (m,) or (m,1).
    alpha: learning rate; iterations: number of steps.
    Returns a 1-D tensor of length n, rounded to 4 decimals.
    """
    X_t = torch.as_tensor(X, dtype=torch.float)
    y_t = torch.as_tensor(y, dtype=torch.float).reshape(-1, 1)
    m, n = X_t.shape
    theta = torch.zeros((n, 1), requires_grad=True)
    for _ in range(iterations):
        preds = X_t @ theta
        loss = ((preds - y_t) ** 2).mean()
        loss.backward()
        with torch.no_grad():
            theta -= alpha * theta.grad
            theta.grad.zero_()
    # detach before converting to numpy
    result = theta.flatten().detach()
    return torch.round(result * 10000) / 10000
```




### starter_code.py

```python
import torch


def linear_regression_gradient_descent(X, y, alpha, iterations) -> torch.Tensor:
    """
    Solve linear regression via gradient descent using PyTorch autograd.
    X: Tensor or convertible shape (m,n); y: shape (m,) or (m,1).
    alpha: learning rate; iterations: number of steps.
    Returns a 1-D tensor of length n, rounded to 4 decimals.
    """
    X_t = torch.as_tensor(X, dtype=torch.float)
    y_t = torch.as_tensor(y, dtype=torch.float).reshape(-1, 1)
    m, n = X_t.shape
    theta = torch.zeros((n, 1), requires_grad=True)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = linear_regression_gradient_descent(\n    torch.eye(2),\n    torch.tensor([5.0, 3.0]),\n    0.1,\n    10\n)\nprint(res.detach().numpy().tolist())",
    "expected_output": "[3.2565999031066895, 1.9539999961853027]"
  },
  {
    "test": "import torch\nX = torch.tensor([[1.0,1.0],[1.0,2.0],[1.0,3.0]])\ny = torch.tensor([1.0,2.0,3.0])\nres = linear_regression_gradient_descent(X, y, 0.01, 1000)\nprint(res.detach().numpy().tolist())",
    "expected_output": "[0.03319999948143959, 0.9854000210762024]"
  }
]
```




### solution.py

```python
import numpy as np


def linear_regression_gradient_descent(
    X: np.ndarray, y: np.ndarray, alpha: float, iterations: int
) -> np.ndarray:
    """
    Perform linear regression using gradient descent.

    m = number of training examples
    n = number of parameters (features), technically n-1 features, 1st column is for intercept

    X: shape (m, n), `m` training examples with `n` input values for each feature
    y: shape (m, 1) array with the target values (ground truth)
    alpha: learning rate
    iterations: number of gradient descent steps
    """

    m, n = X.shape
    y = y.reshape(-1, 1)  # Make sure y is a column vector
    theta = np.zeros((n, 1))  # 1. Initializing the weights with 0s
    for _ in range(iterations):
        predictions = X @ theta  # 2. Compute predictions h(x)
        errors = predictions - y  # 3. Compute error = h - y
        gradient = alpha * (X.T @ errors) / m  # 4. Compute gradient
        theta -= gradient  # 5. Update weights for each iteration
    return np.round(theta.flatten(), 4)
```




### starter_code.py

```python
import numpy as np


def linear_regression_gradient_descent(
    X: np.ndarray, y: np.ndarray, alpha: float, iterations: int
) -> np.ndarray:
    """
    Perform linear regression using gradient descent.

    m = number of training examples
    n = number of parameters (features), technically n-1 features, 1st column is for intercept

    X: shape (m, n), `m` training examples with `n` input values for each feature
    y: shape (m, 1) array with the target values (ground truth)
    alpha: learning rate
    iterations: number of gradient descent steps
    """

    m, n = X.shape
    y = y.reshape(-1, 1)  # Make sure y is a column vector
    theta = np.zeros((n, 1))

    # TODO: Your code here

    return np.round(theta.flatten(), 4)  # Rounded to 4 decimals
```




### tests.json

```json
[
  {
    "test": "print(linear_regression_gradient_descent(np.array([[1, 1], [1, 2], [1, 3]]), np.array([1, 2, 3]), 0.01, 1000))",
    "expected_output": "[0.1107, 0.9513]"
  },
  {
    "test": "print(linear_regression_gradient_descent(np.array([[1, 5], [1, 7], [1, 9]]), np.array([10, 14, 18]), 0.01, 5000))",
    "expected_output": "[0.0211, 1.9971]"
  },
  {
    "test": "print(linear_regression_gradient_descent(np.array([[1, 1, 0], [1, 2, 1], [1, 3, 2], [1, 4, 3]]), np.array([5, 6, 7, 8]), 0.05, 2000))",
    "expected_output": "[3.0, 2.0, -1.0]"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def linear_regression_gradient_descent_tg(X, y, alpha, iterations) -> Tensor:
    """
    Solve linear regression via gradient descent using tinygrad autograd.
    X: Tensor or convertible shape (m,n); y: shape (m,) or (m,1).
    alpha: learning rate; iterations: number of steps.
    Returns a 1-D Tensor of length n, rounded to 4 decimals.
    """
    X_t = Tensor(X).float()
    y_t = Tensor(y).float().reshape(-1, 1)
    m, n = X_t.shape
    theta = Tensor([[0.0] for _ in range(n)])
    for _ in range(iterations):
        preds = X_t.matmul(theta)
        loss = (preds - y_t).pow(2).mean()
        loss.backward()
        # gradient step
        theta = theta - alpha * theta.grad
        theta.grad = None
    res = theta.reshape(n).detach().numpy()
    return Tensor(np.round(res, 4))
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def linear_regression_gradient_descent_tg(X, y, alpha, iterations) -> Tensor:
    """
    Solve linear regression via gradient descent using tinygrad autograd.
    X: Tensor or convertible shape (m,n); y: shape (m,) or (m,1).
    alpha: learning rate; iterations: number of steps.
    Returns a 1-D Tensor of length n, rounded to 4 decimals.
    """
    X_t = Tensor(X).float()
    y_t = Tensor(y).float().reshape(-1, 1)
    m, n = X_t.shape
    theta = Tensor([[0.0] for _ in range(n)])
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nres = linear_regression_gradient_descent_tg(\n    [[1.0,0.0],[0.0,1.0]],\n    [5.0,3.0],\n    0.1,\n    10\n)\nprint(res.numpy().tolist())",
    "expected_output": "[5.0, 3.0]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nX = [[1.0,1.0],[1.0,2.0],[1.0,3.0]]\ny = [1.0,2.0,3.0]\nres = linear_regression_gradient_descent_tg(X, y, 0.01, 1000)\nprint(res.numpy().tolist())",
    "expected_output": "[0.0, 1.0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/15_linear-regression-using-gradient-descent/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/15_linear-regression-using-gradient-descent/description.md)。Deep-ML：Educational Use Only License。
