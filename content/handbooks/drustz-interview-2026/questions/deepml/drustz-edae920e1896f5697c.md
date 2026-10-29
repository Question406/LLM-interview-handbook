---
id: drustz-edae920e1896f5697c
section: deepml
order: 174
level: A
title: The Pattern Weaver's Code
quick: Deep-ML 练习 · The Pattern Weaver's Code
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/89_the-pattern-weaver-s-code/description.md
    type: primary
---
### description.md

Deep in the Crystal Cave, the enigmatic Pattern Weaver creates stunning sequences by uncovering the intricate relationships between crystals. Each crystal is marked by a unique numeric value, and the Weaver emphasizes that the true power of any crystal depends on how it interacts with all others. You have discovered N crystals, each with a specific value, and your task is to reveal their enhanced patterns by analyzing these relationships using self-attention. Given a sequence of crystals and their values, your task is to implement a simplified self-attention mechanism. For each crystal, calculate its relationship with every other crystal, compute the attention scores using the softmax function, and derive the final weighted pattern for each crystal. This Problem was made with the help of GroundZero AI


### example.json

```json
{
  "input": "number of crystals: 5\nvalues: 4 2 7 1 9\n dimension: 1",
  "output": "[8.9993, 8.9638, 9.0, 8.7259, 9.0]",
  "reasoning": "The self-attention mechanism calculates relationships (attention scores) for each crystal using the given formula. These scores are converted to probabilities using the softmax function, and the final weighted pattern for each crystal is derived by summing the weighted values."
}
```




### learn.md

## Understanding Self-Attention

Self-attention is a core concept in modern deep learning architectures, particularly transformers. It helps a model understand relationships between elements in a sequence by comparing each element with every other element.

### Key Formula

The attention score between two elements $i$ and $j$ is calculated as:

$$
\text{Attention Score}_{i,j} = \frac{\text{Value}_i \times \text{Value}_j}{\sqrt{\text{Dimension}}}
$$

### Softmax Function

The softmax function converts raw attention scores into probabilities:

$$
\text{Softmax}(x_i) = \frac{e^{x_i}}{\sum_{j} e^{x_j}}
$$

### Weighted Sum

Using the softmax scores, the final value for each element is calculated as a weighted sum:

$$
\text{Final Value}_i = \sum_{j} \text{Softmax Score}_{i,j} \times \text{Value}_j
$$

### Example Calculation

Consider the following values:

- Crystal values: $[4, 2, 7, 1, 9]$
- Dimension: $1$

#### Step 1: Calculate Attention Scores

For crystal $i = 1$ ($4$):

$$
\text{Score}_{1,1} = \frac{4 \times 4}{\sqrt{1}} = 16,
\quad \text{Score}_{1,2} = \frac{4 \times 2}{\sqrt{1}} = 8,
\ldots
$$

#### Step 2: Apply Softmax

Convert scores to probabilities using softmax.

#### Step 3: Compute Weighted Sum

Multiply probabilities by crystal values and sum them to get the final value.

### Applications

Self-attention is widely used in:

- Natural Language Processing (e.g., transformers)
- Computer Vision (e.g., Vision Transformers)
- Sequence Analysis

Mastering self-attention provides a foundation for understanding advanced AI architectures.


### meta.json

```json
{
  "id": "89",
  "title": "The Pattern Weaver's Code",
  "difficulty": "medium",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://discord.gg/27N5vXdPW4",
      "name": "GroundZero AI"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def softmax(values):
    exps = np.exp(values - np.max(values))
    return exps / np.sum(exps)


def pattern_weaver(n, crystal_values, dimension):
    dimension_sqrt = np.sqrt(dimension)
    final_patterns = []

    for i in range(n):
        attention_scores = []
        for j in range(n):
            score = crystal_values[i] * crystal_values[j] / dimension_sqrt
            attention_scores.append(score)

        softmax_scores = softmax(attention_scores)
        weighted_sum = sum(softmax_scores[k] * crystal_values[k] for k in range(n))
        final_patterns.append(round(weighted_sum, 4))

    return final_patterns
```




### starter_code.py

```python
import numpy as np


def softmax(values):
    # Implement the softmax function
    pass


def pattern_weaver(n, crystal_values, dimension):
    # Your code here
    return np.round(x, 3)
```




### tests.json

```json
[
  {
    "test": "print(pattern_weaver(5, [4, 2, 7, 1, 9], 1))",
    "expected_output": "[8.9993, 8.9638, 9.0, 8.7259, 9.0]"
  },
  {
    "test": "print(pattern_weaver(3, [1, 3, 5], 1))",
    "expected_output": "[4.7019, 4.995, 4.9999]"
  },
  {
    "test": "print(pattern_weaver(4, [2, 8, 6, 4], 1))",
    "expected_output": "[7.9627, 8.0, 8.0, 7.9993]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/89_the-pattern-weaver-s-code/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/89_the-pattern-weaver-s-code/description.md)。Deep-ML：Educational Use Only License。
