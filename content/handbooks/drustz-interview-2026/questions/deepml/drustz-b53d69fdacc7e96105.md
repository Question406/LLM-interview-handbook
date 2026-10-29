---
id: drustz-b53d69fdacc7e96105
section: deepml
order: 106
level: A
title: Implement Precision Metric
quick: Deep-ML 练习 · Implement Precision Metric
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/46_implement-precision-metric/description.md
    type: primary
---
### description.md

Write a Python function `precision` that calculates the precision metric given two numpy arrays: `y_true` and `y_pred`. The `y_true` array contains the true binary labels, and the `y_pred` array contains the predicted binary labels. Precision is defined as the ratio of true positives to the sum of true positives and false positives.


### example.json

```json
{
  "input": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 0, 0, 1])\n\nresult = precision(y_true, y_pred)\nprint(result)",
  "output": "1.0",
  "reasoning": "- True Positives (TP) = 3\n- False Positives (FP) = 0\n- Precision = TP / (TP + FP) = 3 / (3 + 0) = 1.0"
}
```




### learn.md


## Understanding Precision in Classification

Precision is a key metric used in the evaluation of classification models, particularly in binary classification. It provides insight into the accuracy of the positive predictions made by the model.

### Mathematical Definition
Precision is defined as the ratio of true positives (TP) to the sum of true positives and false positives (FP):
$$
\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}
$$

Where:
- **True Positives (TP)**: The number of positive samples that are correctly identified as positive.
- **False Positives (FP)**: The number of negative samples that are incorrectly identified as positive.

### Characteristics of Precision
- **Range**: Precision ranges from 0 to 1, where 1 indicates perfect precision (no false positives) and 0 indicates no true positives.
- **Interpretation**: High precision means that the model has a low false positive rate, meaning it rarely labels negative samples as positive.
- **Use Case**: Precision is particularly useful when the cost of false positives is high, such as in medical diagnosis or fraud detection.

In this problem, you will implement a function to calculate precision given the true labels and predicted labels of a binary classification task.


### meta.json

```json
{
  "id": "46",
  "title": "Implement Precision Metric",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "https://youtu.be/u99yBNF4vE0",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def precision(y_true, y_pred):
    true_positives = np.sum((y_true == 1) & (y_pred == 1))
    false_positives = np.sum((y_true == 0) & (y_pred == 1))
    return (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )
```




### starter_code.py

```python
import numpy as np


def precision(y_true, y_pred):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 0, 0, 1])\nresult = precision(y_true, y_pred)\nprint(result)",
    "expected_output": "1.0"
  },
  {
    "test": "import numpy as np\ny_true = np.array([1, 0, 1, 1, 0, 0])\ny_pred = np.array([1, 0, 0, 0, 0, 1])\nresult = precision(y_true, y_pred)\nprint(result)",
    "expected_output": "0.5"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/46_implement-precision-metric/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/46_implement-precision-metric/description.md)。Deep-ML：Educational Use Only License。
