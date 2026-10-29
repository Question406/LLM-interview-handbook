---
id: drustz-6b4e3db5897c3cf7a5
section: deepml
order: 167
level: A
title: Single Neuron with Backpropagation
quick: Deep-ML 练习 · Single Neuron with Backpropagation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/25_single-neuron-with-backpropagation/description.md
    type: primary
---
### description.md

Write a Python function that simulates a single neuron with sigmoid activation, and implements backpropagation to update the neuron's weights and bias. The function should take a list of feature vectors, associated true binary labels, initial weights, initial bias, a learning rate, and the number of epochs. The function should update the weights and bias using gradient descent based on the MSE loss, and return the updated weights, bias, and a list of MSE values for each epoch, each rounded to four decimal places.


### example.json

```json
{
  "input": "features = [[1.0, 2.0], [2.0, 1.0], [-1.0, -2.0]], labels = [1, 0, 0], initial_weights = [0.1, -0.2], initial_bias = 0.0, learning_rate = 0.1, epochs = 2",
  "reasoning": "The neuron receives feature vectors and computes predictions using the sigmoid activation. Based on the predictions and true labels, the gradients of MSE loss with respect to weights and bias are computed and used to update the model parameters across epochs.",
  "output": "updated_weights = [0.1036, -0.1425], updated_bias = -0.0167, mse_values = [0.3033, 0.2942]"
}
```




### learn.md


## Neural Network Learning with Backpropagation

This task involves implementing backpropagation for a single neuron in a neural network. The neuron processes inputs and updates parameters to minimize the Mean Squared Error (MSE) between predicted outputs and true labels.

### Mathematical Background

**Forward Pass**  
Compute the neuron output by calculating the dot product of the weights and input features, and adding the bias:
$$
z = w_1x_1 + w_2x_2 + \dots + w_nx_n + b
$$
$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

**Loss Calculation (MSE)**  
The Mean Squared Error quantifies the error between the neuron's predictions and the actual labels:
$$
MSE = \frac{1}{n} \sum_{i=1}^{n} (\sigma(z_i) - y_i)^2
$$

### Backward Pass (Gradient Calculation)
Compute the gradient of the MSE with respect to each weight and the bias. This involves the partial derivatives of the loss function with respect to the output of the neuron, multiplied by the derivative of the sigmoid function:
$$
\frac{\partial MSE}{\partial w_j} = \frac{2}{n} \sum_{i=1}^{n} (\sigma(z_i) - y_i) \sigma'(z_i) x_{ij}
$$
$$
\frac{\partial MSE}{\partial b} = \frac{2}{n} \sum_{i=1}^{n} (\sigma(z_i) - y_i) \sigma'(z_i)
$$

### Parameter Update
Update each weight and the bias by subtracting a portion of the gradient, determined by the learning rate:
$$
w_j = w_j - \alpha \frac{\partial MSE}{\partial w_j}
$$
$$
b = b - \alpha \frac{\partial MSE}{\partial b}
$$

### Practical Implementation
This process refines the neuron's ability to predict accurately by iteratively adjusting the weights and bias based on the error gradients, optimizing the neural network's performance over multiple iterations.


### meta.json

```json
{
  "id": "25",
  "title": "Single Neuron with Backpropagation",
  "difficulty": "medium",
  "category": "Deep Learning",
  "video": "https://youtu.be/LPfsTFcFqU4",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/evintunador",
      "name": "evintunador"
    }
  ],
  "tinygrad_difficulty": "medium",
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch
from typing import List, Tuple, Union


def train_neuron(
    features: Union[List[List[float]], torch.Tensor],
    labels: Union[List[float], torch.Tensor],
    initial_weights: Union[List[float], torch.Tensor],
    initial_bias: float,
    learning_rate: float,
    epochs: int,
) -> Tuple[List[float], float, List[float]]:

    # Ensure tensors
    X = torch.as_tensor(features, dtype=torch.float)
    y = torch.as_tensor(labels, dtype=torch.float)
    w = torch.as_tensor(initial_weights, dtype=torch.float)
    b = torch.tensor(initial_bias, dtype=torch.float)

    n = y.shape[0]
    mse_values: List[float] = []

    for _ in range(epochs):
        # Forward
        z = X @ w + b  # (n,)
        preds = torch.sigmoid(z)  # (n,)
        errors = preds - y  # (n,)

        # MSE
        mse = torch.mean(errors**2).item()
        mse_values.append(round(mse, 4))

        # Manual gradients (chain-rule): dMSE/dz = 2/n * (preds-y) * σ'(z)
        sigma_prime = preds * (1 - preds)
        delta = (2.0 / n) * errors * sigma_prime  # (n,)

        grad_w = X.t() @ delta  # (f,)
        grad_b = delta.sum()  # scalar

        # Parameter update (gradient descent)
        w -= learning_rate * grad_w
        b -= learning_rate * grad_b

    # Round final params for return
    updated_weights = [round(val, 4) for val in w.tolist()]
    updated_bias = round(b.item(), 4)
    return updated_weights, updated_bias, mse_values
```




### starter_code.py

