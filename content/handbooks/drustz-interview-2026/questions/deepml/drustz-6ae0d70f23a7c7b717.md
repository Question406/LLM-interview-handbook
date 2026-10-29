---
id: drustz-6ae0d70f23a7c7b717
section: deepml
order: 27
level: A
title: Calculate Performance Metrics for a Classification Model
quick: Deep-ML 练习 · Calculate Performance Metrics for a Classification Model
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/77_calculate-performance-metrics-for-a-classification/description.md
    type: primary
---
### description.md


### Task: Implement Performance Metrics Calculation

In this task, you are required to implement a function `performance_metrics(actual, predicted)` that computes various performance metrics for a binary classification problem. These metrics include:

- Confusion Matrix
- Accuracy
- F1 Score
- Specificity
- Negative Predictive Value

The function should take in two lists:

- `actual`: The actual class labels (1 for positive, 0 for negative).
- `predicted`: The predicted class labels from the model.

### Output

The function should return a tuple containing:

1. `confusion_matrix`: A 2x2 matrix.
2. `accuracy`: A float representing the accuracy of the model.
3. `f1_score`: A float representing the F1 score of the model.
4. `specificity`: A float representing the specificity of the model.
5. `negative_predictive_value`: A float representing the negative predictive value.

### Constraints

- All elements in the `actual` and `predicted` lists must be either 0 or 1.
- Both lists must have the same length.


### example.json

```json
{
  "input": "actual = [1, 0, 1, 0, 1]\npredicted = [1, 0, 0, 1, 1]\nprint(performance_metrics(actual, predicted))",
  "output": "([[2, 1], [1, 1]], 0.6, 0.667, 0.5, 0.5)",
  "reasoning": "The function calculates the confusion matrix, accuracy, F1 score, specificity, and negative predictive value based on the input labels. The resulting values are rounded to three decimal places as required."
}
```




### learn.md


## Performance Metrics

Performance metrics such as accuracy, F1 score, specificity, negative predictive value, precision, and recall are vital to understanding how a model is performing.

How many observations are correctly labeled? Are we mislabeling one category more than the other? Performance metrics can answer these questions and provide an idea of where to focus to improve a model's performance.

For this problem, starting with the confusion matrix is a helpful first step, as all the elements of the confusion matrix can help with calculating other performance metrics.

For a binary classification problem of a dataset with $n$ observations, the confusion matrix is a $2 \times 2$ matrix with the following structure:

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

### Metrics

#### Accuracy
How many observations are labeled as the actual category they belong to?

$$
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
$$

#### Precision
How many elements labeled as positive are actually positive?

$$
\text{Precision} = \frac{TP}{TP + FP}
$$

#### Negative Predictive Value
How many elements labeled as negative are actually negative?

$$
\text{Negative Predictive Value} = \frac{TN}{TN + FN}
$$

#### Recall
Out of all positive elements, how many were correctly labeled?

$$
\text{Recall} = \frac{TP}{TP + FN}
$$

#### Specificity
How well are we labeling the negative elements correctly?

$$
\text{Specificity} = \frac{TN}{TN + FP}
$$

#### F1 Score
How to account for the trade-off of false negatives and positives? The F1 score is the harmonic mean of precision and recall.

$$
\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
$$


### meta.json

```json
{
  "id": "77",
  "title": "Calculate Performance Metrics for a Classification Model",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "https://youtu.be/W9YoUBZApcA?si=I8FTWXfH3EugaZhc",
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
  ]
}
```




### solution.py

```python
from collections import Counter


def performance_metrics(actual: list[int], predicted: list[int]) -> tuple:
    data = list(zip(actual, predicted))
    counts = Counter(tuple(pair) for pair in data)
    TP, FN, FP, TN = counts[(1, 1)], counts[(1, 0)], counts[(0, 1)], counts[(0, 0)]
    confusion_matrix = [[TP, FN], [FP, TN]]
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1 = 2 * precision * recall / (precision + recall)
    negativePredictive = TN / (TN + FN)
    specificity = TN / (TN + FP)
    return (
        confusion_matrix,
        round(accuracy, 3),
        round(f1, 3),
        round(specificity, 3),
        round(negativePredictive, 3),
    )
```




### starter_code.py

```python
def performance_metrics(actual: list[int], predicted: list[int]) -> tuple:
    # Implement your code here
    return (
        confusion_matrix,
        round(accuracy, 3),
        round(f1, 3),
        round(specificity, 3),
        round(negativePredictive, 3),
    )
```




### tests.json

```json
[
  {
    "test": "\nactual = [1, 0, 1, 0, 1]\npredicted = [1, 0, 0, 1, 1]\nprint(performance_metrics(actual, predicted))\n",
    "expected_output": "([[2, 1], [1, 1]], 0.6, 0.667, 0.5, 0.5)"
  },
  {
    "test": "actual = [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1]\npredicted = [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0]\nprint(performance_metrics(actual, predicted))",
    "expected_output": "([[6, 4], [2, 7]], 0.684, 0.667, 0.778, 0.636)"
  },
  {
    "test": "actual = [0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0]\npredicted = [1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1]\nprint(performance_metrics(actual, predicted))",
    "expected_output": "([[4, 4], [5, 2]], 0.4, 0.471, 0.286, 0.333)"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/77_calculate-performance-metrics-for-a-classification/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/77_calculate-performance-metrics-for-a-classification/description.md)。Deep-ML：Educational Use Only License。
