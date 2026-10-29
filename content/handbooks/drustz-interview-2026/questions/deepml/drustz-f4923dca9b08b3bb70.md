---
id: drustz-f4923dca9b08b3bb70
section: deepml
order: 127
level: A
title: Implementing a Custom Dense Layer in Python
quick: Deep-ML 练习 · Implementing a Custom Dense Layer in Python
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/40_implementing-a-custom-dense-layer-in-python/description.md
    type: primary
---
### description.md

## Implementing a Custom Dense Layer in Python

You are provided with a base `Layer` class that defines the structure of a neural network layer. Your task is to implement a subclass called `Dense`, which represents a fully connected neural network layer. The `Dense` class should extend the `Layer` class and implement the following methods:

1. **Initialization (`__init__`)**:
   - Define the layer with a specified number of neurons (`n_units`) and an optional input shape (`input_shape`).
   - Set up placeholders for the layer's weights (`W`), biases (`w0`), and optimizers.

2. **Weight Initialization (`initialize`)**:
   - Initialize the weights `W` using a uniform distribution with a limit of `1 / sqrt(input_shape[0])`, and bias `w0` should be set to zero.
   - Initialize optimizers for `W` and `w0`.

3. **Parameter Count (`parameters`)**:
   - Return the total number of trainable parameters in the layer, which includes the parameters in `W` and `w0`.

4. **Forward Pass (`forward_pass`)**:
   - Compute the output of the layer by performing a dot product between the input `X` and the weight matrix `W`, and then adding the bias `w0`.

5. **Backward Pass (`backward_pass`)**:
   - Calculate and return the gradient with respect to the input.
   - If the layer is trainable, update the weights and biases using the optimizer's update rule.

6. **Output Shape (`output_shape`)**:
   - Return the shape of the output produced by the forward pass, which should be `(self.n_units,)`.

**Objective**:  
Extend the `Layer` class by implementing the `Dense` class to ensure it functions correctly within a neural network framework.


### example.json

```json
{
  "input": "# Initialize a Dense layer with 3 neurons and input shape (2,)\ndense_layer = Dense(n_units=3, input_shape=(2,))\n\n# Define a mock optimizer with a simple update rule\nclass MockOptimizer:\n    def update(self, weights, grad):\n        return weights - 0.01 * grad\n\noptimizer = MockOptimizer()\n\n# Initialize the Dense layer with the mock optimizer\ndense_layer.initialize(optimizer)\n\n# Perform a forward pass with sample input data\nX = np.array([[1, 2]])\noutput = dense_layer.forward_pass(X)\nprint(\"Forward pass output:\", output)\n\n# Perform a backward pass with sample gradient\naccum_grad = np.array([[0.1, 0.2, 0.3]])\nback_output = dense_layer.backward_pass(accum_grad)\nprint(\"Backward pass output:\", back_output)",
  "output": "Forward pass output: [[-0.00655782  0.01429615  0.00905812]]\nBackward pass output: [[ 0.00129588  0.00953634]]",
  "reasoning": "The code initializes a Dense layer with 3 neurons and input shape (2,). It then performs a forward pass with sample input data and a backward pass with sample gradients. The output demonstrates the forward and backward pass results."
}
```




### learn.md

## Understanding the Dense Layer

The Dense layer, also known as a fully connected layer, is a fundamental building block in neural networks. It connects each input neuron to each output neuron, hence the term "fully connected."

### 1. Weight Initialization
In the `initialize` method, weights are typically initialized using a uniform distribution within a certain range. For a Dense layer, a common practice is to set this range as:
$$
\text{limit} = \frac{1}{\sqrt{\text{input\_shape}}}
$$
This initialization helps in maintaining a balance in the distribution of weights, preventing issues like vanishing or exploding gradients during training.

### 2. Forward Pass
During the forward pass, the input data \( X \) is multiplied by the weight matrix \( W \) and added to the bias \( w_0 \) to produce the output:
$$
\text{output} = X \cdot W + w_0
$$

