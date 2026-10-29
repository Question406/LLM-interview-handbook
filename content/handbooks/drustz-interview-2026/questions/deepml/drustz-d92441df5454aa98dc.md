---
id: drustz-d92441df5454aa98dc
section: deepml
order: 67
level: A
title: Feature Scaling Implementation
quick: Deep-ML 练习 · Feature Scaling Implementation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/16_feature-scaling-implementation/description.md
    type: primary
---
### description.md

Write a Python function that performs feature scaling on a dataset using both standardization and min-max normalization. The function should take a 2D NumPy array as input, where each row represents a data sample and each column represents a feature. It should return two 2D NumPy arrays: one scaled by standardization and one by min-max normalization. Make sure all results are rounded to the nearest 4th decimal.


### example.json

```json
{
  "input": "data = np.array([[1, 2], [3, 4], [5, 6]])",
  "output": "([[-1.2247, -1.2247], [0.0, 0.0], [1.2247, 1.2247]], [[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]])",
  "reasoning": "Standardization rescales the feature to have a mean of 0 and a standard deviation of 1.\n        Min-max normalization rescales the feature to a range of [0, 1], where the minimum feature value\n        maps to 0 and the maximum to 1."
}
```




### learn.md


## Feature Scaling Techniques

Feature scaling is crucial in many machine learning algorithms that are sensitive to the magnitude of features. This includes algorithms that use distance measures, like k-nearest neighbors, and gradient descent-based algorithms, like linear regression.

### Standardization
Standardization (or Z-score normalization) is the process where features are rescaled so that they have the properties of a standard normal distribution with a mean of zero and a standard deviation of one:
$$
z = \frac{(x - \mu)}{\sigma}
$$
where \( x \) is the original feature, \( \mu \) is the mean of that feature, and \( \sigma \) is the standard deviation.

### Min-Max Normalization
Min-max normalization rescales the feature to a fixed range, typically 0 to 1, or it can be shifted to any range \([a, b]\) by transforming the data using the formula:
$$
x' = \frac{(x - \text{min}(x))}{(\text{max}(x) - \text{min}(x))} \times (\text{max} - \text{min}) + \text{min}
$$
where \( x \) is the original value, \( \text{min}(x) \) is the minimum value for that feature, \( \text{max}(x) \) is the maximum value, and \( \text{min} \) and \( \text{max} \) are the new minimum and maximum values for the scaled data.

### Key Points
- **Equal Contribution**: Implementing these scaling techniques ensures that features contribute equally to the development of the model.
- **Improved Convergence**: Feature scaling can significantly improve the convergence speed of learning algorithms.

This structured explanation outlines the importance of feature scaling and describes two commonly used techniques with their mathematical formulas.


### meta.json

```json
{
  "id": "16",
  "title": "Feature Scaling Implementation",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "https://youtu.be/RrEbO-lbg84?si=hk2qk-26eUyXh0Ee",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ],
  "tinygrad_difficulty": "easy",
  "pytorch_difficulty": "easy"
}
```




### solution.py

```python
import torch


def feature_scaling(data) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Standardize and Min-Max normalize input data using PyTorch.
    Input: Tensor or convertible of shape (m,n).
    Returns (standardized_data, normalized_data), both rounded to 4 decimals.
    """
    data_t = torch.as_tensor(data, dtype=torch.float)
    mean = data_t.mean(dim=0)
    std = data_t.std(dim=0, unbiased=False)
    standardized = (data_t - mean) / std
    min_val = data_t.min(dim=0).values
    max_val = data_t.max(dim=0).values
    normalized = (data_t - min_val) / (max_val - min_val)
    standardized = torch.round(standardized * 10000) / 10000
    normalized = torch.round(normalized * 10000) / 10000
    return standardized, normalized
```




### starter_code.py

```python
import torch


def feature_scaling(data) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Standardize and Min-Max normalize input data using PyTorch.
    Input: Tensor or convertible of shape (m,n).
    Returns (standardized_data, normalized_data), both rounded to 4 decimals.
    """
    data_t = torch.as_tensor(data, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nstd, norm = feature_scaling([[1.0,2.0],[3.0,4.0],[5.0,6.0]])\nprint(std.numpy().tolist(), norm.numpy().tolist())",
    "expected_output": "[[-1.2246999740600586, -1.2246999740600586], [0.0, 0.0], [1.2246999740600586, 1.2246999740600586]] [[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]]"
  },
  {
    "test": "import torch\nstd, norm = feature_scaling(torch.tensor([[10.0,0.0],[20.0,5.0]]))\nprint(std.numpy().tolist(), norm.numpy().tolist())",
    "expected_output": "[[-1.0, -1.0], [1.0, 1.0]] [[0.0, 0.0], [1.0, 1.0]]"
  }
]
```




### solution.py

```python
import numpy as np


def feature_scaling(data):
    # Standardization
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    standardized_data = (data - mean) / std

    # Min-Max Normalization
    min_val = np.min(data, axis=0)
    max_val = np.max(data, axis=0)
    normalized_data = (data - min_val) / (max_val - min_val)

    return np.round(standardized_data, 4).tolist(), np.round(
        normalized_data, 4
    ).tolist()
```




### starter_code.py

```python
def feature_scaling(data: np.ndarray) -> (np.ndarray, np.ndarray):
    # Your code here
    return standardized_data, normalized_data
```




### tests.json

```json
[
  {
    "test": "print(feature_scaling(np.array([[1, 2], [3, 4], [5, 6]])))",
    "expected_output": "([[-1.2247, -1.2247], [0.0, 0.0], [1.2247, 1.2247]], [[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]])"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def feature_scaling_tg(data) -> tuple[Tensor, Tensor]:
    """
    Standardize and Min-Max normalize input data using tinygrad.
    Input: Tensor or convertible of shape (m,n).
    Returns (standardized_data, normalized_data), both rounded to 4 decimals.
    """
    data_t = Tensor(data).float()
    data_np = data_t.numpy()
    mean = np.mean(data_np, axis=0)
    std = np.std(data_np, axis=0)
    standardized_np = (data_np - mean) / std
    min_val = np.min(data_np, axis=0)
    max_val = np.max(data_np, axis=0)
    normalized_np = (data_np - min_val) / (max_val - min_val)
    return Tensor(np.round(standardized_np, 4)), Tensor(np.round(normalized_np, 4))
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def feature_scaling_tg(data) -> tuple[Tensor, Tensor]:
    """
    Standardize and Min-Max normalize input data using tinygrad.
    Input: Tensor or convertible of shape (m,n).
    Returns (standardized_data, normalized_data), both rounded to 4 decimals.
    """
    data_t = Tensor(data).float()
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "from tinygrad.tensor import Tensor\nstd, norm = feature_scaling_tg([[1.0,2.0],[3.0,4.0],[5.0,6.0]])\nprint(std.numpy().tolist(), norm.numpy().tolist())",
    "expected_output": "[[-1.2247, -1.2247], [0.0, 0.0], [1.2247, 1.2247]] [[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]]"
  },
  {
    "test": "from tinygrad.tensor import Tensor\nstd, norm = feature_scaling_tg(Tensor([[10.0,0.0],[20.0,5.0]]))\nprint(std.numpy().tolist(), norm.numpy().tolist())",
    "expected_output": "[[-1.0, -1.0], [1.0, 1.0]] [[0.0, 0.0], [1.0, 1.0]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/16_feature-scaling-implementation/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/16_feature-scaling-implementation/description.md)。Deep-ML：Educational Use Only License。
