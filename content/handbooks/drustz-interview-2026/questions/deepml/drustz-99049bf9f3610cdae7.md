---
id: drustz-99049bf9f3610cdae7
section: deepml
order: 133
level: A
title: K-Means Clustering
quick: Deep-ML 练习 · K-Means Clustering
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/17_k-means-clustering/description.md
    type: primary
---
### description.md

Your task is to write a Python function that implements the k-Means clustering algorithm. This function should take specific inputs and produce a list of final centroids. k-Means clustering is a method used to partition `n` points into `k` clusters. The goal is to group similar points together and represent each group by its center (called the *centroid*).

### Function Inputs:

- `points`: A list of points, where each point is a tuple of coordinates (e.g., `(x, y)` for 2D points)
- `k`: An integer representing the number of clusters to form
- `initial_centroids`: A list of initial centroid points, each a tuple of coordinates
- `max_iterations`: An integer representing the maximum number of iterations to perform

### Function Output:

A list of the final centroids of the clusters, where each centroid is rounded to the nearest fourth decimal.


### example.json

```json
{
  "input": "points = [(1, 2), (1, 4), (1, 0), (10, 2), (10, 4), (10, 0)], k = 2, initial_centroids = [(1, 1), (10, 1)], max_iterations = 10",
  "output": "[(1, 2), (10, 2)]",
  "reasoning": "Given the initial centroids and a maximum of 10 iterations,\n        the points are clustered around these points, and the centroids are\n        updated to the mean of the assigned points, resulting in the final\n        centroids which approximate the means of the two clusters.\n        The exact number of iterations needed may vary,\n        but the process will stop after 10 iterations at most."
}
```




### learn.md


## K-Means Clustering Algorithm Implementation

### Algorithm Steps

1. **Initialization**  
   Use the provided `initial_centroids` as your starting point. This step is already done for you in the input.

2. **Assignment Step**  
   For each point in your dataset:
   - Calculate its distance to each centroid.
   - Assign the point to the cluster of the nearest centroid.  
   *Hint*: Consider creating a helper function to calculate the Euclidean distance between two points.

3. **Update Step**  
   For each cluster:
   - Calculate the mean of all points assigned to the cluster.
   - Update the centroid to this new mean position.  
   *Hint*: Be careful with potential empty clusters. Decide how you'll handle them (e.g., keep the previous centroid).

4. **Iteration**  
   Repeat steps 2 and 3 until either:
   - The centroids no longer change significantly (this case does not need to be included in your solution), or
   - You reach the `max_iterations` limit.  
   *Hint*: You might want to keep track of the previous centroids to check for significant changes.

5. **Result**  
   Return the list of final centroids, ensuring each coordinate is rounded to the nearest fourth decimal.


### meta.json

```json
{
  "id": "17",
  "title": "K-Means Clustering",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "https://youtu.be/KzJORp8bgqs?si=BBrGGuCAWt_AA8QV",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Haleshot",
      "name": "Srihari Thyagarajan"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium",
  "marimo_link": "https://adityakhalkar.github.io/Deep-ML-x-Marimo/17"
}
```




### solution.py

```python
import torch


def k_means_clustering(
    points, k, initial_centroids, max_iterations
) -> list[tuple[float, ...]]:
    """
    Perform k-means clustering on `points` into `k` clusters.
    points: tensor of shape (n_points, n_features)
    initial_centroids: tensor of shape (k, n_features)
    max_iterations: maximum number of iterations
    Returns a list of k centroids as tuples, rounded to 4 decimals.
    """
    points_t = torch.as_tensor(points, dtype=torch.float)
    centroids = torch.as_tensor(initial_centroids, dtype=torch.float)
    for _ in range(max_iterations):
        # compute distances (k, n_points)
        diffs = points_t.unsqueeze(0) - centroids.unsqueeze(1)
        distances = torch.sqrt((diffs**2).sum(dim=2))
        # assign each point to nearest centroid
        assignments = distances.argmin(dim=0)
        new_centroids = []
        for i in range(k):
            cluster_points = points_t[assignments == i]
            if cluster_points.numel() == 0:
                new_centroids.append(centroids[i])
            else:
                new_centroids.append(cluster_points.mean(dim=0))
        new_centroids = torch.stack(new_centroids)
        new_centroids = torch.round(new_centroids * 10000) / 10000
        if torch.equal(new_centroids, centroids):
            break
        centroids = new_centroids
    return [tuple(c.tolist()) for c in centroids]
```




### starter_code.py

```python
import torch


def k_means_clustering(
    points, k, initial_centroids, max_iterations
) -> list[tuple[float, ...]]:
    """
    Perform k-means clustering on `points` into `k` clusters.
    points: tensor of shape (n_points, n_features)
    initial_centroids: tensor of shape (k, n_features)
    max_iterations: maximum number of iterations
    Returns a list of k centroids as tuples, rounded to 4 decimals.
    """
    # Convert to tensors
    points_t = torch.as_tensor(points, dtype=torch.float)
    centroids = torch.as_tensor(initial_centroids, dtype=torch.float)
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nres = k_means_clustering(\n    torch.tensor([[0.0,0.0],[0.1,0.1],[10.0,10.0],[10.1,10.1]]),\n    2,\n    torch.tensor([[0.0,0.0],[10.0,10.0]]),\n    10\n)\nprint(res)",
    "expected_output": "[(0.05, 0.05), (10.05, 10.05)]"
  },
  {
    "test": "import torch\nres = k_means_clustering(\n    torch.tensor([[1.0,2.0],[3.0,4.0]]),\n    1,\n    torch.tensor([[1.0,2.0]]),\n    10\n)\nprint(res)",
    "expected_output": "[(2.0, 3.0)]"
  }
]
```




