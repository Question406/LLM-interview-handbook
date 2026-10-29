---
id: drustz-078e0eaec945af3fda
section: deepml
order: 25
level: A
title: Calculate Mean Absolute Error (MAE)
quick: Deep-ML 练习 · Calculate Mean Absolute Error (MAE)
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/93_calculate-mean-absolute-error-mae/description.md
    type: primary
---
### description.md

Implement a function to calculate the Mean Absolute Error (MAE) between two arrays of actual and predicted values. The MAE is a metric used to measure the average magnitude of errors in a set of predictions without considering their direction.


### example.json

```json
{
  "input": "y_true = np.array([3, -0.5, 2, 7]), y_pred = np.array([2.5, 0.0, 2, 8])",
  "output": "0.500",
  "reasoning": "The MAE is calculated by taking the mean of the absolute differences between the predicted and true values. Using the formula, the result is 0.500."
}
```




### learn.md

## Mean Absolute Error (MAE)

The Mean Absolute Error (MAE) is a measure of the average magnitude of errors between predicted and actual values. Here's how to express it mathematically:

1. **Basic Formula**:
   - The MAE formula can be written as: $MAE = \frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|$

   Where:
   - $n$ is the number of observations
   - $y_i$ is the true value
   - $\hat{y}_i$ is the predicted value
   - $|...|$ represents the absolute value

2. **Example Calculation**:
   For the values:

```text
y_true = [3, -0.5, 2, 7]
y_pred = [2.5, 0.0, 2, 8]
```




   The calculation would be:
   $$
   \begin{align*}
   MAE &= \frac{1}{4}(|3-2.5| + |-0.5-0.0| + |2-2| + |7-8|) \\
   &= \frac{1}{4}(0.5 + 0.5 + 0 + 1) \\
   &= \frac{2}{4} \\
   &= 0.5
   \end{align*}
   $$

3. **Properties**:
   - MAE is always non-negative: $MAE \geq 0$
   - Perfect predictions result in $MAE = 0$
   - MAE is measured in the same units as the original data
   - MAE treats all errors with equal weight (unlike Mean Squared Error)

4. **Comparison with Other Metrics**:
   The formula for Mean Squared Error (MSE) is:
   $$MSE = \frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2$$

   While MAE uses absolute values, MSE squares the differences, which:
   - Makes MSE more sensitive to outliers
   - Results in MSE values that are not in the original unit of measurement


### meta.json

```json
{
  "id": "93",
  "title": "Calculate Mean Absolute Error (MAE)",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/rittik9",
      "name": "rittik9"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def mae(y_true, y_pred):
    """
    Calculate Mean Absolute Error between two arrays.

    Parameters:
    y_true (numpy.ndarray): Array of true values
    y_pred (numpy.ndarray): Array of predicted values

    Returns:
    float: Mean Absolute Error rounded to 3 decimal places
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Arrays must have the same shape")
    if y_true.size == 0:
        raise ValueError("Arrays cannot be empty")

    return round(np.mean(np.abs(y_true - y_pred)), 3)
```




### starter_code.py

```python
import numpy as np


def mae(y_true, y_pred):
    """
        Calculate Mean Absolute Error between two arrays.

        Parameters:
        y_true (numpy.ndarray): Array of true values
    y_pred (numpy.ndarray): Array of predicted values

        Returns:
        float: Mean Absolute Error rounded to 3 decimal places
    """
    # Your code here
    pass
    return round(val, 3)
```




### tests.json

```json
[
  {
    "test": "print(mae(np.array([3, -0.5, 2, 7]), np.array([2.5, 0.0, 2, 8])))",
    "expected_output": "0.500"
  },
  {
    "test": "print(mae(np.array([[0.5, 1], [-1, 1], [7, -6]]), np.array([[0, 2], [-1, 2], [8, -5]])))",
    "expected_output": "0.750"
  },
  {
    "test": "print(mae(np.array([-1, -2, -3]), np.array([-1.5, -2.2, -2.8])))",
    "expected_output": "0.300"
  },
  {
    "test": "print(mae(np.array([1, -1, 0]), np.array([-1, 1, 0])))",
    "expected_output": "1.333"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/93_calculate-mean-absolute-error-mae/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/93_calculate-mean-absolute-error-mae/description.md)。Deep-ML：Educational Use Only License。
