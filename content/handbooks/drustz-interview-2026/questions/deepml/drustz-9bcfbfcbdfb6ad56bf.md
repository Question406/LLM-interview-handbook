---
id: drustz-9bcfbfcbdfb6ad56bf
section: deepml
order: 23
level: A
title: Calculate Jaccard Index for Binary Classification
quick: Deep-ML 练习 · Calculate Jaccard Index for Binary Classification
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/72_calculate-jaccard-index-for-binary-classification/description.md
    type: primary
---
### description.md


## Task: Implement the Jaccard Index

Your task is to implement a function `jaccard_index(y_true, y_pred)` that calculates the Jaccard Index, a measure of similarity between two binary sets. The Jaccard Index is widely used in binary classification tasks to evaluate the overlap between predicted and true labels.

### Your Task:
Implement the function `jaccard_index(y_true, y_pred)` to:
1. Calculate the Jaccard Index between the arrays `y_true` and `y_pred`.
2. Return the Jaccard Index as a float value.
3. Ensure the function handles cases where:
   - There is no overlap between `y_true` and `y_pred`.
   - Both arrays contain only zeros (edge cases).

The Jaccard Index is defined as:

$$
\scriptsize
\text{Jaccard Index} = \frac{\text{Number of elements in the intersection of } y_{\text{true}} \text{ and } y_{\text{pred}}}{\text{Number of elements in the union of } y_{\text{true}} \text{ and } y_{\text{pred}}}
$$


Where:
- $ y_{\text{true}} $ and $ y_{\text{pred}} $ are binary arrays of the same length, representing true and predicted labels.
- The result ranges from 0 (no overlap) to 1 (perfect overlap).


### example.json

```json
{
  "input": "y_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 0, 0, 1])\nprint(jaccard_index(y_true, y_pred))",
  "output": "0.75",
  "reasoning": "The Jaccard Index is calculated as 3 / 4 = 0.75, indicating a 75% overlap between the true and predicted labels."
}
```




### learn.md


## Understanding Jaccard Index in Classification

The Jaccard Index, also known as the Jaccard Similarity Coefficient, is a statistic used to measure the similarity between sets. In the context of binary classification, it measures the overlap between predicted and actual positive labels.

### Mathematical Definition

The Jaccard Index is defined as the size of the intersection divided by the size of the union of two sets:

$$
\text{Jaccard Index} = \frac{|A \cap B|}{|A \cup B|} = \frac{|A \cap B|}{|A| + |B| - |A \cap B|}
$$

### In the Context of Binary Classification
1. **Intersection ($A \cap B$):** The number of positions where both the predicted and true labels are 1 (True Positives).  
2. **Union ($A \cup B$):** The number of positions where either the predicted or true labels (or both) are 1.  

### Key Properties
1. **Range:** The Jaccard Index always falls between 0 and 1 (inclusive).  
2. **Perfect Match:** A value of 1 indicates identical sets.  
3. **No Overlap:** A value of 0 indicates disjoint sets.  
4. **Symmetry:** The index is symmetric, meaning $J(A, B) = J(B, A)$.  

### Example
Consider two binary vectors:  
- **True labels:** [1, 0, 1, 1, 0, 1]  
- **Predicted labels:** [1, 0, 1, 0, 0, 1]  

In this case:  
1. **Intersection** (positions where both are 1): 3.  
2. **Union** (positions where either is 1): 4.  
3. **Jaccard Index**: $3 / 4 = 0.75$.

### Usage in Machine Learning
The Jaccard Index is particularly useful in:  
1. Evaluating clustering algorithms.  
2. Comparing binary classification results.  
3. Document similarity analysis.  
4. Image segmentation evaluation.  

When implementing the Jaccard Index, it's important to handle edge cases, such as when both sets are empty (in which case the index is typically defined as 0).


### meta.json

```json
{
  "id": "72",
  "title": "Calculate Jaccard Index for Binary Classification",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/rittik9",
      "name": "rittik9"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def jaccard_index(y_true, y_pred):
    intersection = np.sum((y_true == 1) & (y_pred == 1))
    union = np.sum((y_true == 1) | (y_pred == 1))
    result = intersection / union
    if np.isnan(result):
        return 0.0
    return round(result, 3)
```




### starter_code.py

```python
import numpy as np


def jaccard_index(y_true, y_pred):
    # Write your code here
    return round(result, 3)
```




### tests.json

```json
[
  {
    "test": "\n# Test case 1: Perfect match\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 1, 0, 1])\nprint(jaccard_index(y_true, y_pred))\n",
    "expected_output": "1.0"
  },
  {
    "test": "\n# Test case 2: No overlap\ny_true = np.array([1, 0, 1, 1, 0, 0])\ny_pred = np.array([0, 1, 0, 0, 1, 1])\nprint(jaccard_index(y_true, y_pred))\n",
    "expected_output": "0.0"
  },
  {
    "test": "\n# Test case 3: Partial overlap\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([1, 0, 1, 0, 0, 0])\nprint(jaccard_index(y_true, y_pred))\n",
    "expected_output": "0.5"
  },
  {
    "test": "\ny_true = np.array([1, 0, 1, 1, 0, 1])\ny_pred = np.array([0, 1, 0, 1, 1, 0])\nprint(jaccard_index(y_true, y_pred))\n",
    "expected_output": "0.167"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/72_calculate-jaccard-index-for-binary-classification/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/72_calculate-jaccard-index-for-binary-classification/description.md)。Deep-ML：Educational Use Only License。
