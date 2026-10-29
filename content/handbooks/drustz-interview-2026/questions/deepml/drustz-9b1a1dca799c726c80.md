---
id: drustz-9b1a1dca799c726c80
section: deepml
order: 58
level: A
title: Divide Dataset Based on Feature Threshold
quick: Deep-ML 练习 · Divide Dataset Based on Feature Threshold
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/31_divide-dataset-based-on-feature-threshold/description.md
    type: primary
---
### description.md

Write a Python function to divide a dataset based on whether the value of a specified feature is greater than or equal to a given threshold. The function should return two subsets of the dataset: one with samples that meet the condition and another with samples that do not.


### example.json

```json
{
  "input": "X = np.array([[1, 2], \n                  [3, 4], \n                  [5, 6], \n                  [7, 8], \n                  [9, 10]])\n    feature_i = 0\n    threshold = 5",
  "output": "[array([[ 5,  6],\n                    [ 7,  8],\n                    [ 9, 10]]), \n             array([[1, 2],\n                    [3, 4]])]",
  "reasoning": "The dataset X is divided based on whether the value in the 0th feature (first column) is greater than or equal to 5. Samples with the first column value >= 5 are in the first subset, and the rest are in the second subset."
}
```




### learn.md


## Understanding Dataset Division Based on Feature Threshold

Dividing a dataset based on a feature threshold is a common operation in machine learning, especially in decision tree algorithms. This technique helps in creating splits that can be used for further processing or model training.

### Problem Overview
In this problem, you will write a function to split a dataset based on whether the value of a specified feature is greater than or equal to a given threshold. You'll need to create two subsets:
- One for samples that meet the condition (values greater than or equal to the threshold).
- Another for samples that do not meet the condition.

### Importance
This method is crucial for algorithms that rely on data partitioning, such as decision trees and random forests. By splitting the data, the model can create rules to make predictions based on the threshold values of certain features.


### meta.json

```json
{
  "id": "31",
  "title": "Divide Dataset Based on Feature Threshold",
  "difficulty": "medium",
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


def divide_on_feature(X, feature_i, threshold):
    # Define the split function based on the threshold type
    split_func = None
    if isinstance(threshold, int) or isinstance(threshold, float):
        # For numeric threshold, check if feature value is greater than or equal to the threshold
        split_func = lambda sample: sample[feature_i] >= threshold
    else:
        # For non-numeric threshold, check if feature value is equal to the threshold
        split_func = lambda sample: sample[feature_i] == threshold

    # Create two subsets based on the split function
    X_1 = np.array([sample for sample in X if split_func(sample)])
    X_2 = np.array([sample for sample in X if not split_func(sample)])

    # Return the two subsets
    return [X_1, X_2]
```




### starter_code.py

```python
import numpy as np


def divide_on_feature(X, feature_i, threshold):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(divide_on_feature(np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]), 0, 5))",
    "expected_output": "[array([[ 5,  6], [ 7,  8], [ 9, 10]]), array([[1, 2], [3, 4]])]"
  },
  {
    "test": "print(divide_on_feature(np.array([[1, 1], [2, 2], [3, 3], [4, 4]]), 1, 3))",
    "expected_output": "[array([[3, 3], [4, 4]]), array([[1, 1], [2, 2]])]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/31_divide-dataset-based-on-feature-threshold/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/31_divide-dataset-based-on-feature-threshold/description.md)。Deep-ML：Educational Use Only License。
