---
id: drustz-aa61f67f62c304d24d
section: deepml
order: 44
level: A
title: Deep-ML legacy · 139 elastic net gradient descent
quick: Deep-ML 练习 · Deep-ML legacy · 139 elastic net gradient descent
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/139_elastic_net_gradient_descent/learn.md
    type: primary
---
### learn.md

# Elastic Net Regression Using Gradient Descent

Elastic Net Regression combines both L1 (Lasso) and L2 (Ridge) regularization techniques to overcome the limitations of using either regularization method alone. It's particularly useful when dealing with datasets that have many correlated features.

## What is Elastic Net?

Elastic Net addresses two main issues:
- **Lasso's limitation**: When features are highly correlated, Lasso tends to select only one feature from a group of correlated features arbitrarily
- **Ridge's limitation**: Ridge regression doesn't perform feature selection (coefficients approach zero but never become exactly zero)

The goal of Elastic Net is to minimize the objective function:

$$J(w, b) = \underbrace{\frac{1}{2n} \sum_{i=1}^n\left( y_i - \left(\sum_{j=1}^pX_{ij}w_j+b\right)\right)^2}_{\text{MSE Loss}} + \underbrace{\alpha_1 \sum_{j=1}^p |w_j|}_{\text{L1 Regularization}} + \underbrace{\alpha_2 \sum_{j=1}^p w_j^2}_{\text{L2 Regularization}}$$

Where:
* The first term is the **Mean Squared Error (MSE) Loss**: $\frac{1}{2n} \sum_{i=1}^n\left( y_i - \left(\sum_{j=1}^pX_{ij}w_j+b\right)\right)^2$
* The second term is the **L1 Regularization** (Lasso penalty): $\alpha_1 \sum_{j=1}^p |w_j|$
* The third term is the **L2 Regularization** (Ridge penalty): $\alpha_2 \sum_{j=1}^p w_j^2$
* $\alpha_1$ controls the strength of L1 regularization
* $\alpha_2$ controls the strength of L2 regularization

## Step-by-Step Implementation Guide

### 1. Initialize weights $w_j$ and bias $b$ to 0

### 2. Make Predictions
At each iteration, calculate predictions using:
$$\hat{y}_i = \sum_{j=1}^pX_{ij}w_j + b$$

Where:
- $\hat{y}_i$ is the predicted value for the $i$-th sample
- $X_{ij}$ is the value of the $i$-th sample's $j$-th feature
- $w_j$ is the weight associated with the $j$-th feature

### 3. Calculate Residuals
Find the difference between actual and predicted values: $error_i = \hat{y}_i - y_i$

### 4. Update Weights and Bias Using Gradients

**Gradient with respect to weights:**
$$\frac{\partial J}{\partial w_j} = \frac{1}{n} \sum_{i=1}^nX_{ij}(\hat{y}_i - y_i) + \alpha_1 \cdot \text{sign}(w_j) + 2\alpha_2 \cdot w_j$$

**Gradient with respect to bias:**
$$\frac{\partial J}{\partial b} = \frac{1}{n} \sum_{i=1}^n(\hat{y}_i - y_i)$$

**Update rules:**
$$w_j = w_j - \eta \cdot \frac{\partial J}{\partial w_j}$$
$$b = b - \eta \cdot \frac{\partial J}{\partial b}$$

Where $\eta$ is the learning rate.

### 5. Check for Convergence
Repeat steps 2-4 until convergence. Convergence is determined by evaluating the L1 norm of the weight gradients:

$$||\nabla w||_1 = \sum_{j=1}^p \left|\frac{\partial J}{\partial w_j}\right|$$

If $||\nabla w||_1 < \text{tolerance}$, stop the algorithm.

### 6. Return the Final Weights and Bias

## Key Parameters

- **alpha1**: L1 regularization strength (promotes sparsity)
- **alpha2**: L2 regularization strength (handles correlated features)
- **learning_rate**: Step size for gradient descent
- **max_iter**: Maximum number of iterations
- **tol**: Convergence tolerance
Path
## Key Differences from Lasso and Ridge

1. **Lasso (L1 only)**: Tends to select one feature from correlated groups, can be unstable with small sample sizes
2. **Ridge (L2 only)**: Keeps all features but shrinks coefficients, doesn't perform feature selection
3. **Elastic Net (L1 + L2)**: Combines benefits of both - performs feature selection while handling correlated features better than Lasso alone

The balance between L1 and L2 regularization is controlled by the `alpha1` and `alpha2` parameters, allowing you to tune the model for your specific dataset characteristics.

### solution.py

```python
import numpy as np


def elastic_net_gradient_descent(
    X: np.ndarray,
    y: np.ndarray,
    alpha1: float = 0.1,
    alpha2: float = 0.1,
    learning_rate: float = 0.01,
    max_iter: int = 1000,
    tol: float = 1e-4,
) -> tuple:
    """
    Implement Elastic Net regression using gradient descent.

    Parameters:
    X: Feature matrix (n_samples, n_features)
    y: Target values (n_samples,)
    alpha1: L1 regularization strength (Lasso)
    alpha2: L2 regularization strength (Ridge)
    learning_rate: Step size for gradient descent
    max_iter: Maximum number of iterations
    tol: Convergence tolerance

    Returns:
    tuple: (weights, bias)
    """
    n_samples, n_features = X.shape

    # Initialize weights and bias
    weights = np.zeros(n_features)
    bias = 0

    for _ in range(max_iter):
        # Make predictions
        y_pred = np.dot(X, weights) + bias

        # Calculate residuals
        error = y_pred - y

        # Calculate gradients
        grad_w = (
            (1 / n_samples) * np.dot(X.T, error)
            + alpha1 * np.sign(weights)
            + 2 * alpha2 * weights
        )
        grad_b = (1 / n_samples) * np.sum(error)

        # Update weights and bias
        weights -= learning_rate * grad_w
        bias -= learning_rate * grad_b

        # Check for convergence
        if np.linalg.norm(grad_w, ord=1) < tol:
            break

    return weights, bias


def test_elastic_net_gradient_descent():
    """Test cases for Elastic Net implementation"""

    # Test case 1: Simple linear relationship
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([0, 1, 2])
    alpha1, alpha2 = 0.1, 0.1

    weights, bias = elastic_net_gradient_descent(
        X, y, alpha1=alpha1, alpha2=alpha2, learning_rate=0.01, max_iter=1000
    )

    expected_weights = np.array([0.37, 0.37])
    expected_bias = 0.24

    assert np.allclose(weights, expected_weights, atol=0.05), "Test case 1 failed"
    assert np.isclose(bias, expected_bias, atol=0.05), "Test case 1 failed"

    # Test case 2: More complex relationship
    X = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])
    y = np.array([1, 2, 3, 4, 5])
    alpha1, alpha2 = 0.1, 0.1

    weights, bias = elastic_net_gradient_descent(
        X, y, alpha1=alpha1, alpha2=alpha2, learning_rate=0.01, max_iter=2000
    )

    expected_weights = np.array([0.42, 0.48])
    expected_bias = 0.68

    assert np.allclose(weights, expected_weights, atol=0.05), "Test case 2 failed"
    assert np.isclose(bias, expected_bias, atol=0.05), "Test case 2 failed"


if __name__ == "__main__":
    test_elastic_net_gradient_descent()
    print("All Elastic Net tests passed!")
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/Problems/139_elastic_net_gradient_descent/learn.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/139_elastic_net_gradient_descent/learn.md)。Deep-ML：Educational Use Only License。
