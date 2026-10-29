---
id: drustz-cd92bdd6a145c70298
section: deepml
order: 111
level: A
title: Implement Ridge Regression Loss Function
quick: Deep-ML 练习 · Implement Ridge Regression Loss Function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/43_implement-ridge-regression-loss-function/description.md
    type: primary
---
### description.md

Write a Python function `ridge_loss` that implements the Ridge Regression loss function. The function should take a 2D numpy array `X` representing the feature matrix, a 1D numpy array `w` representing the coefficients, a 1D numpy array `y_true` representing the true labels, and a float `alpha` representing the regularization parameter. The function should return the Ridge loss, which combines the Mean Squared Error (MSE) and a regularization term.


### example.json

```json
{
  "input": "import numpy as np\n\nX = np.array([[1, 1], [2, 1], [3, 1], [4, 1]])\nw = np.array([0.2, 2])\ny_true = np.array([2, 3, 4, 5])\nalpha = 0.1\n\nloss = ridge_loss(X, w, y_true, alpha)\nprint(loss)",
  "output": "2.204",
  "reasoning": "The Ridge loss is calculated using the Mean Squared Error (MSE) and a regularization term. The output represents the combined loss value."
}
```




### learn.md


## Ridge Regression Loss

Ridge Regression is a linear regression method with a regularization term to prevent overfitting by controlling the size of the coefficients.

### Key Concepts:
1. **Regularization**:  
   Adds a penalty to the loss function to discourage large coefficients, helping to generalize the model.

2. **Mean Squared Error (MSE)**:  
   Measures the average squared difference between actual and predicted values.

3. **Penalty Term**:  
   The sum of the squared coefficients, scaled by the regularization parameter $ \lambda $, which controls the strength of the regularization.

### Ridge Loss Function
The Ridge Loss function combines MSE and the penalty term:
$$
L(\beta) = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 + \lambda \sum_{j=1}^{p} \beta_j^2
$$

### Implementation Steps:
1. **Calculate MSE**:  
   Compute the average squared difference between actual and predicted values.

2. **Add Regularization Term**:  
   Compute the sum of squared coefficients multiplied by $ \lambda $.

3. **Combine and Minimize**:  
   Sum MSE and the regularization term to form the Ridge loss, then minimize this loss to find the optimal coefficients.


### meta.json

```json
{
  "id": "43",
  "title": "Implement Ridge Regression Loss Function",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ],
  "marimo_link": "https://open-deep-ml.github.io/DML-OpenProblem/problem-43/index.html"
}
```




### solution.py

```python
import numpy as np


def ridge_loss(X: np.ndarray, w: np.ndarray, y_true: np.ndarray, alpha: float) -> float:
    loss = np.mean((y_true - X @ w) ** 2) + alpha * np.sum(w**2)
    return loss
```




### starter_code.py

```python
import numpy as np


def ridge_loss(X: np.ndarray, w: np.ndarray, y_true: np.ndarray, alpha: float) -> float:
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "X = np.array([[1,1],[2,1],[3,1],[4,1]])\nW = np.array([.2,2])\ny = np.array([2,3,4,5])\nalpha = 0.1\noutput = ridge_loss(X, W, y, alpha)\nprint(output)",
    "expected_output": "2.204"
  },
  {
    "test": "X = np.array([[1,1,4],[2,1,2],[3,1,.1],[4,1,1.2],[1,2,3]])\nW = np.array([.2,2,5])\ny = np.array([2,3,4,5,2])\nalpha = 0.1\noutput = ridge_loss(X, W, y, alpha)\nprint(output)",
    "expected_output": "164.402"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/43_implement-ridge-regression-loss-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/43_implement-ridge-regression-loss-function/description.md)。Deep-ML：Educational Use Only License。
