---
id: drustz-f7f15f1ecbd6008a04
section: deepml
order: 30
level: A
title: Calculate the Phi Coefficient
quick: Deep-ML 练习 · Calculate the Phi Coefficient
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/95_calculate-the-phi-coefficient/description.md
    type: primary
---
### description.md

Implement a function to calculate the Phi coefficient, a measure of the correlation between two binary variables. The function should take two lists of integers (0s and 1s) as input and return the Phi coefficient rounded to 4 decimal places.


### example.json

```json
{
  "input": "phi_corr([1, 1, 0, 0], [0, 0, 1, 1])",
  "output": "-1.0",
  "reasoning": "The Phi coefficient measures the correlation between two binary variables. In this example, the variables have a perfect negative correlation, resulting in a Phi coefficient of -1.0."
}
```




### learn.md

# The Phi coefficient

The Phi coefficient is a type of correlation coefficient , which is used when we need to find the correlation between two binary variables.
For example when we have two variables x and y , x being gender and y signifying the presence of heart disease. 
Both variables are binary and if we need to find a correlation between x and y then we can use the formula below :


$\phi = \frac{(x_{00} \cdot x_{11}) - (x_{01} \cdot x_{10})}{\sqrt{(x_{00} + x_{01})(x_{10} + x_{11})(x_{00} + x_{10})(x_{01} + x_{11})}}$




### Explanation of Terms:
- \(x_00\): The number of cases where \(x = 0\) and \(y = 0\).
- \(x_01\): The number of cases where \(x = 0\) and \(y = 1\).
- \(x_10\): The number of cases where \(x = 1\) and \(y = 0\).
- \(x_11\): The number of cases where \(x = 1\) and \(y = 1\).


### meta.json

```json
{
  "id": "95",
  "title": "Calculate the Phi Coefficient",
  "difficulty": "easy",
  "category": "Statistics",
  "video": "https://youtu.be/z0A4peJnJOs",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Noth2006",
      "name": "Noth2006"
    },
    {
      "profile_link": "https://github.com/Selbl",
      "name": "Selbl"
    }
  ]
}
```




### solution.py

```python
def phi_corr(x: list[int], y: list[int]) -> float:
    """
    Calculate the Phi coefficient between two binary variables.

    Args:
    x (list[int]): A list of binary values (0 or 1).
    y (list[int]): A list of binary values (0 or 1).

    Returns:
    float: The Phi coefficient rounded to 4 decimal places.
    """
    x1y1 = x1y0 = x0y1 = x0y0 = 0

    # Count occurrences
    for i in range(len(x)):
        if x[i] == 1:
            if y[i] == 1:
                x1y1 += 1
            else:
                x1y0 += 1
        elif x[i] == 0:
            if y[i] == 1:
                x0y1 += 1
            else:
                x0y0 += 1

    # Calculate numerator and denominator
    numerator = (x0y0 * x1y1) - (x0y1 * x1y0)
    denominator = ((x0y0 + x0y1) * (x1y0 + x1y1) * (x0y0 + x1y0) * (x0y1 + x1y1)) ** 0.5

    if denominator == 0:
        return 0.0

    phi = numerator / denominator
    return round(phi, 4)
```




### starter_code.py

```python
def phi_corr(x: list[int], y: list[int]) -> float:
    """
    Calculate the Phi coefficient between two binary variables.

    Args:
    x (list[int]): A list of binary values (0 or 1).
    y (list[int]): A list of binary values (0 or 1).

    Returns:
    float: The Phi coefficient rounded to 4 decimal places.
    """
    # Your code here
    pass
    return round(val, 4)
```




### tests.json

```json
[
  {
    "test": "print(phi_corr([1, 1, 0, 0], [0, 0, 1, 1]))",
    "expected_output": "-1.0"
  },
  {
    "test": "print(phi_corr([1, 1, 0, 0], [1, 0, 1, 1]))",
    "expected_output": "-0.5774"
  },
  {
    "test": "print(phi_corr([0, 0, 1, 1], [0, 1, 0, 1]))",
    "expected_output": "0.0"
  },
  {
    "test": "print(phi_corr([1, 0, 1, 0,1,1,0], [1, 1, 0, 0,1,1,1]))",
    "expected_output": "0.0913"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/95_calculate-the-phi-coefficient/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/95_calculate-the-phi-coefficient/description.md)。Deep-ML：Educational Use Only License。
