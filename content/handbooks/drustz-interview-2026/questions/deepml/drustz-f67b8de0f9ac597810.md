---
id: drustz-f67b8de0f9ac597810
section: deepml
order: 85
level: A
title: Implement a Sparse Mixture of Experts Layer
quick: Deep-ML 练习 · Implement a Sparse Mixture of Experts Layer
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/125_implement-a-sparse-mixture-of-experts-layer/description.md
    type: primary
---
### description.md

Implement a Mixture-of-Experts (MoE) layer using softmax gating and top-k routing. Given an input tensor, a set of expert weight matrices, a gating weight matrix, and parameters specifying the number of experts and the value of k, compute the final MoE output by selecting the top-k experts per token, applying their transformations, and aggregating the results weighted by the normalized gating probabilities.


### example.json

```json
{
  "input": "x = np.arange(12).reshape(2, 3, 2)\nWe = np.ones((4, 2, 2))\nWg = np.ones((2, 4))\ntop_k = 1",
  "output": "[[[1, 1], [5, 5], [9, 9]], [[13, 13], [17, 17], [21, 21]]]",
  "reasoning": "Each token is routed to its top expert and processed using a weight matrix of ones. The result matches the input tokens due to identity transformation and weight 1."
}
```




### learn.md


## Mixture of Experts Layer

Mixture-of-Experts layers route each token through a small subset of expert networks, reducing computation while retaining flexibility.

