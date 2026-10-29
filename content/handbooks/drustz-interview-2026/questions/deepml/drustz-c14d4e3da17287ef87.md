---
id: drustz-c14d4e3da17287ef87
section: deepml
order: 149
level: A
title: One-Hot Encoding of Nominal Values
quick: Deep-ML 练习 · One-Hot Encoding of Nominal Values
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/34_one-hot-encoding-of-nominal-values/description.md
    type: primary
---
### description.md

Write a Python function to perform one-hot encoding of nominal values. The function should take in a 1D numpy array x of integer values and an optional integer  $n_{col}$  representing the number of columns for the one-hot encoded array. If  $n_{col}$  is not provided, it should be automatically determined from the input array.


### example.json

```json
{
  "input": "x = np.array([0, 1, 2, 1, 0])\n    output = to_categorical(x)\n    print(output)",
  "output": "# [[1. 0. 0.]\n    #  [0. 1. 0.]\n    #  [0. 0. 1.]\n    #  [0. 1. 0.]\n    #  [1. 0. 0.]]",
  "reasoning": "Each element in the input array is transformed into a one-hot encoded vector,\n    where the index corresponding to the value in the input array is set to 1, \n    and all other indices are set to 0."
}
```




### learn.md


## Understanding One-Hot Encoding

One-hot encoding is a method used to represent categorical variables as binary vectors. This technique is useful in machine learning when dealing with categorical data that has no ordinal relationship.

### Explanation
In one-hot encoding, each category is represented by a binary vector with a length equal to the number of categories. The vector has a value of 1 at the index corresponding to the category and 0 at all other indices.

### Example
For instance, if you have three categories: 0, 1, and 2, the one-hot encoded vectors would be:
- **0**: $[1, 0, 0]$
- **1**: $[0, 1, 0]$
- **2**: $[0, 0, 1]$

This method ensures that the model does not assume any ordinal relationship between categories, which is crucial for many machine learning algorithms.

### Mathematical Representation
The one-hot encoding process can be mathematically represented as follows:

Given a category $x_i$ from a set of categories $\{0, 1, \ldots, n-1\}$, the one-hot encoded vector $\mathbf{v}$ is:
$$
\mathbf{v}_i = 
\begin{cases} 
1 & \text{if } i = x_i \\
0 & \text{otherwise}
\end{cases}
$$

This vector $\mathbf{v}$ will have a length equal to the number of unique categories.


### meta.json

```json
{
  "id": "34",
  "title": "One-Hot Encoding of Nominal Values",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": []
}
```




### solution.py

```python
import numpy as np


def to_categorical(x, n_col=None):
    # One-hot encoding of nominal values
    # If n_col is not provided, determine the number of columns from the input array
    if not n_col:
        n_col = np.amax(x) + 1
    # Initialize a matrix of zeros with shape (number of samples, n_col)
    one_hot = np.zeros((x.shape[0], n_col))
    # Set the appropriate elements to 1
    one_hot[np.arange(x.shape[0]), x] = 1
    return one_hot
```




### starter_code.py

```python
import numpy as np


def to_categorical(x, n_col=None):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(to_categorical(np.array([0, 1, 2, 1, 0])))",
    "expected_output": "[[1., 0., 0.], [0., 1., 0.], [0., 0., 1.], [0., 1., 0.], [1., 0., 0.]]"
  },
  {
    "test": "print(to_categorical(np.array([3, 1, 2, 1, 3]), 4))",
    "expected_output": "[[0., 0., 0., 1.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/34_one-hot-encoding-of-nominal-values/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/34_one-hot-encoding-of-nominal-values/description.md)。Deep-ML：Educational Use Only License。
