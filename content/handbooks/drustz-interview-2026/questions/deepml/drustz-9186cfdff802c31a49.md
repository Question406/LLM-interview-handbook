---
id: drustz-9186cfdff802c31a49
section: deepml
order: 108
level: A
title: Implement Recall Metric in Binary Classification
quick: Deep-ML 练习 · Implement Recall Metric in Binary Classification
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/52_implement-recall-metric-in-binary-classification/description.md
    type: primary
---
### description.md

## Task: Implement Recall in Binary Classification

Your task is to implement the **recall** metric in a binary classification setting. Recall is a performance measure that evaluates how effectively a machine learning model identifies positive instances from all the actual positive cases in a dataset.

You need to write a function `recall(y_true, y_pred)` that calculates the recall metric. The function should accept two inputs:

- `y_true`: A list of true binary labels (0 or 1) for the dataset.
- `y_pred`: A list of predicted binary labels (0 or 1) from the model.

Your function should return the recall value rounded to three decimal places. If the denominator (TP + FN) is zero, the recall should be 0.0 to avoid division by zero.

    


### example.json

```json
{
  "input": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 0, 0, 1])\n\nprint(recall(y_true, y_pred))",
  "output": "# 0.75",
  "reasoning": "The recall value for the given true labels and predicted labels is 0.75. The model correctly identified 3 out of 4 positive instances in the dataset."
}
```




### learn.md


## Understanding Recall in Classification

Recall is a metric that measures how often a machine learning model correctly identifies positive instances, also known as true positives, from all the actual positive samples in the dataset.

### Mathematical Definition

Recall, also known as sensitivity, is the fraction of relevant instances that were retrieved. It is calculated using the following equation:
$$
\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}
$$

Where:
1. **True Positives (TP)**: The number of positive samples that are correctly identified as positive.
2. **False Negatives (FN)**: The number of positive samples that are incorrectly identified as negative.

### Task

In this problem, you will implement a function to calculate recall given the true labels and predicted labels of a binary classification task. The results should be rounded to three decimal places.


### meta.json

```json
{
  "id": "52",
  "title": "Implement Recall Metric in Binary Classification",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/rafaelgreca",
      "name": "Rafael Greca"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def recall(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    try:
        return round(tp / (tp + fn), 3)
    except ZeroDivisionError:
        return 0.0
```




### starter_code.py

```text
import numpy as np
def recall(y_true, y_pred):
```




### tests.json

```json
[
  {
    "test": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 0, 0, 1])\nprint(recall(y_true, y_pred))",
    "expected_output": "0.75"
  },
  {
    "test": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 0])\ny_pred = np.array([1, 0, 0, 0, 0, 1])\nprint(recall(y_true, y_pred))",
    "expected_output": "0.333"
  },
  {
    "test": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 0])\ny_pred = np.array([1, 0, 1, 1, 0, 0])\nprint(recall(y_true, y_pred))",
    "expected_output": "1.0"
  },
  {
    "test": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([0, 0, 0, 1, 0, 1])\nprint(recall(y_true, y_pred))",
    "expected_output": "0.5"
  },
  {
    "test": "import numpy as np\n\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([0, 1, 0, 0, 1, 0])\nprint(recall(y_true, y_pred))",
    "expected_output": "0.0"
  }
]
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/52_implement-recall-metric-in-binary-classification/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/52_implement-recall-metric-in-binary-classification/description.md)。Deep-ML：Educational Use Only License。
