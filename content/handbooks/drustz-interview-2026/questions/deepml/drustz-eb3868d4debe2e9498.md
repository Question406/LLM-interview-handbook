---
id: drustz-eb3868d4debe2e9498
section: deepml
order: 105
level: A
title: Implement Orthogonal Projection of a Vector onto a Line
quick: Deep-ML 练习 · Implement Orthogonal Projection of a Vector onto a Line
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/66_implement-orthogonal-projection-of-a-vector-onto-a/description.md
    type: primary
---
### description.md

## Task: Compute the Orthogonal Projection of a Vector

Your task is to implement a function that calculates the orthogonal projection of a vector **v** onto another vector **L**. This projection results in the vector on **L** that is closest to **v**.

Write a function `orthogonal_projection(v, L)` that takes in two lists, `v` (the vector to be projected) and `L` (the line vector), and returns the orthogonal projection of `v` onto `L`. The function should output a list representing the projection vector rounded to three decimal places.

    


### example.json

```json
{
  "input": "v = [3, 4]\nL = [1, 0]\nprint(orthogonal_projection(v, L))",
  "output": "[3.0, 0.0]",
  "reasoning": "The orthogonal projection of vector [3, 4] onto the line defined by [1, 0] results in the projection vector [3, 0], which lies on the line [1, 0]."
}
```




### learn.md


## Understanding Orthogonal Projection in Vector Spaces

Orthogonal projection is a fundamental concept in linear algebra, used to project one vector onto another. The projection of vector $v$ onto a line defined by vector $L$ results in a new vector that lies on $L$, representing the closest point to $v$ on that line. This can be thought of as $v$'s shadow on $L$ if a light was shown directly down on $v$.

To project a vector $v$ onto a non-zero vector $L$ in space, we calculate the scalar projection of $v$ onto the unit vector of $L$, which represents the magnitude of the projection. The resulting projection vector lies along the direction of $L$.

For any vector $v$ in Cartesian space, the orthogonal projection onto $L$ is calculated using the formula:

$$
\text{proj}_{L} (v) = \frac{v \cdot L}{L \cdot L} L
$$

Where:

1) $v$ is the vector being projected,  
2) $L$ is the vector defining the line of projection,  
3) $v \cdot L$ is the dot product of $v$ and $L$,  
4) $L \cdot L$ is the dot product of $L$ with itself, which gives the magnitude squared of $L$.

The resulting projection vector lies along the direction of $L$ and represents the component of $v$ that is parallel to $L$.

More generally, the projection of $v$ onto a unit vector $ \hat{L} $ (the normalized version of $L$) simplifies to:

$$
\text{proj}_{L} (v) = (v \cdot \hat{L}) \hat{L}
$$

### Applications of Orthogonal Projection

Orthogonal projection has a wide range of applications across various fields in mathematics, physics, computer science, and engineering. Some of the most common applications include:

1) **Computer Graphics**: In 3D rendering, orthogonal projections are used to create 2D views of 3D objects. This projection helps in reducing dimensional complexity and displaying models from different angles.
2) **Data Science and Machine Learning**: In high-dimensional data, projection methods are used to reduce dimensions (e.g., Principal Component Analysis) by projecting data onto lower-dimensional subspaces, helping with data visualization and reducing computational complexity.


### meta.json

```json
{
  "id": "66",
  "title": "Implement Orthogonal Projection of a Vector onto a Line",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/paddywardle",
      "name": "paddywardle"
    }
  ]
}
```




### solution.py

```python
def dot(v1, v2):
    return sum([ax1 * ax2 for ax1, ax2 in zip(v1, v2)])


def scalar_mult(scalar, v):
    return [scalar * ax for ax in v]


def orthogonal_projection(v, L):
    L_mag_sq = dot(L, L)
    proj_scalar = dot(v, L) / L_mag_sq
    proj_v = scalar_mult(proj_scalar, L)
    return [round(x, 3) for x in proj_v]
```




### starter_code.py

```python
def orthogonal_projection(v, L):
    """
    Compute the orthogonal projection of vector v onto line L.

    :param v: The vector to be projected
    :param L: The line vector defining the direction of projection
    :return: List representing the projection of v onto L
    """
    pass
```




### tests.json

```json
[
  {
    "test": "v = [3, 4]\nL = [1, 0]\nprint(orthogonal_projection(v, L))",
    "expected_output": "[3.0, 0.0]"
  },
  {
    "test": "v = [1, 2, 3]\nL = [0, 0, 1]\nprint(orthogonal_projection(v, L))",
    "expected_output": "[0.0, 0.0, 3.0]"
  },
  {
    "test": "v = [5, 6, 7]\nL = [2, 0, 0]\nprint(orthogonal_projection(v, L))",
    "expected_output": "[5.0, 0.0, 0.0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/66_implement-orthogonal-projection-of-a-vector-onto-a/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/66_implement-orthogonal-projection-of-a-vector-onto-a/description.md)。Deep-ML：Educational Use Only License。
