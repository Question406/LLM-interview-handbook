---
id: drustz-ca2ba2f77bf7c92ede
section: deepml
order: 113
level: A
title: Implement SwiGLU activation function
quick: Deep-ML 练习 · Implement SwiGLU activation function
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/156_implement_SwiGLU_activation_function/description.md
    type: primary
---
### description.md

## Problem

Implement a Python function that applies the **SwiGLU activation function** to a NumPy array.

Assume the input array has already been passed through a linear projection and has shape `(batch_size, 2d)`. Round each output to four decimal places and return the result as a NumPy array of the shape `(batch_size, d)`.


### example.json

```json
{
  "input": "np.array([[1, -1, 1000, -1000]])",
  "output": "[[1000., 0.]]",
  "reasoning": "The input is of shape (1, 4), so it is split into x1 = [1, -1] and x2 = [1000, -1000]. The sigmoid of 1000 is approximately 1, and the sigmoid of -1000 is approximately 0 due to saturation. Thus, Swish(1000) ≈ 1000 x 1 = 1000 and Swish(-1000) ≈ -1000 x 0 = 0. Then, SwiGLU = x1 * Swish(x2) = [1 x 1000, -1 x 0] = [1000, 0]."
}
```




### learn.md

## Understanding the SwiGLU Activation Function

As the name suggests the SwiGLU activation function is a combination of two activations - Swish (implemented as SiLU in PyTorch) and GLU (Gated Linear Unit). It is important that we understand Swish and GLU because SwiGLU inherits properties from both — the smooth self-gating behavior of Swish, the decoupled gating structure of GLU.

### Swish Activation (Self-Gating)

**Swish**, introduced by Google Brain, is a smooth, self-gated activation function defined as:

$$
\text{Swish}(x) = x \cdot \sigma(x)
$$

where the sigmoid function is:

$$
\sigma(x) = \frac{1}{1 + e^{-x}}
$$

In Swish, the same input $x$ is used to:
  - **Compute the gate**: $\sigma(x)$
  - **Modulate itself**: $x \cdot \sigma(x)$

This is called **self-gating** — the input both **creates** and **passes through** the gate. \
**Note:** When written in a PyTorch forward loop, it looks something like -
```text
import torch.nn.functional as F

def forward(self, x):
   x1 = self.fc1(x)   # x1 = Wx + b where W, b are learnable params
   output = F.silu(x) # output = x1 * sigmoid(x1) 
   return output      # output = (Wx + b) * sigmoid(Wx + b)
```

This essentially means that the gate is learnable, and the model learns the best shape of the activation function.

### Gated Linear Unit (GLU)

**GLU**, introduced in *Language Modeling with Gated Convolutional Networks* (Dauphin et al., 2017), is a gated activation mechanism defined as:

$$
\text{GLU}(x_1, x_2) = x_1 \cdot \sigma(x_2)
$$

Here:
- $x_1$ is the **input signal**.
- $x_2$ is used to **compute the gate** via the sigmoid function.

In practice, both $x_1$ and $x_2$ are obtained by **splitting the output of a single linear layer**:

```text
import torch.nn.functional as F

def forward(self, x):
   x_proj = self.fc1(x)                
   x1, x2 = x_proj.chunk(2, dim=-1)    # x1 = Wx + b, x2 = Vx + c
   output = x1 * torch.sigmoid(x2)     # GLU = x1 · σ(x2)
   return output
```

So GLU can be rewritten as:

$$
\text{GLU}(x) = x_1 \cdot \sigma(x_2)
$$
where:
$$x_1 = W x + b$$
 $$x_2 = V x + c$$


This is a learned, cross-gating mechanism — the model learns different parameters for the signal and the gate.


## SwiGLU

With Swish and GLU out of the way, it becomes very easy to understand **SwiGLU**. It is defined as:

$$
\text{SwiGLU}(x) = x_1 \cdot \text{Swish}(x_2)
$$

Where:
- $x_1, x_2$ are typically obtained by splitting a linear projection of the input (inspired by GLU).

