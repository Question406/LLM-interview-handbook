---
id: drustz-c24af574b6cbd3be45
section: deepml
order: 34
level: A
title: Compute Pointwise Mutual Information
quick: Deep-ML 练习 · Compute Pointwise Mutual Information
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/111_compute-pointwise-mutual-information/description.md
    type: primary
---
### description.md

Implement a function to compute the Pointwise Mutual Information (PMI) given the joint occurrence count of two events, their individual counts, and the total number of samples. PMI measures how much the actual joint occurrence of events differs from what we would expect by chance.


### example.json

```json
{
  "input": "compute_pmi(50, 200, 300, 1000)",
  "output": "-0.263",
  "reasoning": "The PMI calculation compares the actual joint probability (50/1000 = 0.05) to the product of the individual probabilities (200/1000 * 300/1000 = 0.06). Thus, PMI = log₂(0.05 / (0.2 * 0.3)) ≈ -0.263, indicating the events co-occur slightly less than expected by chance."
}
```




### learn.md

# Pointwise Mutual Information (PMI)

Pointwise Mutual Information (PMI) is a statistical measure used in information theory and Natural Language Processing (NLP) to quantify the association between two events. It measures how much the actual joint occurrence of two events differs from what would be expected if they were independent. PMI is commonly used for identifying word associations, feature selection in text classification, and calculating document similarity.

## Implementation 

1. **Collect Count Data** for events $x$, $y$, and their joint occurrence $(x,y)$.

2. **Calculate Individual Probabilities**:
   - $P(x) = \frac{\text{Count}(x)}{\text{Total Count}}$
   - $P(y) = \frac{\text{Count}(y)}{\text{Total Count}}$

3. **Calculate Joint Probability**:
   - $P(x,y) = \frac{\text{Count}(x,y)}{\text{Total Count}}$

4. **Calculate PMI**:
   - $$\text{PMI}(x,y) = \log_2\left(\frac{P(x,y)}{P(x) \cdot P(y)}\right)$$

## Interpretation of PMI Values

- **Positive PMI**: Events co-occur more frequently than expected by chance.
- **Zero PMI**: Events are statistically independent.
- **Negative PMI**: Events co-occur less frequently than expected by chance.
- **Undefined PMI**: Occurs when $P(x,y) = 0$ (the events never co-occur).

## Variants of PMI

### 1. Normalized PMI (NPMI)

NPMI scales PMI to a range of [-1, 1] to account for dataset size variations:

$$
\text{NPMI}(x,y) = \frac{\text{PMI}(x,y)}{-\log_2 P(x,y)}
$$

### 2. Positive PMI (PPMI)

PPMI sets negative PMI scores to zero, often used in word embeddings:

$$
\text{PPMI}(x,y) = \max(\text{PMI}(x,y),\,0)
$$


### meta.json

```json
{
  "id": "111",
  "title": "Compute Pointwise Mutual Information",
  "difficulty": "medium",
  "category": "NLP",
  "video": "",
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


def compute_pmi(joint_counts, total_counts_x, total_counts_y, total_samples):

    if not all(
        isinstance(x, int) and x >= 0
        for x in [joint_counts, total_counts_x, total_counts_y, total_samples]
    ):
        raise ValueError("All inputs must be non-negative integers.")

    if total_samples == 0:
        raise ValueError("Total samples cannot be zero.")

    if joint_counts > min(total_counts_x, total_counts_y):
        raise ValueError("Joint counts cannot exceed individual counts.")

    p_x = total_counts_x / total_samples
    p_y = total_counts_y / total_samples
    p_xy = joint_counts / total_samples

    if p_xy == 0:
        return float('-inf')

    pmi = np.log2(p_xy / (p_x * p_y))

    return round(pmi, 3)
```




### starter_code.py

```python
import numpy as np


def compute_pmi(joint_counts, total_counts_x, total_counts_y, total_samples):
    # Implement PMI calculation here
    pass
```




### tests.json

```json
[
  {
    "test": "print(compute_pmi(10, 50, 50, 200))",
    "expected_output": "-0.322"
  },
  {
    "test": "print(compute_pmi(100, 500, 500, 1000))",
    "expected_output": "-1.322"
  },
  {
    "test": "print(float(compute_pmi(100, 400, 600, 1200)))",
    "expected_output": "-1."
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/111_compute-pointwise-mutual-information/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/111_compute-pointwise-mutual-information/description.md)。Deep-ML：Educational Use Only License。
