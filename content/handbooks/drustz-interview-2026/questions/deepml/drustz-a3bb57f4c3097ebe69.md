---
id: drustz-a3bb57f4c3097ebe69
section: deepml
order: 17
level: A
title: Calculate Cosine Similarity Between Vectors
quick: Deep-ML 练习 · Calculate Cosine Similarity Between Vectors
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/76_calculate-cosine-similarity-between-vectors/description.md
    type: primary
---
### description.md


## Task: Implement Cosine Similarity

In this task, you need to implement a function `cosine_similarity(v1, v2)` that calculates the cosine similarity between two vectors. Cosine similarity measures the cosine of the angle between two vectors, indicating their directional similarity.

### Input:
- `v1` and `v2`: Numpy arrays representing the input vectors.

### Output:
- A float representing the cosine similarity, rounded to three decimal places.

### Constraints:
- Both input vectors must have the same shape.
- Input vectors cannot be empty or have zero magnitude.


### example.json

```json
{
  "input": "import numpy as np\n\nv1 = np.array([1, 2, 3])\nv2 = np.array([2, 4, 6])\nprint(cosine_similarity(v1, v2))",
  "output": "1.0",
  "reasoning": "The cosine similarity between v1 and v2 is 1.0, indicating perfect similarity."
}
```




### learn.md


## Cosine Similarity

Cosine similarity measures the cosine of the angle between two vectors. It doesn't consider the magnitude of the vectors but focuses on the angle between them.

### Cosine Similarity Formula
$$
\cos(\theta) = \frac{\sum_{i=1}^{p} A_i B_i}{\sqrt{\sum_{i=1}^{p} A_i^2} \sqrt{\sum_{i=1}^{p} B_i^2}}
$$

### Implementation Steps for Cosine Similarity
1. **Handle Input**: Ensure input vectors have the same dimensions and handle edge cases (e.g., zero vectors).
2. **Dot Product**: Compute $\sum_{i=1}^{p} A_i B_i $ for the two vectors.
3. **Magnitudes**: Compute the L2 norms $ \sqrt{\sum_{i=1}^{p} A_i^2} $ and $ \sqrt{\sum_{i=1}^{p} B_i^2} $.
4. **Final Result**: Divide the dot product by the product of the magnitudes.

### Use Cases
1. **Text and Image Similarity**
2. **Recommendation Systems**
3. **Query Matching**

### Pitfalls
1. **Magnitude Blindness**:
   - Example:
     - $ \text{vector1} = (1, 1) $
     - $ \text{vector2} = (1000, 1000) $
     - Cosine similarity $ = 1 $, despite the vastly different magnitudes.
2. **Sparse Data Issues**:
   - In high-dimensional spaces, where data is often sparse, cosine similarity may become less reliable.
3. **Non-Negative Data Limitation**:
   - If all values are positive, cosine similarity cannot capture negative relationships or inverse trends.


### meta.json

```json
{
  "id": "76",
  "title": "Calculate Cosine Similarity Between Vectors",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "https://youtu.be/QMdvVDhc6f0?si=ST33rc73BjHY3pij",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/saitiger",
      "name": "saitiger"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def cosine_similarity(v1, v2):
    if v1.shape != v2.shape:
        raise ValueError("Arrays must have the same shape")

    if v1.size == 0:
        raise ValueError("Arrays cannot be empty")

    # Flatten arrays in case of 2D
    v1_flat = v1.flatten()
    v2_flat = v2.flatten()

    dot_product = np.dot(v1_flat, v2_flat)
    magnitude1 = np.sqrt(np.sum(v1_flat**2))
    magnitude2 = np.sqrt(np.sum(v2_flat**2))

    if magnitude1 == 0 or magnitude2 == 0:
        raise ValueError("Vectors cannot have zero magnitude")

    return round(dot_product / (magnitude1 * magnitude2), 3)
```




### starter_code.py

```python
import numpy as np


def cosine_similarity(v1, v2):
    # Implement your code here
    pass
```




### tests.json

```json
[
  {
    "test": "\nimport numpy as np\n\nv1 = np.array([1, 2, 3])\nv2 = np.array([2, 4, 6])\nprint(cosine_similarity(v1, v2))\n",
    "expected_output": "1.0"
  },
  {
    "test": "\nimport numpy as np\n\nv1 = np.array([1, 2, 3])\nv2 = np.array([-1, -2, -3])\nprint(cosine_similarity(v1, v2))\n",
    "expected_output": "-1.0"
  },
  {
    "test": "\nimport numpy as np\n\nv1 = np.array([1, 0, 7])\nv2 = np.array([0, 1, 3])\nprint(cosine_similarity(v1, v2))\n",
    "expected_output": "0.939"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/76_calculate-cosine-similarity-between-vectors/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/76_calculate-cosine-similarity-between-vectors/description.md)。Deep-ML：Educational Use Only License。
