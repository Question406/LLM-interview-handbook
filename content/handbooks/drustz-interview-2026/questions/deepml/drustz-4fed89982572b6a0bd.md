---
id: drustz-4fed89982572b6a0bd
section: deepml
order: 82
level: A
title: Implement a Simple CNN Training Function with Backpropagation
quick: Deep-ML 练习 · Implement a Simple CNN Training Function with Backpropagation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/130_implement-a-simple-cnn-training-function-with-back/description.md
    type: primary
---
### description.md

Create a function that trains a basic Convolutional Neural Network (CNN) using backpropagation. The network should include one convolutional layer with ReLU activation, followed by flattening and a dense layer with softmax output, and a cross entropy loss. You need to handle the forward pass, compute the loss gradients, and update the weights and biases using stochastic gradient descent. Ensure the function processes input data as grayscale images and one-hot encoded labels, and returns the trained weights and biases for the convolutional and dense layers.


### example.json

```json
{
  "input": "import numpy as np; np.random.seed(42); X = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]); y = np.array([[1, 0]]); print(train_simple_cnn_with_backprop(X, y, 1, 0.01, 3, 1))",
  "output": "(array([[[ 0.00501739],        [-0.00128214],        [ 0.00662764]],       [[ 0.01543131],        [-0.00209028],        [-0.00203986]],       [[ 0.01614389],        [ 0.00807636],        [-0.00424248]]]), array([5.02517066e-05]), array([[ 0.00635715, -0.00556573]]), array([ 0.00499531, -0.00499531]))",
  "reasoning": "The solution processes the input X through a forward pass, where it applies a convolutional layer with ReLU activation, flattens the output, and passes it through a dense layer with softmax to compute predictions and loss based on the one-hot encoded label y. In the backward pass, it calculates gradients using backpropagation for the weights and biases, then updates them using stochastic gradient descent with the specified learning rate, and returns the updated weights after one epoch."
}
```




### learn.md

## Understanding a Simple Convolutional Neural Network with Backpropagation

A **Convolutional Neural Network** (CNN) learns two things at once:  
1. **What to look for** - small filters (kernels) that detect edges, textures, etc.  
2. **How to combine those detections** - a dense layer that converts them into class probabilities.

Below is the full training loop broken into intuitive steps that can be implemented directly in NumPy.

---

### 1. Forward Pass

**Convolution**  
The convolution layer slides a small filter over the input and produces feature maps:

$$
Z^c[p, q, k] = \sum_{i, j} X[p+i, q+j] \cdot W^c[i, j, k] + b^c[k]
$$

This results in a tensor of shape $(H - k + 1, W - k + 1, F)$, where $H$ and $W$ are the input height and width, $k$ is the kernel size, and $F$ is the number of filters.

**ReLU Activation**

$$
A^c = \max(0, Z^c)
$$

This introduces non-linearity by zeroing out negative values.

**Flattening**

The feature maps are reshaped into a vector:

$$
A^f = \text{flatten}(A^c)
$$

**Dense Layer**

$$
Z^d = A^f \cdot W^d + b^d
$$

Each entry in $A^f$ contributes to every output class via weight matrix $W^d$ and bias $b^d$.

**Softmax Activation**

$$
\hat{y}_c = \frac{e^{Z^d_c}}{\sum_j e^{Z^d_j}}
$$

This converts raw scores into probabilities for classification.

---

### 2. Loss Function – Cross Entropy

For one-hot encoded label $y$ and prediction $\hat{y}$:

$$
\mathcal{L}(\hat{y}, y) = -\sum_c y_c \log(\hat{y}_c)
$$

This penalizes incorrect predictions based on confidence.

---

### 3. Backward Pass

**Gradient of Softmax + Cross Entropy**

$$
\frac{\partial \mathcal{L}}{\partial Z^d} = \hat{y} - y
$$

**Dense Layer Gradients**

$\frac{\partial \mathcal{L}}{\partial W^d} = (A^f)^T \cdot \frac{\partial \mathcal{L}}{\partial Z^d}$,
and the gradient with respect to biases is
$\frac{\partial \mathcal{L}}{\partial b^d} = \frac{\partial \mathcal{L}}{\partial Z^d}$.

