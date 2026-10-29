---
id: drustz-ad869ae9212e0343de
section: deepml
order: 99
level: A
title: Implement K-Nearest Neighbors
quick: Deep-ML 练习 · Implement K-Nearest Neighbors
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/173_implement-k-nearest-neighbors/description.md
    type: primary
---
### description.md

## Problem

Given a list of points in n-dimensional space represented as tuples and a query point, implement a function to find the k nearest neighbors to the query point using Euclidean distance.

### example.json

```json
{
  "input": "points = [(1, 2), (3, 4), (1, 1), (5, 6), (2, 3)], query_point = (2, 2), k = 3",
  "output": "[(1, 2), (2, 3), (1, 1)]",
  "reasoning": "The 3 closest points to (2, 2) are (1, 2), (2, 3), and (1, 1), so the output is [(1, 2), (2, 3), (1, 1)]."
}
```




### learn.md

## Solution Explanation

The key insight is to use numpy's vectorized operations to efficiently calculate distances between the query point and all data points simultaneously, then select the k smallest distances.

## Algorithm Steps:

Convert to numpy arrays - Transform the input tuples into numpy arrays for vectorized operations
Calculate distances - Use broadcasting to compute Euclidean distance from query point to all points at once
Find k nearest - Use np.argsort() to get indices of points sorted by distance, then take first k
Return as tuples - Convert the selected points back to tuple format

### meta.json

```json
{
  "id": "173",
  "title": "Implement K-Nearest Neighbors",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/kartik-git",
      "name": "kartik-git"
    }
  ]
}
```




### solution.py

```python
def k_nearest_neighbors(points, query_point, k):
    """
    Find k nearest neighbors to a query point

    Args:
        points: List of tuples representing points [(x1, y1), (x2, y2), ...]
        query_point: Tuple representing query point (x, y)
        k: Number of nearest neighbors to return

    Returns:
        List of k nearest neighbor points as tuples
    """
    if not points or k <= 0:
        return []

    if k > len(points):
        k = len(points)

    # Convert to numpy arrays for vectorized operations
    points_array = np.array(points)
    query_array = np.array(query_point)

    # Calculate Euclidean distances using broadcasting
    distances = np.sqrt(np.sum((points_array - query_array) ** 2, axis=1))

    # Get indices of k smallest distances
    k_nearest_indices = np.argsort(distances)[:k]

    # Return the k nearest points as tuples
    return [tuple(points_array[i]) for i in k_nearest_indices]
```




### starter_code.py

```python
def k_nearest_neighbors(points, query_point, k):
    """
    Find k nearest neighbors to a query point

    Args:
        points: List of tuples representing points [(x1, y1), (x2, y2), ...]
        query_point: Tuple representing query point (x, y)
        k: Number of nearest neighbors to return

    Returns:
        List of k nearest neighbor points as tuples
    """
    pass
```




### tests.json

```json
[
  {
    "test": "print(k_nearest_neighbors([(1, 2), (3, 4), (1, 1), (5, 6), (2, 3)], (2, 2), 3))",
    "expected_output": "[(1, 2), (2, 3), (1, 1)]"
  },
  {
    "test": "print(k_nearest_neighbors([(0, 0), (1, 1), (2, 2), (3, 3)], (1.5, 1.5), 2))",
    "expected_output": "[(1, 1), (2, 2)]"
  },
  {
    "test": "print(k_nearest_neighbors([(1, 1), (2, 2), (3, 3)], (0, 0), 1))",
    "expected_output": "[(1, 1)]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/173_implement-k-nearest-neighbors/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/173_implement-k-nearest-neighbors/description.md)。Deep-ML：Educational Use Only License。
