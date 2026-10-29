---
id: drustz-ca953f38648d3a87df
section: deepml
order: 14
level: A
title: Calculate Accuracy Score
quick: Deep-ML 练习 · Calculate Accuracy Score
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/36_calculate-accuracy-score/description.md
    type: primary
---
### description.md

Write a Python function to calculate the accuracy score of a model's predictions. The function should take in two 1D numpy arrays:  $y_{true}$ , which contains the true labels, and  $y_{pred}$ , which contains the predicted labels. It should return the accuracy score as a float.


### example.json

```json
{
  "input": "y_true = np.array([1, 0, 1, 1, 0, 1])\n    y_pred = np.array([1, 0, 0, 1, 0, 1])\n    output = accuracy_score(y_true, y_pred)\n    print(output)",
  "output": "# 0.8333333333333334",
  "reasoning": "The function compares the true labels with the predicted labels and calculates the ratio of correct predictions to the total number of predictions. In this example, there are 5 correct predictions out of 6, resulting in an accuracy score of 0.8333333333333334."
}
```




### learn.md


## Understanding Accuracy Score

Accuracy is a metric used to evaluate the performance of a classification model. It is defined as the ratio of the number of correct predictions to the total number of predictions made. Mathematically, accuracy is given by:
$$
\text{Accuracy} = \frac{\text{Number of Correct Predictions}}{\text{Total Number of Predictions}}
$$

### Problem Overview
In this problem, you will write a function to calculate the accuracy score given the true labels and the predicted labels. The function will compare the two arrays and compute the accuracy as the proportion of matching elements.

### Importance
Accuracy is a straightforward and commonly used metric for classification tasks. It provides a quick way to understand how well a model is performing, but it may not always be the best metric, especially for imbalanced datasets.


### meta.json

```json
{
  "id": "36",
  "title": "Calculate Accuracy Score",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/eriklindernoren/ML-From-Scratch",
      "name": "Erik Linder-Nor\u00e9n"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def accuracy_score(y_true, y_pred):
    accuracy = np.sum(y_true == y_pred, axis=0) / len(y_true)
    return accuracy
```




### starter_code.py

```python
import numpy as np


def accuracy_score(y_true, y_pred):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(accuracy_score(np.array([1, 0, 1, 1, 0, 1]), np.array([1, 0, 0, 1, 0, 1])))",
    "expected_output": "0.8333333333333334"
  },
  {
    "test": "print(accuracy_score(np.array([1, 1, 1, 1]), np.array([1, 0, 1, 0])))",
    "expected_output": "0.5"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/36_calculate-accuracy-score/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/36_calculate-accuracy-score/description.md)。Deep-ML：Educational Use Only License。
