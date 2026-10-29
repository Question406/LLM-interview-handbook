---
id: drustz-f833dd69cd40ac2594
section: deepml
order: 28
level: A
title: Calculate R-squared for Regression Analysis
quick: Deep-ML 练习 · Calculate R-squared for Regression Analysis
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/69_calculate-r-squared-for-regression-analysis/description.md
    type: primary
---
### description.md


## Task: Compute the R-squared Value in Regression Analysis

- R-squared, also known as the coefficient of determination, is a measure that indicates how well the independent variables explain the variability of the dependent variable in a regression model. 

- **Your Task**: 
    To implement the function `r_squared(y_true, y_pred)` that calculates the R-squared value, given arrays of true values `y_true` and predicted values `y_pred`.


### example.json

```json
{
  "input": "import numpy as np\n\ny_true = np.array([1, 2, 3, 4, 5])\ny_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])\nprint(r_squared(y_true, y_pred))",
  "output": "0.989",
  "reasoning": "The R-squared value is calculated to be 0.989, indicating that the regression model explains 98.9% of the variance in the dependent variable."
}
```




### learn.md


# Understanding R-squared ( $R^{2}$ ) in Regression Analysis

R-squared, also known as the coefficient of determination, is a statistical measure that represents the proportion of the variance for a dependent variable that's explained by an independent variable or variables in a regression model. It provides insight into how well the model fits the data.

### Mathematical Definition

The R-squared value is calculated using the following formula:  
$$
R^2 = 1 - \frac{\text{SSR}}{\text{SST}}
$$
Where:  

1) $ \text{SSR} $ (Sum of Squared Residuals): The sum of the squares of the differences between the actual values and the predicted values.  
2) $ \text{SST} $ (Total Sum of Squares): The sum of the squares of the differences between the actual values and the mean of the actual values.

### Equations for SSR and SST

To calculate SSR and SST, we use the following formulas:  

1) SSR:  
$$
\text{SSR} = \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
$$  

2) SST:  
$$
\text{SST} = \sum_{i=1}^{n} (y_i - \bar{y})^2
$$  

Where:  

1) $ y_i $: Actual value  
2) $ \hat{y}_i $: Predicted value  
3) $ \bar{y} $: Mean of the actual values  

### Significance of R-squared

R-squared is a key metric for evaluating how well a regression model performs. A higher R-squared value indicates a better fit for the model, meaning it can explain more variability in the data. However, it's important to note:  

- A high R-squared does not always imply that the model is good; it can sometimes be misleading if overfitting occurs.  
- It should be used in conjunction with other metrics for comprehensive model evaluation.

### Implementing R-squared Calculation

In this problem, you will implement a function to calculate R-squared given arrays of true and predicted values from a regression task. The results should be rounded to three decimal places.  

In the solution, the implemented $ r\_squared() $ function calculates R-squared by first determining SSR and SST, then applying them to compute $ R^2 $. It handles edge cases such as perfect predictions and situations where all true values are identical.

### Reference

You can refer to this resource for more information:  
[Coefficient of Determination](https://www.ncl.ac.uk/webtemplate/ask-assets/external/maths-resources/statistics/regression-and-correlation/coefficient-of-determination-r-squared.html)


### meta.json

```json
{
  "id": "69",
  "title": "Calculate R-squared for Regression Analysis",
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


def r_squared(y_true, y_pred):
    """
    Calculate the R-squared (R²) coefficient of determination.

    Args:
        y_true (numpy.ndarray): Array of true values
        y_pred (numpy.ndarray): Array of predicted values

    Returns:
        float: R-squared value rounded to 3 decimal places
    """
    if np.array_equal(y_true, y_pred):
        return 1.0

    # Calculate mean of true values
    y_mean = np.mean(y_true)

    # Calculate Sum of Squared Residuals (SSR)
    ssr = np.sum((y_true - y_pred) ** 2)

    # Calculate Total Sum of Squares (SST)
    sst = np.sum((y_true - y_mean) ** 2)

    try:
        # Calculate R-squared
        r2 = 1 - (ssr / sst)
        if np.isinf(r2):
            return 0.0
        return round(r2, 3)
    except ZeroDivisionError:
        return 0.0
```




### starter_code.py

```python
import numpy as np


def r_squared(y_true, y_pred):
    # Write your code here
    pass
```




### tests.json

```json
[
  {
    "test": "\nimport numpy as np\ny_true = np.array([1, 2, 3, 4, 5])\ny_pred = np.array([1, 2, 3, 4, 5])\nprint(r_squared(y_true, y_pred))\n",
    "expected_output": "1.0"
  },
  {
    "test": "\nimport numpy as np\ny_true = np.array([1, 2, 3, 4, 5])\ny_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])\nprint(r_squared(y_true, y_pred))\n",
    "expected_output": "0.989"
  },
  {
    "test": "\nimport numpy as np\ny_true = np.array([1, 2, 3, 4, 5])\ny_pred = np.array([2, 1, 4, 3, 5])\nprint(r_squared(y_true, y_pred))\n",
    "expected_output": "0.6"
  },
  {
    "test": "\nimport numpy as np\ny_true = np.array([1, 2, 3, 4, 5])\ny_pred = np.array([3, 3, 3, 3, 3])\nprint(r_squared(y_true, y_pred))\n",
    "expected_output": "0.0"
  },
  {
    "test": "\nimport numpy as np\ny_true = np.array([1, 2, 3, 4, 5])\ny_pred = np.array([5, 4, 3, 2, 1])\nprint(r_squared(y_true, y_pred))\n",
    "expected_output": "-3.0"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/69_calculate-r-squared-for-regression-analysis/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/69_calculate-r-squared-for-regression-analysis/description.md)。Deep-ML：Educational Use Only License。
