---
id: drustz-fdbdcbc050f2618ad7
section: deepml
order: 60
level: A
title: Dropout Layer
quick: Deep-ML 练习 · Dropout Layer
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/151_dropout-layer/description.md
    type: primary
---
### description.md

Implement a dropout layer that applies random neuron deactivation during training to prevent overfitting in neural networks. The layer should randomly zero out a proportion of input elements based on a dropout rate p, scale the remaining values by 1/(1-p) to maintain expected values, and pass inputs unchanged during inference. During backpropagation, gradients must be masked with the same dropout pattern and scaled by the same factor to ensure proper gradient flow.


### example.json

```json
{
  "input": "x = np.array([1.0, 2.0, 3.0, 4.0]), grad = np.array([0.1, 0.2, 0.3, 0.4]), p = 0.5",
  "output": "output = array([[2., 0. , 6. , 0. ]]), grad = array([[0.2, 0. , 0.6, 0. ]])",
  "reasoning": "The Dropout layer randomly zeroes out elements of the input tensor with probability p during training. To maintain the expected value of the activations, the remaining elements are scaled by a factor of 1 / (1 - p). During inference, Dropout is disabled and the input is passed through unchanged. During backpropagation, the same dropout mask and scaling are applied to the gradients, ensuring the expected gradient magnitude is preserved."
}
```




### learn.md

# Implementing Dropout Layer

## Introduction
Dropout is a regularization technique that randomly deactivates neurons during training to prevent overfitting. It forces the network to learn with different neurons and prevents it from becoming too dependent on specific neurons.

## Learning Objectives
- Understand the concept and purpose of dropout
- Learn how dropout works during training and inference
- Implement dropout layer with proper scaling

## Theory
During training, dropout randomly sets a proportion of inputs to zero and scales up the remaining values to maintain the expected value. The mathematical formulation is:

During training:

$y = \dfrac{x \odot m}{1-p}$

During inference:

$y = x$

During backpropagation:

$grad = \dfrac{grad \odot m}{1-p}$

Where:
- $x$ is the input vector
- $m$ is a binary mask vector sampled from Bernoulli(p)
- $\odot$ represents element-wise multiplication
- $p$ is the dropout rate (probability of keeping a neuron)

The mask $m$ is randomly generated for each forward pass during training and is stored in memory to be used in the corresponding backward pass. This ensures that the same neurons are dropped during both forward and backward propagation for a given input.

The scaling factor $\frac{1}{1-p}$ during training ensures that the expected value of the output matches the input, making the network's behavior consistent between training and inference.

During backpropagation, the gradients must also be scaled by the same factor $\frac{1}{1-p}$ to maintain the correct gradient flow.

Dropout acts as a form of regularization by:
1. Preventing co-adaptation of neurons, forcing them to learn more robust features that are useful in combination with many different random subsets of other neurons
2. Creating an implicit ensemble of networks, as each forward pass uses a different subset of neurons, effectively training multiple networks that share parameters
3. Reducing the effective capacity of the network during training, which helps prevent overfitting by making the model less likely to memorize the training data

Read more at:

1. Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. (2014). Dropout: A Simple Way to Prevent Neural Networks from Overfitting. Journal of Machine Learning Research, 15(1), 1929-1958. [PDF](https://www.cs.toronto.edu/~hinton/absps/JMLRdropout.pdf)

## Problem Statement
Implement a dropout layer class that can be used during both training and inference phases of a neural network. The implementation should:

1. Apply dropout during training by randomly zeroing out elements
2. Scale the remaining values appropriately to maintain expected values
3. Pass through inputs unchanged during inference
4. Support backpropagation by storing and using the dropout mask

### Requirements
The `DropoutLayer` class should implement:

1. `__init__(p: float)`: Initialize with dropout probability p
2. `forward(x: np.ndarray, training: bool = True) -> np.ndarray`: Apply dropout during forward pass
3. `backward(grad: np.ndarray) -> np.ndarray`: Handle gradient flow during backpropagation

### Input Parameters
- `p`: Dropout rate (probability of keeping a neuron), must be between 0 and 1
- `x`: Input tensor of any shape
- `training`: Boolean flag indicating if in training mode
- `grad`: Gradient tensor during backpropagation

### Output
- Forward pass: Tensor of same shape as input with dropout applied
- Backward pass: Gradient tensor with dropout mask applied

## Example
```python
# Example usage:
x = np.array([1.0, 2.0, 3.0, 4.0])
grad = np.array([0.1, 0.2, 0.3, 0.4])
p = 0.5  # 50% dropout rate

# During training
output_train = dropout_layer(x, p, training=True)

# During inference
output_inference = dropout_layer(x, p, training=False)

# Backward
grad_back = dropout.backward(grad)
```



## Tips
- Use numpy's random binomial generator for creating the mask
- Remember to scale up the output and gradients during training by 1/(1-p)
- Test with different dropout rates (typically between 0.2 and 0.5)
- Verify that the expected value of the output matches the input

## Common Pitfalls
- Using the same mask for all examples in a batch
- Setting dropout rate too high (can lead to underfitting)

---


### meta.json

```json
{
  "id": "151",
  "title": "Dropout Layer",
  "difficulty": "medium",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/mavleo96",
      "name": "Vijayabharathi Murugan"
    }
  ],
  "pytorch_difficulty": "easy"
}
```




### solution.py

```python
import torch
import torch.nn as nn


class DropoutLayer(nn.Module):
    def __init__(self, p: float):
        """Initialize the dropout layer."""
        super(DropoutLayer, self).__init__()
        if p < 0 or p >= 1:
            raise ValueError("Dropout rate must be between 0 and 1 (1-exclusive)")

        self.p = p
        self.mask = None

    def forward(self, x: torch.Tensor, training: bool = True) -> torch.Tensor:
        """Forward pass of the dropout layer."""
        if not training:
            return x

        self.mask = torch.bernoulli(torch.ones_like(x) * (1 - self.p))

        return x * self.mask / (1 - self.p)

    def backward(self, grad: torch.Tensor) -> torch.Tensor:
        """Backward pass of the dropout layer."""
        if self.mask is None:
            raise ValueError("Forward pass must be called before backward pass")

        return grad * self.mask / (1 - self.p)
```




### starter_code.py

```python
import torch


class DropoutLayer:
    def __init__(self, p: float):
        """Initialize the dropout layer."""
        # Your code here

    def forward(self, x: torch.Tensor, training: bool = True) -> torch.Tensor:
        """Forward pass of the dropout layer."""
        # Your code here

    def backward(self, grad: torch.Tensor) -> torch.Tensor:
        """Backward pass of the dropout layer."""
        # Your code here
```




### tests.json

```json
[
  {
    "test": "import torch\ntorch.manual_seed(42)\nx = torch.tensor([[1.0, 2.0], [3.0, 4.0]])\ngrad = torch.tensor([[0.5, 0.2], [1.0, 2.0]])\n\ndropout = DropoutLayer(0.2)\n\nprint(dropout.forward(x, training=True), dropout.forward(x, training=False), dropout.backward(grad))",
    "expected_output": "(tensor([[0., 0.], [3.75, 0.]]), tensor([[1.0, 2.0], [3.0, 4.0]]), tensor([[0., 0.], [1.25, 0.]]))"
  },
  {
    "test": "import torch\ntorch.manual_seed(42)\nx = torch.ones((1000, 1000))\ndropout = DropoutLayer(0.2)\n\n_ = dropout.forward(x, training=True)\nmask1 = dropout.mask.clone()\n_ = dropout.forward(x, training=True)\nmask2 = dropout.mask.clone()\nprint(mask1.equal(mask2))",
    "expected_output": "False"
  },
  {
    "test": "import torch\ntorch.manual_seed(42)\nx = torch.ones((1000, 1000))\ndropout = DropoutLayer(0.3)\noutput_train = dropout.forward(x, training=True)\nmean_output = torch.mean(output_train)\nprint(abs(mean_output - 1.0).item() < 0.1)",
    "expected_output": "True"
  },
  {
    "test": "p = 1.5\ntry:\n    dropout = DropoutLayer(p)\n    raise AssertionError('Expected ValueError for p = 1.5')\nexcept ValueError:\n    pass\np = -0.5\ntry:\n    dropout = DropoutLayer(p)\n    raise AssertionError('Expected ValueError for p = -0.5')\nexcept ValueError:\n    pass\nprint('All tests passed')",
    "expected_output": "All tests passed"
  }
]
```




### solution.py

```python
import numpy as np


class DropoutLayer:
    def __init__(self, p: float):
        """Initialize the dropout layer."""
        if p < 0 or p >= 1:
            raise ValueError("Dropout rate must be between 0 and 1 (1-exclusive)")

        self.p = p
        self.mask = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """Forward pass of the dropout layer."""
        if not training:
            return x

        self.mask = np.random.binomial(1, 1 - self.p, x.shape)

        return x * self.mask / (1 - self.p)

    def backward(self, grad: np.ndarray) -> np.ndarray:
        """Backward pass of the dropout layer."""
        if self.mask is None:
            raise ValueError("Forward pass must be called before backward pass")

        return grad * self.mask / (1 - self.p)
```




### starter_code.py

```python
import numpy as np


class DropoutLayer:
    def __init__(self, p: float):
        """Initialize the dropout layer."""
        # Your code here

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """Forward pass of the dropout layer."""
        # Your code here

    def backward(self, grad: np.ndarray) -> np.ndarray:
        """Backward pass of the dropout layer."""
        # Your code here
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nnp.random.seed(42)\nx = np.array([[1.0, 2.0], [3.0, 4.0]])\ngrad = np.array([[0.5, 0.2], [1.0, 2.0]])\n\ndropout = DropoutLayer(0.2)\n\nprint(dropout.forward(x, training=True), dropout.forward(x, training=False), dropout.backward(grad))",
    "expected_output": "(array([[1.25, 0.], [3.75, 5.]]), array([[1.0, 2.0], [3.0, 4.0]]), array([[0.625, 0.], [1.25, 2.5]]))"
  },
  {
    "test": "import numpy as np\nnp.random.seed(42)\nx = np.ones((1000, 1000))\ndropout = DropoutLayer(0.2)\n\n_ = dropout.forward(x, training=True)\nmask1 = dropout.mask.copy()\n_ = dropout.forward(x, training=True)\nmask2 = dropout.mask.copy()\nprint(np.array_equal(mask1, mask2))",
    "expected_output": "False"
  },
  {
    "test": "import numpy as np\nnp.random.seed(42)\nx = np.ones((1000, 1000))\ndropout = DropoutLayer(0.3)\n\noutput_train = dropout.forward(x, training=True)\nmean_output = np.mean(output_train)\nprint(abs(mean_output - 1.0) < 0.1)",
    "expected_output": "True"
  },
  {
    "test": "p = 1.5\ntry:\n    dropout = DropoutLayer(p)\n    raise AssertionError('Expected ValueError for p = 1.5')\nexcept ValueError:\n    pass\np = -0.5\ntry:\n    dropout = DropoutLayer(p)\n    raise AssertionError('Expected ValueError for p = -0.5')\nexcept ValueError:\n    pass\nprint('All tests passed')",
    "expected_output": "All tests passed"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/151_dropout-layer/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/151_dropout-layer/description.md)。Deep-ML：Educational Use Only License。