### 3. Backward Pass
The backward pass computes the gradients of the loss function with respect to the input data, weights, and biases. If the layer is trainable, it updates the weights and biases using the optimizer's update rule:
$$
W = W - \eta \cdot \text{grad}_W
$$
$$
w_0 = w_0 - \eta \cdot \text{grad}_{w_0}
$$
where \( \eta \) is the learning rate and \( \text{grad}_W \) and \( \text{grad}_{w_0} \) are the gradients of the weights and biases, respectively.

### 4. Output Shape
The shape of the output from a Dense layer is determined by the number of neurons in the layer. If a layer has `n_units` neurons, the output shape will be \( (n\_units,) \).

### Resources
- [CS231n: Fully Connected Layer](https://cs231n.github.io/neural-networks-2/#fc)

    


### meta.json

```json
{
  "id": "40",
  "title": "Implementing a Custom Dense Layer in Python",
  "difficulty": "hard",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabor"
    }
  ]
}
```




### solution.py

```python
class Dense(Layer):
    def __init__(self, n_units, input_shape=None):
        self.layer_input = None
        self.input_shape = input_shape
        self.n_units = n_units
        self.trainable = True
        self.W = None
        self.w0 = None

    def initialize(self, optimizer):
        limit = 1 / math.sqrt(self.input_shape[0])
        self.W = np.random.uniform(-limit, limit, (self.input_shape[0], self.n_units))
        self.w0 = np.zeros((1, self.n_units))
        self.W_opt = copy.copy(optimizer)
        self.w0_opt = copy.copy(optimizer)

    def parameters(self):
        return np.prod(self.W.shape) + np.prod(self.w0.shape)

    def forward_pass(self, X, training=True):
        self.layer_input = X
        return X.dot(self.W) + self.w0

    def backward_pass(self, accum_grad):
        W = self.W
        if self.trainable:
            grad_w = self.layer_input.T.dot(accum_grad)
            grad_w0 = np.sum(accum_grad, axis=0, keepdims=True)
            self.W = self.W_opt.update(self.W, grad_w)
            self.w0 = self.w0_opt.update(self.w0, grad_w0)
        accum_grad = accum_grad.dot(W.T)
        return accum_grad

    def output_shape(self):
        return (self.n_units,)
```




### starter_code.py

```text

import numpy as np
import copy
import math

# DO NOT CHANGE SEED
np.random.seed(42)

# DO NOT CHANGE LAYER CLASS
class Layer(object):

	def set_input_shape(self, shape):
    
		self.input_shape = shape

	def layer_name(self):
		return self.__class__.__name__

	def parameters(self):
		return 0

	def forward_pass(self, X, training):
		raise NotImplementedError()

	def backward_pass(self, accum_grad):
		raise NotImplementedError()

	def output_shape(self):
		raise NotImplementedError()

# Your task is to implement the Dense class based on the above structure
class Dense(Layer):
	def __init__(self, n_units, input_shape=None):
		self.layer_input = None
		self.input_shape = input_shape
		self.n_units = n_units
		self.trainable = True
		self.W = None
		self.w0 = None

	def forward_pass():


	def backward_pass(self, accum_grad):


	def number_of_parameters():
```




### tests.json

```json
[
  {
    "test": "\ndense_layer = Dense(n_units=3, input_shape=(2,))\n\nclass MockOptimizer:\n    def update(self, weights, grad):\n        return weights - 0.01 * grad\n\noptimizer = MockOptimizer()\ndense_layer.initialize(optimizer)\n\nX = np.array([[1, 2]])\noutput = dense_layer.forward_pass(X)\n\naccum_grad = np.array([[0.1, 0.2, 0.3]])\nback_output = dense_layer.backward_pass(accum_grad)\nprint(back_output)",
    "expected_output": "[[ 0.20816524, -0.22928937]]"
  }
]
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/40_implementing-a-custom-dense-layer-in-python/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/40_implementing-a-custom-dense-layer-in-python/description.md)。Deep-ML：Educational Use Only License。