### 1. Gating with Softmax  
- **Logits**: For each token $t$, compute a vector of gating scores $g_t \in \mathbb{R}^E$, where $E$ is the number of experts.  
- **Softmax**: Convert scores into a probability distribution  
  $$
  \alpha_{t,j}
    = \frac{\exp\bigl(g_{t,j} - \max_j g_{t,j}\bigr)}
           {\sum_{j'=1}^{E}\exp\bigl(g_{t,j'} - \max_j g_{t,j'}\bigr)}.
  $$

### 2. Top-$k$ Selection  
- **Sparsity**: Keep only the $k$ largest weights per token, zeroing out the rest.  
- **Renormalize**: For token $t$, let $\mathcal{K}_t$ be the indices of the top $k$ experts. Then  
  $$
  \tilde\alpha_{t,j} =
    \begin{cases}
      \displaystyle\frac{\alpha_{t,j}}{\sum_{i \in \mathcal{K}_t}\alpha_{t,i}}
        & j \in \mathcal{K}_t,\\[8pt]
      0
        & \text{otherwise.}
    \end{cases}
  $$

### 3. Expert Computation  
Each expert $i$ applies its own linear transform to the token embedding $x_t$:  
$$
O_t^{(i)} = x_t\,W_e^{(i)},
$$  
where $W_e^{(i)}$ is the expert's $d \times d$ weight matrix.

### 4. Weighted Aggregation  
Combine the selected experts' outputs for each token:  
$$
y_t = \sum_{i=1}^{E} \tilde\alpha_{t,i}\,O_t^{(i)}.
$$  
The result $y_t$ lives in the original embedding space $\mathbb{R}^d$.

---

### Example Walk Through

Suppose one sentence of length 2, embedding size 3, $E=4$ experts, and $k=2$.  
- After flattening, you get 2 softmax distributions of length 4.  
- You pick the top 2 experts for each token and renormalize their weights.  
- Each selected expert produces a 3-dimensional output for its tokens.  
- You weight and sum those outputs to yield the final 3-dimensional vector per token.

This sparse routing mechanism dramatically cuts computation only $k$ experts run per token instead of all $E$ while retaining the expressivity of a full ensemble.


### meta.json

```json
{
  "id": "125",
  "title": "Implement a Sparse Mixture of Experts Layer",
  "difficulty": "hard",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/lefarov",
      "name": "lefarov"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def get_top_k(arr: np.ndarray, k: int):
    idx = np.argpartition(arr, -k)[..., -k:]
    vals = np.take_along_axis(arr, idx, axis=-1)
    return idx, vals


def expert(x: np.ndarray, We_i: np.ndarray):
    # x: [n_tokens, d_model]
    # We_i: [d_model, d_model]
    return x @ We_i


def gate(x: np.ndarray, Wg: np.ndarray):
    # x: [n_batch * l_seq, d_model]
    # Wg: [n_batch * l_seq, n_experts]
    return x @ Wg


def moe(x: np.ndarray, We: np.ndarray, Wg: np.ndarray, n_experts: int, top_k: int):
    # x: [n_batch, l_seq, d_model]
    # We: [n_experts, d_model, d_model]
    # Wg: [n_batch * l_seq, n_experts]

    n_batch, l_seq, d_model = x.shape

    # flatten batch and sequence dimensions for easier indexing
    # x_flat: [n_batch * l_seq, d_model]
    x_flat = x.reshape(-1, d_model)
    n_tokens, _ = x_flat.shape

    gating_logits = gate(x_flat, Wg)
    gating_weights = softmax(gating_logits, axis=-1)

    topk_idx, topk_weights = get_top_k(gating_weights, top_k)
    topk_idx_flat = topk_idx.flatten()  # [n_tokens * top_k]
    # mapping from top K expert indices to token indices: [n_tokens * top_k]
    token_idx_flat = np.arange(n_tokens).repeat(top_k)

    topk_weights_norm = topk_weights / topk_weights.sum(axis=1, keepdims=True)
    topk_weights_norm_flat = topk_weights_norm.flatten()

    # prepare result memory for aggregation: [n_tokens, d_model]
    output_flat = np.zeros_like(x_flat)
    for i in range(n_experts):
        mask = topk_idx_flat == i
        tokens_expert_i = token_idx_flat[mask]

        if tokens_expert_i.size > 0:
            x_expert_i = x_flat[tokens_expert_i]
            output_expert_i = expert(x_expert_i, We[i, ...])
            output_expert_i *= topk_weights_norm_flat[mask, None]

            # scatter add to result memory
            np.add.at(output_flat, tokens_expert_i, output_expert_i)

    return output_flat.reshape(n_batch, l_seq, d_model)
```




### starter_code.py

```python
import numpy as np


def moe(
    x: np.ndarray, We: np.ndarray, Wg: np.ndarray, n_experts: int, top_k: int
) -> np.ndarray:
    """
    Args:
        x: Input tensor of shape (n_batch, l_seq, d_model)
        We: Expert weights of shape (n_experts, d_model, d_model)
        Wg: Gating weights of shape (d_model, n_experts)
        n_experts: Number of experts
        top_k: Number of experts to route each token to
    Returns:
        Output tensor of shape (n_batch, l_seq, d_model)
    """
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nnp.random.seed(42)\nd_model = 2\nn_experts = 4\nl_seq = 3\nn_batch = 2\ntop_k = 2\nx = np.random.rand(n_batch, l_seq, d_model)\nWe = np.random.rand(n_experts, d_model, d_model)\nWg = np.random.rand(d_model, n_experts)\noutput = moe(x, We, Wg, n_experts, top_k)\nprint(np.round(output, 4))",
    "expected_output": "[[[0.5148 0.4329]\n  [0.5554 0.5447]\n  [0.1285 0.102 ]]\n\n [[0.339  0.3046]\n  [0.5391 0.417 ]\n  [0.3597 0.3262]]]"
  },
  {
    "test": "import numpy as np\nnp.random.seed(42)\nd_model = 2\nn_experts = 4\nl_seq = 3\nn_batch = 2\ntop_k = 2\nx = np.random.rand(n_batch, l_seq, d_model)\nWe = np.zeros((n_experts, d_model, d_model))\nWg = np.random.rand(d_model, n_experts)\noutput = moe(x, We, Wg, n_experts, top_k)\nprint(output)",
    "expected_output": "[[[0. 0.]\n  [0. 0.]\n  [0. 0.]]\n\n [[0. 0.]\n  [0. 0.]\n  [0. 0.]]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/125_implement-a-sparse-mixture-of-experts-layer/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/125_implement-a-sparse-mixture-of-experts-layer/description.md)。Deep-ML：Educational Use Only License。
