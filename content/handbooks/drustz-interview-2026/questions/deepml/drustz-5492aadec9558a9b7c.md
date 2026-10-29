---
id: drustz-5492aadec9558a9b7c
section: deepml
order: 120
level: A
title: Implement the Noisy Top-K Gating Function
quick: Deep-ML 练习 · Implement the Noisy Top-K Gating Function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/124_implement-the-noisy-top-k-gating-function/description.md
    type: primary
---
### description.md

Implement the Noisy Top-K gating mechanism used in Mixture-of-Experts (MoE) models. Given an input matrix, weight matrices, pre-sampled noise, and a sparsity constraint k, compute the final gating probabilities matrix.


### example.json

```json
{
  "input": "X = [[1.0, 2.0]]\nW_g = [[1.0, 0.0], [0.0, 1.0]]\nW_noise = [[0.5, 0.5], [0.5, 0.5]]\nN = [[1.0, -1.0]]\nk = 2",
  "output": "[[0.917, 0.0825]]",
  "reasoning": "This example demonstrates that the gating function produces a sparse softmax output, favoring the higher gate after noise perturbation."
}
```




### learn.md

## Noisy Top-K Gating

Noisy Top-K Gating is a sparse selection mechanism used in Mixture-of-Experts (MoE) models. It routes input tokens to a subset of available experts, enhancing efficiency and model capacity.

### Overview

The core idea is to add learned noise to the gating logits and then select only the top-k experts for each input. This encourages exploration and helps balance load across experts.

### Step-by-Step Breakdown

1. **Compute Raw Gate Scores**  
   First, compute two linear projections of the input:
   $$
   H_{\text{base}} = X W_g
   $$
   $$
   H_{\text{noise}} = X W_{\text{noise}}
   $$

2. **Apply Noise with Softplus Scaling**  
   Add pre-sampled Gaussian noise, scaled by a softplus transformation:
   $$
   H = H_{\text{base}} + N \odot \text{Softplus}(H_{\text{noise}})
   $$

3. **Top-K Masking**  
   Keep only the top-k elements in each row (i.e., per input), setting the rest to $-\infty$:
   $$
   H' = \text{TopK}(H, k)
   $$

4. **Softmax Over Top-K**  
   Normalize the top-k scores into a valid probability distribution:
   $$
   G = \text{Softmax}(H')
   $$

### Worked Example

Let:
- $X = [[1.0, 2.0]]$
- $W_g = [[1.0, 0.0], [0.0, 1.0]]$
- $W_{\text{noise}} = [[0.5, 0.5], [0.5, 0.5]]$
- $N = [[1.0, -1.0]]$
- $k = 2$

Step-by-step:
- $H_{\text{base}} = [1.0, 2.0]$
- $H_{\text{noise}} = [1.5, 1.5]$
- $\text{Softplus}(H_{\text{noise}}) \approx [1.804, 1.804]$
- $H = [1.0 + 1.804, 2.0 - 1.804] = [2.804, 0.196]$
- Softmax over these gives: $[0.917, 0.0825]$

### Benefits

- **Computational Efficiency**: Activates only k experts per input.
- **Load Balancing**: Injected noise encourages diversity in expert selection.
- **Improved Generalization**: Acts as a regularizer via noise-based gating.

This technique is used in large sparse models like GShard and Switch Transformers.


### meta.json

```json
{
  "id": "124",
  "title": "Implement the Noisy Top-K Gating Function",
  "difficulty": "medium",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def noisy_topk_gating(
    X: np.ndarray, W_g: np.ndarray, W_noise: np.ndarray, N: np.ndarray, k: int
) -> np.ndarray:
    H_base = X @ W_g
    H_noise = X @ W_noise
    softplus = np.log1p(np.exp(H_noise))
    H = H_base + N * softplus

    def top_k_masked(row, k):
        mask = np.full_like(row, -np.inf)
        top_idx = np.argsort(row)[-k:]
        mask[top_idx] = row[top_idx]
        return mask

    masked_H = np.vstack([top_k_masked(row, k) for row in H])
    exps = np.exp(masked_H - np.max(masked_H, axis=1, keepdims=True))
    return exps / np.sum(exps, axis=1, keepdims=True)
```




### starter_code.py

```python
import numpy as np


def noisy_topk_gating(
    X: np.ndarray, W_g: np.ndarray, W_noise: np.ndarray, N: np.ndarray, k: int
) -> np.ndarray:
    """
    Args:
        X: Input data, shape (batch_size, features)
        W_g: Gating weight matrix, shape (features, num_experts)
        W_noise: Noise weight matrix, shape (features, num_experts)
        N: Noise samples, shape (batch_size, num_experts)
        k: Number of experts to keep per example
    Returns:
        Gating probabilities, shape (batch_size, num_experts)
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nnp.random.seed(0)\nX = np.array([[1.0, 2.0]])\nW_g = np.array([[1.0, 0.0], [0.0, 1.0]])\nW_noise = np.zeros((2,2))\nN = np.zeros((1,2))\nprint(noisy_topk_gating(X, W_g, W_noise, N, k=1))",
    "expected_output": "[[0. 1.]]"
  },
  {
    "test": "import numpy as np\nX = np.array([[1.0, 2.0]])\nW_g = np.array([[1.0, 0.0], [0.0, 1.0]])\nW_noise = np.array([[0.5, 0.5], [0.5, 0.5]])\nN = np.array([[1.0, -1.0]])\nprint(np.round(noisy_topk_gating(X, W_g, W_noise, N, k=2), 4))",
    "expected_output": "[[0.917, 0.083]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/124_implement-the-noisy-top-k-gating-function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/124_implement-the-noisy-top-k-gating-function/description.md)。Deep-ML：Educational Use Only License。
