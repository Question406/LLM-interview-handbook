---
id: drustz-c8cf17d742ee5f57cc
section: deepml
order: 6
level: A
title: Batch Iterator for Dataset
quick: Deep-ML 练习 · Batch Iterator for Dataset
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/30_batch-iterator-for-dataset/description.md
    type: primary
---
### description.md

Implement a batch iterable function that samples in a numpy array X and an optional numpy array y. The function should return batches of a specified size. If y is provided, the function should return batches of (X, y) pairs; otherwise, it should return batches of X only.


### example.json

```json
{
  "input": "X = np.array([[1, 2], \n                  [3, 4], \n                  [5, 6], \n                  [7, 8], \n                  [9, 10]])\n    y = np.array([1, 2, 3, 4, 5])\n    batch_size = 2\n    batch_iterator(X, y, batch_size)",
  "output": "[[[[1, 2], [3, 4]], [1, 2]],\n     [[[5, 6], [7, 8]], [3, 4]],\n     [[[9, 10]], [5]]]",
  "reasoning": "The dataset X contains 5 samples, and we are using a batch size of 2. Therefore, the function will divide the dataset into 3 batches. The first two batches will contain 2 samples each, and the last batch will contain the remaining sample. The corresponding values from y are also included in each batch."
}
```




### learn.md


## Understanding Batch Iteration

Batch iteration is a common technique used in machine learning and data processing to handle large datasets more efficiently. Instead of processing the entire dataset at once, which can be memory-intensive, data is processed in smaller, more manageable batches.

### Step-by-Step Method to Create a Batch Iterator

1. **Determine the Number of Samples**  
   Calculate the total number of samples in the dataset.

2. **Iterate in Batches**  
   Loop through the dataset in increments of the specified batch size.

3. **Yield Batches**  
   For each iteration, yield a batch of samples from \( X \) and, if provided, the corresponding samples from \( y \).

### Key Point
This method ensures efficient processing and can be used for both the training and evaluation phases in machine learning workflows.


### meta.json

```json
{
  "id": "30",
  "title": "Batch Iterator for Dataset",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "https://youtu.be/_Ox2PUBpkMw?si=oiWBJezQQoREIHPU",
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


def batch_iterator(X, y=None, batch_size=64):
    n_samples = X.shape[0]
    batches = []
    for i in np.arange(0, n_samples, batch_size):
        begin, end = i, min(i + batch_size, n_samples)
        if y is not None:
            batches.append([X[begin:end], y[begin:end]])
        else:
            batches.append(X[begin:end])
    return batches
```




### starter_code.py

```python
import numpy as np


def batch_iterator(X, y=None, batch_size=64):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(batch_iterator(np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]), np.array([1, 2, 3, 4, 5]), batch_size=2))",
    "expected_output": "[[[[1, 2], [3, 4]], [1, 2]], [[[5, 6], [7, 8]], [3, 4]], [[[9, 10]], [5]]]"
  },
  {
    "test": "print(batch_iterator(np.array([[1, 1], [2, 2], [3, 3], [4, 4]]), batch_size=3))",
    "expected_output": "[[[1, 1], [2, 2], [3, 3]], [[4, 4]]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/30_batch-iterator-for-dataset/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/30_batch-iterator-for-dataset/description.md)。Deep-ML：Educational Use Only License。