```python
import torch
from typing import List, Tuple, Union


def train_neuron(
    features: Union[List[List[float]], torch.Tensor],
    labels: Union[List[float], torch.Tensor],
    initial_weights: Union[List[float], torch.Tensor],
    initial_bias: float,
    learning_rate: float,
    epochs: int,
) -> Tuple[List[float], float, List[float]]:
    """
    Train a single neuron (sigmoid activation) with mean-squared-error loss.

    Returns (updated_weights, updated_bias, mse_per_epoch)
    — weights & bias are rounded to 4 decimals; each MSE value is rounded too.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "import torch\nuw, ub, mses = train_neuron(\n    torch.tensor([[1.0, 2.0], [2.0, 1.0], [-1.0, -2.0]]),\n    torch.tensor([1, 0, 0]),\n    torch.tensor([0.1, -0.2]),\n    0.0,\n    0.1,\n    2\n)\nprint((uw, ub, mses))",
    "expected_output": "([0.1036, -0.1425], -0.0167, [0.3033, 0.2942])"
  },
  {
    "test": "import torch\nuw, ub, mses = train_neuron(\n    torch.tensor([[1, 2], [2, 3], [3, 1]]),\n    torch.tensor([1, 0, 1]),\n    torch.tensor([0.5, -0.2]),\n    0.0,\n    0.1,\n    3\n)\nprint((uw, ub, mses))",
    "expected_output": "([0.4892, -0.2301], 0.0029, [0.21, 0.2087, 0.2076])"
  }
]
```




### solution.py

```python
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def train_neuron(
    features, labels, initial_weights, initial_bias, learning_rate, epochs
):
    weights = np.array(initial_weights)
    bias = initial_bias
    features = np.array(features)
    labels = np.array(labels)
    mse_values = []

    for _ in range(epochs):
        z = np.dot(features, weights) + bias
        predictions = sigmoid(z)

        mse = np.mean((predictions - labels) ** 2)
        mse_values.append(round(mse, 4))

        # Gradient calculation for weights and bias
        errors = predictions - labels
        weight_gradients = (2 / len(labels)) * np.dot(
            features.T, errors * predictions * (1 - predictions)
        )
        bias_gradient = (2 / len(labels)) * np.sum(
            errors * predictions * (1 - predictions)
        )

        # Update weights and bias
        weights -= learning_rate * weight_gradients
        bias -= learning_rate * bias_gradient

        # Round weights and bias for output
        updated_weights = np.round(weights, 4)
        updated_bias = round(bias, 4)

    return updated_weights.tolist(), updated_bias, mse_values
```




### starter_code.py

```python
import numpy as np


def train_neuron(
    features: np.ndarray,
    labels: np.ndarray,
    initial_weights: np.ndarray,
    initial_bias: float,
    learning_rate: float,
    epochs: int,
) -> (np.ndarray, float, list[float]):
    # Your code here
    return updated_weights, updated_bias, mse_values
```




### tests.json

```json
[
  {
    "test": "print(train_neuron(np.array([[1.0, 2.0], [2.0, 1.0], [-1.0, -2.0]]), np.array([1, 0, 0]), np.array([0.1, -0.2]), 0.0, 0.1, 2))",
    "expected_output": "([0.1036, -0.1425], -0.0167, [0.3033, 0.2942])"
  },
  {
    "test": "print(train_neuron(np.array([[1, 2], [2, 3], [3, 1]]), np.array([1, 0, 1]), np.array([0.5, -0.2]), 0, 0.1, 3))",
    "expected_output": "([0.4892, -0.2301], 0.0029, [0.21, 0.2087, 0.2076])"
  }
]
```




### solution.py

```python
from tinygrad.tensor import Tensor
from typing import List, Tuple


def train_neuron_tg(
    features: List[List[float]],
    labels: List[float],
    initial_weights: List[float],
    initial_bias: float,
    learning_rate: float,
    epochs: int,
) -> Tuple[List[float], float, List[float]]:
    X = Tensor(features)
    y = Tensor(labels).reshape(len(labels), 1)
    w = Tensor(initial_weights).reshape(len(initial_weights), 1)
    b = Tensor(initial_bias)

    mse_values: List[float] = []
    n = len(labels)

    for _ in range(epochs):
        z = X.matmul(w) + b  # (n,1)
        preds = z.sigmoid()  # (n,1)
        errors = preds - y  # (n,1)

        mse = float(((errors**2).mean()).numpy())
        mse_values.append(round(mse, 4))

        sigma_prime = preds * (1 - preds)
        delta = (2.0 / n) * errors * sigma_prime  # (n,1)

        grad_w = X.T.matmul(delta)  # (f,1)
        grad_b = delta.sum()

        w -= Tensor(learning_rate) * grad_w
        b -= Tensor(learning_rate) * grad_b

    updated_weights = [round(val, 4) for val in w.numpy().flatten().tolist()]
    updated_bias = round(float(b.numpy()), 4)
    return updated_weights, updated_bias, mse_values
```




### starter_code.py

```python
from tinygrad.tensor import Tensor
from typing import List, Tuple


def train_neuron_tg(
    features: List[List[float]],
    labels: List[float],
    initial_weights: List[float],
    initial_bias: float,
    learning_rate: float,
    epochs: int,
) -> Tuple[List[float], float, List[float]]:
    """
    Tinygrad version — same contract as PyTorch implementation.
    """
    # Your implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "uw, ub, mses = train_neuron_tg(\n    [[1.0, 2.0], [2.0, 1.0], [-1.0, -2.0]],\n    [1, 0, 0],\n    [0.1, -0.2],\n    0.0,\n    0.1,\n    2\n)\nprint((uw, ub, mses))",
    "expected_output": "([0.1036, -0.1425], -0.0167, [0.3033, 0.2942])"
  },
  {
    "test": "uw, ub, mses = train_neuron_tg(\n    [[1, 2], [2, 3], [3, 1]],\n    [1, 0, 1],\n    [0.5, -0.2],\n    0.0,\n    0.1,\n    3\n)\nprint((uw, ub, mses))",
    "expected_output": "([0.4892, -0.2301], 0.0029, [0.21, 0.2087, 0.2076])"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/25_single-neuron-with-backpropagation/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/25_single-neuron-with-backpropagation/description.md)。Deep-ML：Educational Use Only License。
