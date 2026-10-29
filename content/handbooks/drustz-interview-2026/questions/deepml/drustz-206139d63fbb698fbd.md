---
id: drustz-206139d63fbb698fbd
section: deepml
order: 43
level: A
title: Deep-ML legacy · 135 early stopping
quick: Deep-ML 练习 · Deep-ML legacy · 135 early stopping
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/135_early_stopping/learn.md
    type: primary
---
### learn.md

## Implementing Early Stopping Criterion

Early stopping is a regularization technique that helps prevent overfitting in machine learning models. Your task is to implement the early stopping decision logic based on the validation loss history.

### Problem Description

Given a sequence of validation losses from model training, determine if training should be stopped based on the following criteria:

- Training should stop if the validation loss hasn't improved (decreased) for a specified number of epochs (patience)
- An improvement is only counted if the loss decreases by more than a minimum threshold (min_delta)
- The best model is the one with the lowest validation loss

### Example

Consider the following validation losses: [0.9, 0.8, 0.75, 0.77, 0.76, 0.77, 0.78]

- With patience=2 and min_delta=0.01:
  - Best loss is 0.75 at epoch 2
  - No improvement > 0.01 for next 2 epochs
  - Should stop at epoch 4

### Function Requirements

- Return both the epoch to stop at and the best epoch
- If no stopping is needed, return the last epoch
- Epochs are 0-indexed


### solution.py

```python
import numpy as np
from typing import Tuple


def early_stopping(
    val_losses: list[float], patience: int, min_delta: float
) -> Tuple[int, int]:

    best_loss = float('inf')
    best_epoch = 0
    epochs_without_improvement = 0

    for epoch, loss in enumerate(val_losses):
        # Check if current loss is better than best loss by at least min_delta
        if loss < best_loss - min_delta:
            best_loss = loss
            best_epoch = epoch
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        # Check if we should stop
        if epochs_without_improvement >= patience:
            return epoch, best_epoch

    # If we never hit the patience threshold, return the last epoch
    return len(val_losses) - 1, best_epoch


def test_early_stopping():

    losses1 = [0.9, 0.8, 0.75, 0.77, 0.76, 0.77, 0.78]
    stop_epoch1, best_epoch1 = early_stopping(losses1, patience=2, min_delta=0.01)
    assert stop_epoch1 == 4 and best_epoch1 == 2, "Test case 1 failed"

    losses2 = [0.9, 0.8, 0.7, 0.6, 0.5]
    stop_epoch2, best_epoch2 = early_stopping(losses2, patience=2, min_delta=0.01)
    assert stop_epoch2 == 4 and best_epoch2 == 4, "Test case 2 failed"

    losses3 = [0.9, 0.8, 0.79, 0.78, 0.77]
    stop_epoch3, best_epoch3 = early_stopping(losses3, patience=2, min_delta=0.1)
    assert stop_epoch3 == 4 and best_epoch3 == 2, "Test case 3 failed"

    losses4 = [0.5, 0.4]
    stop_epoch4, best_epoch4 = early_stopping(losses4, patience=3, min_delta=0.01)
    assert stop_epoch4 == 1 and best_epoch4 == 1, "Test case 4 failed"

    losses5 = [0.5, 0.4, 0.4, 0.4, 0.4]
    stop_epoch5, best_epoch5 = early_stopping(losses5, patience=2, min_delta=0.01)
    assert stop_epoch5 == 3 and best_epoch5 == 1, "Test case 5 failed"


if __name__ == "__main__":
    test_early_stopping()
    print("All test cases passed!")
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/Problems/135_early_stopping/learn.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/135_early_stopping/learn.md)。Deep-ML：Educational Use Only License。
