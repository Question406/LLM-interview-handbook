---
id: drustz-358a7cf8a25c6fcb8e
section: deepml
order: 75
level: A
title: Generate Random Subsets of a Dataset
quick: Deep-ML 练习 · Generate Random Subsets of a Dataset
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/33_generate-random-subsets-of-a-dataset/description.md
    type: primary
---
### description.md

Write a Python function to generate random subsets of a given dataset. The function should take in a 2D numpy array X, a 1D numpy array y, an integer  $n_{subsets}$ , and a boolean replacements. It should return a list of  $n_{subsets}$  random subsets of the dataset, where each subset is a tuple of ( $X_{subset}$ ,  $y_{subset}$ ). If replacements is True, the subsets should be created with replacements; otherwise, without replacements.


### example.json

```json
{
  "input": "X = np.array([[1, 2],\n                  [3, 4],\n                  [5, 6],\n                  [7, 8],\n                  [9, 10]])\n    y = np.array([1, 2, 3, 4, 5])\n    n_subsets = 3\n    replacements = False\n    get_random_subsets(X, y, n_subsets, replacements)",
  "output": "[array([[7, 8],\n            [1, 2]]), \n     array([4, 1])]\n     \n    [array([[9, 10],\n            [5, 6]]), \n     array([5, 3])]\n     \n    [array([[3, 4],\n            [5, 6]]), \n     array([2, 3])]",
  "reasoning": "The function generates three random subsets of the dataset without replacements.\n    Each subset includes 50% of the samples (since replacements=False). The samples\n    are randomly selected without duplication."
}
```




### learn.md


## Understanding Random Subsets of a Dataset

Generating random subsets of a dataset is a useful technique in machine learning, particularly in ensemble methods like bagging and random forests. By creating random subsets, models can be trained on different parts of the data, which helps in reducing overfitting and improving generalization.

### Problem Overview
In this problem, you will write a function to generate random subsets of a given dataset. Specifically:
- Given a 2D numpy array $X$, a 1D numpy array $y$, an integer `n_subsets`, and a boolean `replacements`, the function will create a list of `n_subsets` random subsets.
- Each subset will be a tuple of $(X_{\text{subset}}, y_{\text{subset}})$.

### Parameters
- **$X$**: A 2D numpy array representing the features.
- **$y$**: A 1D numpy array representing the labels.
- **$n_{\text{subsets}}$**: The number of random subsets to generate.
- **`replacements`**: A boolean indicating whether to sample with or without replacement.
  - If `replacements` is **True**, subsets will be created *with* replacements, meaning samples can be repeated within a subset.
  - If `replacements` is **False**, subsets will be created *without* replacements, meaning samples cannot be repeated within a subset.

### Importance
By understanding and implementing this technique, you can enhance the performance of your models through methods like bootstrapping and ensemble learning.


### meta.json

```json
{
  "id": "33",
  "title": "Generate Random Subsets of a Dataset",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/peppermin-t",
      "name": "Yinjia Chen"
    },
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


def get_random_subsets(X, y, n_subsets, replacements=True, seed=42):
    np.random.seed(seed)

    n, m = X.shape

    subset_size = n if replacements else n // 2
    idx = np.array(
        [
            np.random.choice(n, subset_size, replace=replacements)
            for _ in range(n_subsets)
        ]
    )
    # convert all ndarrays to lists
    return [(X[idx][i].tolist(), y[idx][i].tolist()) for i in range(n_subsets)]
```




### starter_code.py

```python
import numpy as np


def get_random_subsets(X, y, n_subsets, replacements=True, seed=42):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": " \nX = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])\ny = np.array([1, 2, 3, 4, 5])\nprint(get_random_subsets(X,y, 3, False, seed=42))",
    "expected_output": "[[[3, 4], [9, 10]], [2, 5], [[7, 8], [3, 4]], [4, 2], [[3, 4], [1, 2]], [2, 1]]"
  },
  {
    "test": "\nX = np.array([[1, 1], [2, 2], [3, 3], [4, 4]])\ny = np.array([10, 20, 30, 40])\nprint(get_random_subsets(X, y, 1, True, seed=42))",
    "expected_output": "[([[3, 3], [4, 4], [1, 1], [3, 3]], [30, 40, 10, 30])]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/33_generate-random-subsets-of-a-dataset/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/33_generate-random-subsets-of-a-dataset/description.md)。Deep-ML：Educational Use Only License。