Reshape the upstream gradient to the shape of $A^c$ for backpropagation through ReLU.

**ReLU Gradient**

$$
\frac{\partial \mathcal{L}}{\partial Z^c} = \frac{\partial \mathcal{L}}{\partial A^c} \cdot \mathbf{1}(Z^c > 0)
$$

**Convolution Filter Gradients**

For each filter $k$:

$$
\frac{\partial \mathcal{L}}{\partial W^c_{i,j,k}} = \sum_{p,q} \frac{\partial \mathcal{L}}{\partial Z^c_{p,q,k}} \cdot X_{p+i, q+j}
$$

$$
\frac{\partial \mathcal{L}}{\partial b^c_k} = \sum_{p,q} \frac{\partial \mathcal{L}}{\partial Z^c_{p,q,k}}
$$

---

### 4. Updating Parameters (SGD)

With learning rate $\eta$:

$$
W \leftarrow W - \eta \cdot \frac{\partial \mathcal{L}}{\partial W}
$$

$$
b \leftarrow b - \eta \cdot \frac{\partial \mathcal{L}}{\partial b}
$$

Repeat this process for each sample (stochastic gradient descent) and for multiple epochs.

---

### 5. Example Walkthrough

Suppose $X$ is a grayscale image:

$$
X = \begin{bmatrix}
1 & 2 & 3 \\
4 & 5 & 6 \\
7 & 8 & 9
\end{bmatrix}
$$

And the kernel is:

$$
K = \begin{bmatrix}
1 & 0 \\
0 & -1
\end{bmatrix}
$$

Perform convolution at the top-left:

$$
(1 \cdot 1 + 2 \cdot 0 + 4 \cdot 0 + 5 \cdot (-1)) = 1 - 5 = -4
$$

After ReLU: max(0, -4) = 0  
Flatten the result -> Dense layer -> Softmax output -> Compute loss

Backpropagate the error to adjust weights, and repeat to learn better filters and classifications over time.


### meta.json

```json
{
  "id": "130",
  "title": "Implement a Simple CNN Training Function with Backpropagation",
  "difficulty": "hard",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "moe"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def train_simple_cnn_with_backprop(
    X, y, epochs, learning_rate, kernel_size=3, num_filters=1
):
    '''
    Trains a simple CNN with one convolutional layer, ReLU activation, flattening, and a dense layer with softmax output using backpropagation.

    Assumes X has shape (n_samples, height, width) for grayscale images and y is one-hot encoded with shape (n_samples, num_classes).

    Parameters:
    X : np.ndarray, input data
    y : np.ndarray, one-hot encoded labels
    epochs : int, number of training epochs
    learning_rate : float, learning rate for weight updates
    kernel_size : int, size of the square convolutional kernel
    num_filters : int, number of filters in the convolutional layer

    Returns:
    W_conv, b_conv, W_dense, b_dense : Trained weights and biases for the convolutional and dense layers
    '''
    n_samples, height, width = X.shape
    num_classes = y.shape[1]

    # Initialize weights and biases
    W_conv = np.random.randn(kernel_size, kernel_size, num_filters) * 0.01
    b_conv = np.zeros(num_filters)
    output_height = height - kernel_size + 1
    output_width = width - kernel_size + 1
    flattened_size = output_height * output_width * num_filters
    W_dense = np.random.randn(flattened_size, num_classes) * 0.01
    b_dense = np.zeros(num_classes)

    for epoch in range(epochs):
        for i in range(n_samples):  # Stochastic Gradient Descent with batch size 1
            # Forward pass
            # Convolutional layer
            Z_conv = np.zeros((output_height, output_width, num_filters))
            for k in range(num_filters):
                for p in range(output_height):
                    for q in range(output_width):
                        Z_conv[p, q, k] = (
                            np.sum(
                                X[i, p : p + kernel_size, q : q + kernel_size]
                                * W_conv[:, :, k]
                            )
                            + b_conv[k]
                        )
            A_conv = np.maximum(Z_conv, 0)  # ReLU activation
            A_flat = A_conv.flatten()  # Flatten the output

            # Dense layer
            Z_dense = np.dot(A_flat, W_dense) + b_dense
            exp_Z_dense = np.exp(
                Z_dense - np.max(Z_dense)
            )  # Numerical stability for softmax
            A_dense = exp_Z_dense / np.sum(exp_Z_dense)

            # Backpropagation
            # Loss gradient for cross-entropy with softmax
            dZ_dense = A_dense - y[i]

            # Dense layer gradients
            dW_dense = np.outer(A_flat, dZ_dense)
            db_dense = dZ_dense
            dA_flat = np.dot(dZ_dense, W_dense.T)

            # Reshape and backprop through ReLU
            dA_conv = dA_flat.reshape(A_conv.shape)
            dZ_conv = dA_conv * (A_conv > 0).astype(float)

            # Convolutional layer gradients
            dW_conv = np.zeros_like(W_conv)
            db_conv = np.zeros(num_filters)
            for k in range(num_filters):
                db_conv[k] = np.sum(dZ_conv[:, :, k])
                for ii in range(kernel_size):
                    for jj in range(kernel_size):
                        dW_conv[ii, jj, k] = np.sum(
                            dZ_conv[:, :, k]
                            * X[i, ii : ii + output_height, jj : jj + output_width]
                        )

            # Update weights and biases
            W_conv -= learning_rate * dW_conv
            b_conv -= learning_rate * db_conv
            W_dense -= learning_rate * dW_dense
            b_dense -= learning_rate * db_dense

    return W_conv, b_conv, W_dense, b_dense
```