- $\text{Swish}(x_2) = x_2 \cdot \sigma(x_2)$ is the self-gated activation.

So putting it together:

$$
\text{SwiGLU}(x) = x_1 \cdot (x_2 \cdot \sigma(x_2))
$$

This combines the **signal-gate decoupling** of GLU with the **smooth self-gating** of Swish, and is used in the feed-forward blocks of large-scale models like Google's PaLM, Meta's LLaMA.


### Why Does It Work?
> Noam Shazeer, the author in his paper writes: "We offer no explanation as to why these architectures seem to work; we attribute their success, as all else, to divine benevolence."

The improvement in performance have only been proven *emprically* by observing faster convergence during training

### meta.json

```json
{
  "id": "151",
  "title": "Implement SwiGLU activation function",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/PT-10",
      "name": "PT-10"
    }
  ],
  "pytorch_difficulty": "easy"
}
```




### solution.py

```python
import torch


def SwiGLU(x: torch.Tensor) -> torch.Tensor:
    """
    Apply the SwiGLU activation function.
    Assumes:
      - Input x is a torch tensor of shape (batch_size, 2d)
      - x has already been passed through a linear projection layer

    Returns:
      - Tensor of shape (batch_size, d) after applying SwiGLU:
        x1 * SiLU(x2), where [x1, x2] = split(x)
    """
    x1, x2 = x.chunk(2, dim=-1)
    return x1 * torch.nn.functional.silu(x2)
```




### starter_code.py

```python
import torch


def swiglu(x: torch.Tensor) -> torch.Tensor:
    """
    Apply the SwiGLU activation function.
    Assumes:
      - Input x is a torch tensor of shape (batch_size, 2d)
      - x has already been passed through a linear projection layer

    Returns:
      - Tensor of shape (batch_size, d) after applying SwiGLU:
    """
    return scores
```




### tests.json

```json
[
  {
    "test": "print(torch.round(SwiGLU(torch.tensor([[0., 0., 0., 0.]])), decimals=4))",
    "expected_output": "tensor([[0., 0.]])"
  },
  {
    "test": "print(torch.round(SwiGLU(torch.tensor([[1.0, -1.0, 2.0, -2.0]])), decimals=4))",
    "expected_output": "tensor([[1.7616, 0.2384]])"
  },
  {
    "test": "print(torch.round(SwiGLU(torch.tensor([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])), decimals=4))",
    "expected_output": "tensor([[2.8577, 7.8561], [34.9681, 47.9839], [98.9984, 119.9992]])"
  }
]
```




### solution.py

```python
import numpy as np


def SwiGLU(x: np.ndarray) -> np.ndarray:
    """
    Args:
        x: np.ndarray of shape (batch_size, 2d)

    Returns:
        np.ndarray of shape (batch_size, d)
    """

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    d = x.shape[1] // 2
    x1 = x[:, :d]
    x2 = x[:, d:]
    return x1 * (x2 * sigmoid(x2))
```




### starter_code.py

```python
import numpy as np


def SwiGLU(x: np.ndarray) -> np.ndarray:
    """
    Args:
        x: np.ndarray of shape (batch_size, 2d)

    Returns:
        np.ndarray of shape (batch_size, d)
    """
    # Your code here
    return scores
```




### tests.json

```json
[
  {
    "test": "print(np.round(SwiGLU(np.zeros((1, 4))), 4))",
    "expected_output": "[[0., 0.]]"
  },
  {
    "test": "print(np.round(SwiGLU(np.array([[1.0, -1.0, 2.0, -2.0]])), 4))",
    "expected_output": "[[1.7616, 0.2384]]"
  },
  {
    "test": "print(np.round(SwiGLU(np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])), 4))",
    "expected_output": "[[2.8577, 7.8561], [34.9681, 47.9839], [98.9983, 119.9993]]"
  }
]
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/156_implement_SwiGLU_activation_function/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/156_implement_SwiGLU_activation_function/description.md)。Deep-ML：Educational Use Only License。
