---
id: drustz-d8f8ed565a99d790e2
section: deepml
order: 147
level: A
title: Nesterov Accelerated Gradient Optimizer
quick: Deep-ML 练习 · Nesterov Accelerated Gradient Optimizer
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/150_nesterov-accelerated-gradient-optimizer/description.md
    type: primary
---
### description.md

Implement the Nesterov Accelerated Gradient (NAG) optimizer update step function. Your function should take the current parameter value, gradient function, and velocity as inputs, and return the updated parameter value and new velocity. The function should use the "look-ahead" approach where momentum is applied before computing the gradient, and should handle both scalar and array inputs.


### example.json

```json
{
  "input": "parameter = 1.0, grad_fn = lambda x: x, velocity = 0.1",
  "output": "(0.9009, 0.0991)",
  "reasoning": "The Nesterov Accelerated Gradient optimizer computes updated values for the parameter and velocity using a look-ahead approach. With input values parameter=1.0, grad_fn=lambda x: x, and velocity=0.1, the updated parameter becomes 0.9009 and the updated velocity becomes 0.0991."
}
```




### learn.md

# Implementing Nesterov Accelerated Gradient (NAG) Optimizer

## Introduction
Nesterov Accelerated Gradient (NAG) is an improvement over classical momentum optimization. While momentum helps accelerate gradient descent in the relevant direction, NAG takes this a step further by looking ahead in the direction of the momentum before computing the gradient. This "look-ahead" property helps NAG make more informed updates and often leads to better convergence.

## Learning Objectives
- Understand how Nesterov Accelerated Gradient optimization works
- Learn to implement NAG-based gradient updates
- Understand the advantages of NAG over classical momentum
- Gain practical experience with advanced gradient-based optimization

## Theory
Nesterov Accelerated Gradient uses a "look-ahead" approach where it first makes a momentum-based step and then computes the gradient at that position. The key equations are:

$\theta_{lookahead, t-1} = \theta_{t-1} - \gamma v_{t-1}$ (Look-ahead position)

$v_t = \gamma v_{t-1} + \eta \nabla_\theta J(\theta_{lookahead, t-1})$ (Velocity update)

$\theta_t = \theta_{t-1} - v_t$ (Parameter update)

Where:
- $v_t$ is the velocity at time t
- $\gamma$ is the momentum coefficient (typically 0.9)
- $\eta$ is the learning rate
- $\nabla_\theta J(\theta)$ is the gradient of the loss function

The key difference from classical momentum is that the gradient is evaluated at $\theta_{lookahead, t-1}$ instead of $\theta_{t-1}$

Read more at:

1. Nesterov, Y. (1983). A method for solving the convex programming problem with convergence rate O(1/ $k^{2}$ ). Doklady Akademii Nauk SSSR, 269(3), 543-547.
2. Ruder, S. (2017). An overview of gradient descent optimization algorithms. [arXiv:1609.04747](https://arxiv.org/pdf/1609.04747)


## Problem Statement
Implement the Nesterov Accelerated Gradient optimizer update step function. Your function should take the current parameter value, gradient function, and velocity as inputs, and return the updated parameter value and new velocity.

### Input Format
The function should accept:
- parameter: Current parameter value
- gradient function: A function that accepts parameters and returns gradient computed at that point
- velocity: Current velocity
- learning_rate: Learning rate (default=0.01)
- momentum: Momentum coefficient (default=0.9)

### Output Format
Return tuple: (updated_parameter, updated_velocity)

## Example
```python
# Example usage:
def grad_func(parameter):
    # Returns gradient
    pass


parameter = 1.0
velocity = 0.1

new_param, new_velocity = nag_optimizer(parameter, grad_func, velocity)
```



## Tips
- Initialize velocity as zero
- Use numpy for numerical operations
- Test with both scalar and array inputs
- Remember that the gradient should be computed at the look-ahead position

---


### meta.json

```json
{
  "id": "150",
  "title": "Nesterov Accelerated Gradient Optimizer",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/mavleo96",
      "name": "Vijayabharathi Murugan"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def nag_optimizer(parameter, grad_fn, velocity, learning_rate=0.01, momentum=0.9):
    """
    Update parameters using the Nesterov Accelerated Gradient optimizer.
    Uses a "look-ahead" approach to improve convergence by applying momentum before computing the gradient.

    Args:
        parameter: Current parameter value
        grad_fn: Function that computes the gradient at a given position
        velocity: Current velocity (momentum term)
        learning_rate: Learning rate (default=0.01)
        momentum: Momentum coefficient (default=0.9)

    Returns:
        tuple: (updated_parameter, updated_velocity)
    """
    assert 0 <= momentum < 1, "Momentum must be between 0 and 1"
    assert learning_rate > 0, "Learning rate must be positive"

    # Compute look-ahead position
    look_ahead = parameter - momentum * velocity

    # Compute gradient at look-ahead position
    grad = grad_fn(look_ahead)

    # Update velocity using momentum and gradient
    velocity = momentum * velocity + learning_rate * grad

    # Update parameters using the new velocity
    parameter = parameter - velocity

    return np.round(parameter, 5), np.round(velocity, 5)
```




### starter_code.py

```python
import numpy as np


def nag_optimizer(parameter, grad_fn, velocity, learning_rate=0.01, momentum=0.9):
    """
    Update parameters using the Nesterov Accelerated Gradient optimizer.
    Uses a "look-ahead" approach to improve convergence by applying momentum before computing the gradient.

    Args:
        parameter: Current parameter value
        grad_fn: Function that computes the gradient at a given position
        velocity: Current velocity (momentum term)
        learning_rate: Learning rate (default=0.01)
        momentum: Momentum coefficient (default=0.9)

    Returns:
        tuple: (updated_parameter, updated_velocity)
    """
    # Your code here
    return np.round(parameter, 5), np.round(velocity, 5)
```




### tests.json

```json
[
  {
    "test": "import numpy as np\ndef gradient_function(x):\n    if isinstance(x, np.ndarray):\n        n = len(x)\n        return x - np.arange(n)\n    else:\n        return x - 0\nprint(nag_optimizer(1., gradient_function, 0.5, 0.01, 0.9))",
    "expected_output": "(0.5445, 0.4555)"
  },
  {
    "test": "import numpy as np\ndef gradient_function(x):\n    if isinstance(x, np.ndarray):\n        n = len(x)\n        return x - np.arange(n)\n    else:\n        return x - 0\nprint(nag_optimizer(np.array([1.0, 2.0]), gradient_function, np.array([0.5, 1.0]), 0.01, 0.9))",
    "expected_output": "(array([0.5445, 1.099]), array([0.4555, 0.901]))"
  },
  {
    "test": "import numpy as np\ndef gradient_function(x):\n    if isinstance(x, np.ndarray):\n        n = len(x)\n        return x - np.arange(n)\n    else:\n        return x - 0\nprint(nag_optimizer(np.array([1.0, 2.0]), gradient_function, np.array([0.5, 1.0]), 0.01, 0.0))",
    "expected_output": "(array([0.99, 1.99]), array([0.01, 0.01]))"
  },
  {
    "test": "import numpy as np\ndef gradient_function(x):\n    if isinstance(x, np.ndarray):\n        n = len(x)\n        return x - np.arange(n)\n    else:\n        return x - 0\nprint(nag_optimizer(0.9, gradient_function, 1, 0.01, 0.9))",
    "expected_output": "(0.0, 0.9)"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/150_nesterov-accelerated-gradient-optimizer/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/150_nesterov-accelerated-gradient-optimizer/description.md)。Deep-ML：Educational Use Only License。
