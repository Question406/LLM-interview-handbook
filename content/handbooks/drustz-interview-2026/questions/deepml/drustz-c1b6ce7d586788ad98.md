---
id: drustz-c1b6ce7d586788ad98
section: deepml
order: 21
level: A
title: Calculate F1 Score from Predicted and True Labels
quick: Deep-ML 练习 · Calculate F1 Score from Predicted and True Labels
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/91_calculate-f1-score-from-predicted-and-true-labels/description.md
    type: primary
---
### description.md

Implement a function to calculate the F1 score given predicted and true labels. The F1 score is a widely used metric in machine learning, combining precision and recall into a single measure. round your solution to the 3rd decimal place


### example.json

```json
{
  "input": "y_true = [1, 0, 1, 1, 0], y_pred = [1, 0, 0, 1, 1]",
  "output": "0.667",
  "reasoning": "The true positives, false positives, and false negatives are calculated from the given labels. Precision and recall are derived, and the F1 score is computed as their harmonic mean."
}
```




### learn.md

## **F1 Score**

The F1 score is a widely used metric in machine learning and statistics, particularly for evaluating classification models. It is the harmonic mean of **precision** and **recall**, providing a single measure that balances the trade-off between these two metrics.

### **Key Concepts**

1. **Precision**: Precision is the fraction of true positive predictions out of all positive predictions made by the model. It measures how many of the predicted positive instances are actually correct.

    $$
    \text{Precision} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Positives (FP)}}
    $$

2. **Recall**: Recall is the fraction of true positive predictions out of all actual positive instances in the dataset. It measures how many of the actual positive instances were correctly predicted.

    $$
    \text{Recall} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Negatives (FN)}}
    $$

3. **F1 Score**: The F1 score is the harmonic mean of precision and recall, providing a balanced measure that takes both metrics into account:

    $$
    \text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
    $$

### **Why Use the F1 Score?**

The F1 score is particularly useful when the dataset is imbalanced, meaning the classes are not equally represented. It provides a single metric that balances the trade-off between precision and recall, especially in scenarios where maximizing one metric might lead to a significant drop in the other.

### **Example Calculation**

Given:
 $y_{true}$  = [1, 0, 1, 1, 0] 


 $y_{pred}$  = [1, 0, 0, 1, 1] 

1. **Calculate True Positives (TP), False Positives (FP), and False Negatives (FN)**:

    $$
    \text{TP} = 2, \quad \text{FP} = 1, \quad \text{FN} = 1
    $$

2. **Calculate Precision**:

    $$
    \text{Precision} = \frac{2}{2 + 1} = \frac{2}{3} \approx 0.667
    $$

3. **Calculate Recall**:

    $$
    \text{Recall} = \frac{2}{2 + 1} = \frac{2}{3} \approx 0.667
    $$

4. **Calculate F1 Score**:

    $$
    \text{F1 Score} = 2 \times \frac{0.667 \times 0.667}{0.667 + 0.667} = 0.667
    $$

### **Applications**

The F1 score is widely used in:
- Binary classification problems (e.g., spam detection, fraud detection).
- Multi-class classification problems (evaluated per class and averaged).
- Information retrieval tasks (e.g., search engines, recommendation systems).

Mastering the F1 score is essential for evaluating and comparing the performance of classification models.


### meta.json

```json
{
  "id": "91",
  "title": "Calculate F1 Score from Predicted and True Labels",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
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
def calculate_f1_score(y_true, y_pred):
    """
    Calculate the F1 score based on true and predicted labels.

    Args:
        y_true (list): True labels (ground truth).
        y_pred (list): Predicted labels.

    Returns:
        float: The F1 score rounded to three decimal places.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("Lengths of y_true and y_pred must be the same")

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    if tp + fp == 0 or tp + fn == 0:
        return 0.0

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    if precision + recall == 0:
        return 0.0

    f1_score = 2 * (precision * recall) / (precision + recall)
    return round(f1_score, 3)
```




### starter_code.py

```python
def calculate_f1_score(y_true, y_pred):
    """
    Calculate the F1 score based on true and predicted labels.

    Args:
            y_true (list): True labels (ground truth).
            y_pred (list): Predicted labels.

    Returns:
            float: The F1 score rounded to three decimal places.
    """
    # Your code here
    pass
    return round(f1, 3)
```




### tests.json

```json
[
  {
    "test": "print(calculate_f1_score([1, 0, 1, 1, 0], [1, 0, 0, 1, 1]))",
    "expected_output": "0.667"
  },
  {
    "test": "print(calculate_f1_score([1, 1, 0, 0], [1, 0, 0, 1]))",
    "expected_output": "0.5"
  },
  {
    "test": "print(calculate_f1_score([0, 0, 0, 0], [1, 1, 1, 1]))",
    "expected_output": "0.0"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/91_calculate-f1-score-from-predicted-and-true-labels/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/91_calculate-f1-score-from-predicted-and-true-labels/description.md)。Deep-ML：Educational Use Only License。
