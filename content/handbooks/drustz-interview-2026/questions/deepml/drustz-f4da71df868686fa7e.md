---
id: drustz-f4da71df868686fa7e
section: deepml
order: 159
level: A
title: Random Shuffle of Dataset
quick: Deep-ML 练习 · Random Shuffle of Dataset
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/29_random-shuffle-of-dataset/description.md
    type: primary
---
### description.md

Write a Python function to perform a random shuffle of the samples in two numpy arrays, X and y, while maintaining the corresponding order between them. The function should have an optional seed parameter for reproducibility.


### example.json

```json
{
  "input": "X = np.array([[1, 2], \n                  [3, 4], \n                  [5, 6], \n                  [7, 8]])\n    y = np.array([1, 2, 3, 4])",
  "output": "(array([[5, 6],\n                    [1, 2],\n                    [7, 8],\n                    [3, 4]]), \n             array([3, 1, 4, 2]))",
  "reasoning": "The samples in X and y are shuffled randomly, maintaining the correspondence between the samples in both arrays."
}
```




### learn.md


## Understanding Dataset Shuffling

Random shuffling of a dataset is a common preprocessing step in machine learning to ensure that the data is randomly distributed before training a model. This helps to avoid any potential biases that may arise from the order in which data is presented to the model.

### Step-by-Step Method to Shuffle a Dataset

1. **Generate a Random Index Array**  
   Create an array of indices corresponding to the number of samples in the dataset.

2. **Shuffle the Indices**  
   Use a random number generator to shuffle the array of indices.

3. **Reorder the Dataset**  
   Use the shuffled indices to reorder the samples in both \( X \) and \( y \).

### Key Point
This method ensures that the correspondence between \( X \) and \( y \) is maintained after shuffling, preserving the relationship between features and labels.


### meta.json

```json
{
  "id": "29",
  "title": "Random Shuffle of Dataset",
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


def shuffle_data(X, y, seed=None):
    if seed:
        np.random.seed(seed)
    idx = np.arange(X.shape[0])
    np.random.shuffle(idx)
    return X[idx], y[idx]
```




### starter_code.py

```python
import numpy as np


def shuffle_data(X, y, seed=None):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(shuffle_data(np.array([[1, 2], [3, 4], [5, 6], [7, 8]]), np.array([1, 2, 3, 4]), seed=42))",
    "expected_output": "(array([[3, 4], [7, 8], [1, 2], [5, 6]]), array([2, 4, 1, 3]))"
  },
  {
    "test": "print(shuffle_data(np.array([[1, 1], [2, 2], [3, 3], [4, 4]]), np.array([10, 20, 30, 40]), seed=24))",
    "expected_output": "(array([[4, 4],[2, 2],[1, 1],[3, 3]]), array([40, 20, 10, 30]))"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/29_random-shuffle-of-dataset/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/29_random-shuffle-of-dataset/description.md)。Deep-ML：Educational Use Only License。
