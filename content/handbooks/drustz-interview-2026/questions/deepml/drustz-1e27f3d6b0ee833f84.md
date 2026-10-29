---
id: drustz-1e27f3d6b0ee833f84
section: deepml
order: 94
level: A
title: Implement Gini Impurity Calculation for a Set of Classes
quick: Deep-ML 练习 · Implement Gini Impurity Calculation for a Set of Classes
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/64_implement-gini-impurity-calculation-for-a-set-of-c/description.md
    type: primary
---
### description.md

## Task: Implement Gini Impurity Calculation

Your task is to implement a function that calculates the Gini Impurity for a set of classes. Gini impurity is commonly used in decision tree algorithms to measure the impurity or disorder within a node.


### example.json

```json
{
  "input": "y = [0, 1, 1, 1, 0]\nprint(gini_impurity(y))",
  "output": "0.48",
  "reasoning": "The Gini Impurity is calculated as 1 - (p_0^2 + p_1^2), where p_0 and p_1 are the probabilities of each class. In this case, p_0 = 2/5 and p_1 = 3/5, resulting in a Gini Impurity of 0.48."
}
```




### learn.md


## Understanding Gini Impurity

Gini impurity is a statistical measurement of the impurity or disorder in a list of elements. It is commonly used in decision tree algorithms to decide the optimal split at tree nodes. It is calculated as follows, where $ p_i $ is the probability of each class, $ \frac{n_i}{n} $:

$$
\text{Gini Impurity} = 1 - \sum_{i=1}^{C} p_i^2
$$

A Gini impurity of 0 indicates a node where all elements belong to the same class, whereas a Gini impurity of 1-1/C indicates maximum impurity, where elements are evenly distributed among each class. This means that a lower impurity implies a less homogeneous distribution of elements, suggesting a good split, as decision trees aim to minimize it at each node.

### Advantages and Limitations

#### Advantages:
- Computationally efficient
- Works for binary and multi-class classification

#### Limitations:
- Biased toward larger classes
- May cause overfitting in deep decision trees

### Example Calculation

Suppose we have the set: $[0, 1, 1, 1, 0]$. The probability of each class is calculated as follows:

$$
p_{0} = \frac{2}{5} \quad p_{1} = \frac{3}{5}
$$

The Gini Impurity is then calculated as follows:

$$
\text{Gini Impurity} = 1 - (p_0^2 + p_1^2) = 1 - \left(\left(\frac{2}{5}\right)^2 + \left(\frac{3}{5}\right)^2\right) = 0.48
$$


### meta.json

```json
{
  "id": "64",
  "title": "Implement Gini Impurity Calculation for a Set of Classes",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/paddywardle",
      "name": "paddywardle"
    },
    {
      "profile_link": "https://github.com/ianxek",
      "name": "ianxek"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def gini_impurity(y: list[int]) -> float:

    classes = set(y)
    n = len(y)

    gini_impurity = 0

    for cls in classes:
        gini_impurity += (y.count(cls) / n) ** 2

    return round(1 - gini_impurity, 3)
```




### starter_code.py

```python
import numpy as np


def gini_impurity(y):
    """
    Calculate Gini Impurity for a list of class labels.

    :param y: List of class labels
    :return: Gini Impurity rounded to three decimal places
    """
    pass
    return round(val, 3)
```




### tests.json

```json
[
  {
    "test": "y = [0, 0, 0, 0, 1, 1, 1, 1]\nprint(gini_impurity(y))",
    "expected_output": "0.5"
  },
  {
    "test": "y = [0, 0, 0, 0, 0, 1]\nprint(gini_impurity(y))",
    "expected_output": "0.278"
  },
  {
    "test": "y = [0, 1, 2, 2, 2, 1, 2]\nprint(gini_impurity(y))",
    "expected_output": "0.571"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/64_implement-gini-impurity-calculation-for-a-set-of-c/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/64_implement-gini-impurity-calculation-for-a-set-of-c/description.md)。Deep-ML：Educational Use Only License。
