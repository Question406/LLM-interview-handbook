---
id: drustz-96fbddc2c29986f1f2
section: deepml
order: 56
level: A
title: Detect Overfitting or Underfitting
quick: Deep-ML 练习 · Detect Overfitting or Underfitting
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/86_detect-overfitting-or-underfitting/description.md
    type: primary
---
### description.md

Write a Python function to determine whether a machine learning model is overfitting, underfitting, or performing well based on training and test accuracy values. The function should take two inputs: `training_accuracy` and `test_accuracy`. It should return one of three values: 1 if Overfitting, -1 if Underfitting, or 0 if a Good fit. The rules for determination are as follows: 
- **Overfitting**: The training accuracy is significantly higher than the test accuracy (difference > 0.2).
- **Underfitting**: Both training and test accuracy are below 0.7.
- **Good fit**: Neither of the above conditions is true.


### example.json

```json
{
  "input": "training_accuracy = 0.95, test_accuracy = 0.65",
  "output": "'1'",
  "reasoning": "The training accuracy is much higher than the test accuracy (difference = 0.30 > 0.2). This indicates that the model is overfitting to the training data and generalizes poorly to unseen data."
}
```




### learn.md

## Understanding Overfitting and Underfitting

Overfitting and underfitting are two common problems in machine learning models that affect their performance and generalization ability.

### Overfitting
Overfitting occurs when a model learns the training data too well, including noise and irrelevant patterns. This results in high training accuracy but poor performance on unseen data (low test accuracy).

- **Indicators**: Training accuracy >> Test accuracy (large gap).

### Underfitting
Underfitting occurs when a model is too simple to capture the underlying patterns in the data. This leads to poor performance on both training and test datasets.

- **Indicators**: Both training and test accuracy are low.

### Good Fit
A good fit occurs when the model generalizes well to unseen data, with training and test accuracy being close and both reasonably high.

### Remedies
- **For Overfitting**:
  - Use regularization techniques (e.g., L1, L2 regularization).
  - Reduce model complexity by pruning unnecessary features.
  - Add more training data to improve generalization.
- **For Underfitting**:
  - Increase model complexity (e.g., add layers or features).
  - Train the model for more epochs.
  - Enhance feature engineering or input data quality.

### Mathematical Representation
1. Overfitting:
   $$ \text{Training Accuracy} - \text{Test Accuracy} > 0.2 $$

2. Underfitting:
   $$ \text{Training Accuracy} < 0.7 \, \text{and} \, \text{Test Accuracy} < 0.7 $$

3. Good Fit:
   $$ \text{Neither overfitting nor underfitting is true.} $$


### meta.json

```json
{
  "id": "86",
  "title": "Detect Overfitting or Underfitting",
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
def model_fit_quality(training_accuracy, test_accuracy):
    """
    Determine if the model is overfitting, underfitting, or a good fit based on training and test accuracy.
    :param training_accuracy: float, training accuracy of the model (0 <= training_accuracy <= 1)
    :param test_accuracy: float, test accuracy of the model (0 <= test_accuracy <= 1)
    :return: int, one of '1', '-1', or '0'.
    """
    if training_accuracy - test_accuracy > 0.2:
        return 1
    elif training_accuracy < 0.7 and test_accuracy < 0.7:
        return -1
    else:
        return 0
```




### starter_code.py

```python
def model_fit_quality(training_accuracy, test_accuracy):
    """
    Determine if the model is overfitting, underfitting, or a good fit based on training and test accuracy.
    :param training_accuracy: float, training accuracy of the model (0 <= training_accuracy <= 1)
    :param test_accuracy: float, test accuracy of the model (0 <= test_accuracy <= 1)
    :return: int, one of '1', '-1', or '0'.
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(model_fit_quality(0.95, 0.65))",
    "expected_output": "1"
  },
  {
    "test": "print(model_fit_quality(0.6, 0.5))",
    "expected_output": "-1"
  },
  {
    "test": "print(model_fit_quality(0.85, 0.8))",
    "expected_output": "0"
  },
  {
    "test": "print(model_fit_quality(0.5, 0.6))",
    "expected_output": "-1"
  },
  {
    "test": "print(model_fit_quality(0.75, 0.74))",
    "expected_output": "0"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/86_detect-overfitting-or-underfitting/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/86_detect-overfitting-or-underfitting/description.md)。Deep-ML：Educational Use Only License。