### solution.py

```python
import numpy as np


def euclidean_distance(a, b):
    return np.sqrt(((a - b) ** 2).sum(axis=1))


def k_means_clustering(points, k, initial_centroids, max_iterations):
    points = np.array(points)
    centroids = np.array(initial_centroids)

    for iteration in range(max_iterations):
        # Assign points to the nearest centroid
        distances = np.array(
            [euclidean_distance(points, centroid) for centroid in centroids]
        )
        assignments = np.argmin(distances, axis=0)

        new_centroids = np.array(
            [
                points[assignments == i].mean(axis=0)
                if len(points[assignments == i]) > 0
                else centroids[i]
                for i in range(k)
            ]
        )

        # Check for convergence
        if np.all(centroids == new_centroids):
            break
        centroids = new_centroids
        centroids = np.round(centroids, 4)
    return [tuple(centroid) for centroid in centroids]
```




### starter_code.py

```python
def k_means_clustering(
    points: list[tuple[float, float]],
    k: int,
    initial_centroids: list[tuple[float, float]],
    max_iterations: int,
) -> list[tuple[float, float]]:
    # Your code here
    return final_centroids
```




### tests.json

```json
[
  {
    "test": "print(k_means_clustering([(1, 2), (1, 4), (1, 0), (10, 2), (10, 4), (10, 0)], 2, [(1, 1), (10, 1)], 10))",
    "expected_output": "[(1.0, 2.0), (10.0, 2.0)]"
  },
  {
    "test": "print(k_means_clustering([(0, 0, 0), (2, 2, 2), (1, 1, 1), (9, 10, 9), (10, 11, 10), (12, 11, 12)], 2, [(1, 1, 1), (10, 10, 10)], 10))",
    "expected_output": "[(1.0, 1.0, 1.0), (10.3333, 10.6667, 10.3333)]"
  },
  {
    "test": "print(k_means_clustering([(1, 1), (2, 2), (3, 3), (4, 4)], 1, [(0,0)], 10))",
    "expected_output": "[(2.5, 2.5)]"
  },
  {
    "test": "print(k_means_clustering([(0, 0), (1, 0), (0, 1), (1, 1), (5, 5), (6, 5), (5, 6), (6, 6),(0, 5), (1, 5), (0, 6), (1, 6), (5, 0), (6, 0), (5, 1), (6, 1)], 4, [(0, 0), (0, 5), (5, 0), (5, 5)], 10))",
    "expected_output": "[(0.5, 0.5), (0.5, 5.5), (5.5, 0.5), (5.5, 5.5)]"
  }
]
```




### solution.py

```python
import numpy as np
from tinygrad.tensor import Tensor


def k_means_clustering_tg(
    points, k, initial_centroids, max_iterations
) -> list[tuple[float, ...]]:
    """
    Perform k-means clustering on `points` into `k` clusters using tinygrad.
    points: list of lists or Tensor, shape (n_points, n_features)
    initial_centroids: list of lists or Tensor, shape (k, n_features)
    max_iterations: maximum number of iterations
    Returns a list of k centroids as tuples, rounded to 4 decimals.
    """
    pts = np.array(points, dtype=float)
    centroids = np.array(initial_centroids, dtype=float)
    for _ in range(max_iterations):
        # compute distances (k, n_points)
        dists = np.array([np.linalg.norm(pts - c, axis=1) for c in centroids])
        # assign points
        assignments = dists.argmin(axis=0)
        new_centroids = np.array(
            [
                pts[assignments == i].mean(axis=0)
                if np.any(assignments == i)
                else centroids[i]
                for i in range(k)
            ]
        )
        new_centroids = np.round(new_centroids, 4)
        if np.array_equal(new_centroids, centroids):
            break
        centroids = new_centroids
    return [tuple(c.tolist()) for c in centroids]
```




### starter_code.py

```python
from tinygrad.tensor import Tensor


def k_means_clustering_tg(
    points, k, initial_centroids, max_iterations
) -> list[tuple[float, ...]]:
    """
    Perform k-means clustering on `points` into `k` clusters using tinygrad.
    points: list of lists or Tensor, shape (n_points, n_features)
    initial_centroids: list of lists or Tensor, shape (k, n_features)
    max_iterations: maximum number of iterations
    Returns a list of k centroids as tuples, rounded to 4 decimals.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "res = k_means_clustering_tg(\n    [[0.0,0.0],[0.1,0.1],[10.0,10.0],[10.1,10.1]],\n    2,\n    [[0.0,0.0],[10.0,10.0]],\n    10\n)\nprint(res)",
    "expected_output": "[(0.05, 0.05), (10.05, 10.05)]"
  },
  {
    "test": "res = k_means_clustering_tg(\n    [[1.0,2.0],[3.0,4.0]],\n    1,\n    [[1.0,2.0]],\n    10\n)\nprint(res)",
    "expected_output": "[(2.0, 3.0)]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/17_k-means-clustering/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/17_k-means-clustering/description.md)。Deep-ML：Educational Use Only License。
