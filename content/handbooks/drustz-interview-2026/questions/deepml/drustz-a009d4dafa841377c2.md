---
id: drustz-a009d4dafa841377c2
section: deepml
order: 74
level: A
title: Generate a Confusion Matrix for Binary Classification
quick: Deep-ML 练习 · Generate a Confusion Matrix for Binary Classification
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/75_generate-a-confusion-matrix-for-binary-classificat/description.md
    type: primary
---
### description.md


## Task: Generate a Confusion Matrix

Your task is to implement the function `confusion_matrix(data)` that generates a confusion matrix for a binary classification problem. The confusion matrix provides a summary of the prediction results on a classification problem, allowing you to visualize how many data points were correctly or incorrectly labeled.

### Input:
- A list of lists, where each inner list represents a pair 
- `[y_true, y_pred]` for one observation. `y_true` is the actual label, and `y_pred` is the predicted label.

### Output:
- A $2 \times 2$ confusion matrix represented as a list of lists.


### example.json

```json
{
  "input": "data = [[1, 1], [1, 0], [0, 1], [0, 0], [0, 1]]\nprint(confusion_matrix(data))",
  "output": "[[1, 1], [2, 1]]",
  "reasoning": "The confusion matrix shows the counts of true positives, false negatives, false positives, and true negatives."
}
```




### learn.md


## Generate Confusion Matrix

The confusion matrix is a very useful tool to get a better understanding of the performance of a classification model. In it, you can visualize how many data points were labeled according to their correct categories.

For a binary classification problem of a dataset with $ n $ observations, the confusion matrix is a $ 2 \times 2 $ matrix with the following structure:

$$
M = \begin{pmatrix} 
TP & FN \\
FP & TN
\end{pmatrix}
$$

Where:

- **TP**: True positives, the number of observations from the positive label that were correctly labeled as positive.
- **FN**: False negatives, the number of observations from the positive label that were incorrectly labeled as negative.
- **FP**: False positives, the number of observations from the negative label that were incorrectly labeled as positive.
- **TN**: True negatives, the number of observations from the negative label that were correctly labeled as negative.

A confusion matrix is a great starting point for computing more advanced metrics such as precision and recall that capture the model's performance.


### meta.json

```json
{
  "id": "75",
  "title": "Generate a Confusion Matrix for Binary Classification",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "https://youtu.be/0n7dGmp0xUE",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Selbl",
      "name": "Selbl"
    },
    {
      "profile_link": "https://www.youtube.com/@StoatScript/videos",
      "name": "StoatScript"
    }
  ],
  "marimo_link": "https://open-deep-ml.github.io/DML-OpenProblem/problem-75"
}
```




### solution.py

```python
from collections import Counter


def confusion_matrix(data):
    # Count all occurrences
    counts = Counter(tuple(pair) for pair in data)
    # Get metrics
    TP, FN, FP, TN = counts[(1, 1)], counts[(1, 0)], counts[(0, 1)], counts[(0, 0)]
    # Define matrix and return
    confusion_matrix = [[TP, FN], [FP, TN]]
    return confusion_matrix
```




### starter_code.py

```python
from collections import Counter


def confusion_matrix(data):
    # Implement the function here
    pass
```




### tests.json

```json
[
  {
    "test": "\ndata = [[1, 1], [1, 0], [0, 1], [0, 0], [0, 1]]\nprint(confusion_matrix(data))\n",
    "expected_output": "[[1, 1], [2, 1]]"
  },
  {
    "test": "\ndata = [[0, 1], [1, 0], [1, 1], [0, 1], [0, 0], [1, 0], [0, 1], [1, 1], [0, 0], [1, 0], [1, 1], [0, 0], [1, 0], [0, 1], [1, 1], [1, 1], [1, 0]]\nprint(confusion_matrix(data))\n",
    "expected_output": "[[5, 5], [4, 3]]"
  },
  {
    "test": "\ndata = [[0, 1], [0, 1], [0, 0], [0, 1], [0, 0], [0, 1], [0, 1], [0, 0], [1, 0], [0, 1], [1, 0], [0, 0], [0, 1], [0, 1], [0, 1], [1, 0]]\nprint(confusion_matrix(data))\n",
    "expected_output": "[[0, 3], [9, 4]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/75_generate-a-confusion-matrix-for-binary-classificat/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/75_generate-a-confusion-matrix-for-binary-classificat/description.md)。Deep-ML：Educational Use Only License。
