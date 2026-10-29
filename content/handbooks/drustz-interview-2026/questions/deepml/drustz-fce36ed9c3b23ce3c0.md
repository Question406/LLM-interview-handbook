---
id: drustz-fce36ed9c3b23ce3c0
section: deepml
order: 162
level: A
title: Shift and Scale Array to Target Range
quick: Deep-ML 练习 · Shift and Scale Array to Target Range
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/141_shift-and-scale-array-to-target-range/description.md
    type: primary
---
### description.md

Write a Python function `convert_range` that shifts and scales the values of a NumPy array from their original range $[a, b]$ (where $a=\min(x)$ and $b=\max(x)$) to a new target range $[c, d]$. Your function should work for both 1D and 2D arrays, returning an array of the same shape, and only use NumPy. Return floating-point results, and ensure you use the correct formula to map the input interval to the output interval.


### example.json

```json
{
  "input": "import numpy as np\nx = np.array([0, 5, 10])\nc, d = 2, 4\nprint(convert_range(x, c, d))",
  "output": "[2. 3. 4.]",
  "reasoning": "The minimum value (a) is 0 and the maximum value (b) is 10. The formula maps 0 to 2, 5 to 3, and 10 to 4 using: f(x) = c + (d-c)/(b-a)*(x-a)."
}
```




### learn.md

# **Shifting and Scaling a Range (Rescaling Data)**

## **1. Motivation**

Rescaling (or shifting and scaling) is a common preprocessing step in data analysis and machine learning. It's often necessary to map data from an original range (e.g., test scores, pixel values, GPA) to a new range suitable for downstream tasks or compatibility between datasets. For example, you might want to shift a GPA from $[0, 10]$ to $[0, 4]$ for comparison or model input.

---

## **2. The General Mapping Formula**

Suppose you have input values in the range $[a, b]$ and you want to map them to the interval $[c, d]$.

- First, shift the lower bound to $0$ by applying $x \mapsto x - a$, so $[a, b] \rightarrow [0, b-a]$.
- Next, scale to unit interval: $t \mapsto \frac{1}{b-a} \cdot t$, yielding $[0, 1]$.
- Now, scale to $[0, d-c]$ with $t \mapsto (d-c)t$, and shift to $[c, d]$ with $t \mapsto c + t$.
- Combining all steps, the complete formula is:

$$
    f(x) = c + \left(\frac{d-c}{b-a}\right)(x-a)
$$

- $x$ = the input value
- $a = \min(x)$ and $b = \max(x)$
- $c$, $d$ = target interval endpoints

---

## **3. Applications**
- **Image Processing**: Rescale pixel intensities
- **Feature Engineering**: Normalize features to a common range
- **Score Conversion**: Convert test scores or grades between systems

---

## **4. Practical Considerations**
- Be aware of the case when $a = b$ (constant input); this may require special handling (e.g., output all $c$).
- For multidimensional arrays, use NumPy’s `.min()` and `.max()` to determine the full input range.

---

This formula gives a **simple, mathematically justified way to shift and scale data to any target range**—a core tool for robust machine learning pipelines.


### meta.json

```json
{
  "id": "141",
  "title": "Shift and Scale Array to Target Range",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/turkunov",
      "name": "turkunov"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def convert_range(values: np.ndarray, c: float, d: float) -> np.ndarray:
    """
    Shift and scale values from their original range [min, max] to a target [c, d] range.

    Parameters
    ----------
    values : np.ndarray
        Input array (1D or 2D) to be rescaled.
    c : float
        New range lower bound.
    d : float
        New range upper bound.

    Returns
    -------
    np.ndarray
        Scaled array with the same shape as the input.
    """
    a, b = values.min(), values.max()
    return c + (d - c) / (b - a) * (values - a)
```




### starter_code.py

```python
import numpy as np


def convert_range(values: np.ndarray, c: float, d: float) -> np.ndarray:
    """
    Shift and scale values from their original range [min, max] to a target [c, d] range.
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nseq = np.array([388, 242, 124, 384, 313, 277, 339, 302, 268, 392])\nc, d = 0, 1\nout = convert_range(seq, c, d)\nprint(np.round(out, 6))",
    "expected_output": "[0.985075, 0.440299, 0.,       0.970149, 0.705224, 0.570896, 0.802239, 0.664179, 0.537313, 1.      ]"
  },
  {
    "test": "import numpy as np\nseq = np.array([[2028, 4522], [1412, 2502], [3414, 3694], [1747, 1233], [1862, 4868]])\nc, d = 4, 8\nout = convert_range(seq, c, d)\nprint(np.round(out, 6))",
    "expected_output": "[[4.874828 7.619257]\n [4.196974 5.396424]\n [6.4      6.708116]\n [4.565612 4.      ]\n [4.69216  8.      ]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/141_shift-and-scale-array-to-target-range/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/141_shift-and-scale-array-to-target-range/description.md)。Deep-ML：Educational Use Only License。