### starter_code.py

```python
def train_simple_cnn_with_backprop(
    X, y, epochs, learning_rate, kernel_size=3, num_filters=1
):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np; np.random.seed(42); X = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]); y = np.array([[1, 0]]); print(train_simple_cnn_with_backprop(X, y, 1, 0.01, 3, 1))",
    "expected_output": "(array([[[ 0.00501739],        [-0.00128214],        [ 0.00662764]],       [[ 0.01543131],        [-0.00209028],        [-0.00203986]],       [[ 0.01614389],        [ 0.00807636],        [-0.00424248]]]), array([5.02517066e-05]), array([[ 0.00635715, -0.00556573]]), array([ 0.00499531, -0.00499531]))"
  },
  {
    "test": "import numpy as np; np.random.seed(42); X = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[9, 8, 7], [6, 5, 4], [3, 2, 1]]]); y = np.array([[0, 1], [1, 0]]); print(train_simple_cnn_with_backprop(X, y, 2, 0.01, 3, 1))",
    "expected_output": "(array([[[ 0.00561561],        [-0.00091884],        [ 0.00675603]],       [[ 0.01532478],        [-0.00243171],        [-0.00261621]],       [[ 0.01533262],        [ 0.00703018],        [-0.00552357]]]), array([-1.80360153e-05]), array([[ 0.00561137, -0.00481995]]), array([ 3.23124658e-05, -3.23124658e-05]))"
  },
  {
    "test": "import numpy as np; np.random.seed(42); X = np.array([[[2, 3, 4], [5, 6, 7], [8, 9, 10]]]); y = np.array([[0.5, 0.5]]); print(train_simple_cnn_with_backprop(X, y, 1, 0.005, 3, 1))",
    "expected_output": "(array([[[ 0.00496708],        [-0.00138273],        [ 0.00647677]],       [[ 0.01523016],        [-0.00234171],        [-0.00234157]],       [[ 0.0157919 ],        [ 0.00767409],        [-0.00469503]]]), array([-2.85717013e-08]), array([[ 0.00542496, -0.00463354]]), array([-2.84019221e-06,  2.84019221e-06]))"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/130_implement-a-simple-cnn-training-function-with-back/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/130_implement-a-simple-cnn-training-function-with-back/description.md)。Deep-ML：Educational Use Only License。
