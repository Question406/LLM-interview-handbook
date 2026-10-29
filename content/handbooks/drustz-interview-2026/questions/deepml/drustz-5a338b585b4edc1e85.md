---
id: drustz-5a338b585b4edc1e85
section: deepml
order: 66
level: A
title: ExponentialLR Learning Rate Scheduler
quick: Deep-ML 练习 · ExponentialLR Learning Rate Scheduler
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/154_exponentialLR/description.md
    type: primary
---
### description.md

## Problem

Write a Python class ExponentialLRScheduler to implement a learning rate scheduler based on the ExponentialLR strategy. Your class should have an __init__ method to initialize with an initial_lr (float) and gamma (float) parameter. It should also have a get_lr(self, epoch) method that returns the current learning rate for a given epoch (int). The learning rate should be decreased by gamma every epoch. The returned learning rate should be rounded to 4 decimal places. Only use standard Python.

### example.json

```json
{
  "input": "scheduler = ExponentialLRScheduler(initial_lr=0.1, gamma=0.9)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=1):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=2):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=3):.4f}\")",
  "output": "0.1000\n0.0900\n0.0810\n0.0729",
  "reasoning": "The initial learning rate is 0.1. At epoch 1, it decays by 0.9 to 0.09. At epoch 2, it decays again to 0.081, and so on, decaying by gamma every single epoch. All results are rounded to 4 decimal places."
}
```




### learn.md

# **Learning Rate Schedulers: ExponentialLR**

## **1. Definition**
A **learning rate scheduler** is a component used in machine learning, especially in neural network training, to adjust the learning rate during the training process. The **learning rate** is a hyperparameter that determines the step size at each iteration while moving towards a minimum of a loss function.

**ExponentialLR (Exponential Learning Rate)** is a common type of learning rate scheduler that decays the learning rate by a fixed multiplicative factor γ (gamma) at *every* epoch. This results in an exponential decrease of the learning rate over time. It's often used when a rapid and continuous reduction of the learning rate is desired.

## **2. Why Use Learning Rate Schedulers?**
* **Faster Convergence:** A higher initial learning rate can help quickly move through the loss landscape.
* **Improved Performance:** A smaller learning rate towards the end of training allows for finer adjustments and helps in converging to a better local minimum, avoiding oscillations around the minimum.
* **Stability:** Reducing the learning rate prevents large updates that could lead to divergence or instability.

## **3. ExponentialLR Mechanism**
The learning rate is reduced by a factor γ (gamma) every epoch.

The formula for the learning rate at a given epoch e is:

$$LR_e = LR_{\text{initial}} \times \gamma^e$$

Where:
* $LR_e$: The learning rate at epoch e.
* $LR_{\text{initial}}$: The initial learning rate.
* γ (gamma): The multiplicative factor by which the learning rate is reduced per epoch (usually between 0 and 1, e.g., 0.9, 0.99).
* e: The current epoch number (0-indexed).

**Example:**
If initial learning rate = 0.1, and γ = 0.9:
* Epoch 0: $LR_0 = 0.1 \times 0.9^0 = 0.1 \times 1 = 0.1$
* Epoch 1: $LR_1 = 0.1 \times 0.9^1 = 0.1 \times 0.9 = 0.09$
* Epoch 2: $LR_2 = 0.1 \times 0.9^2 = 0.1 \times 0.81 = 0.081$
* Epoch 3: $LR_3 = 0.1 \times 0.9^3 = 0.1 \times 0.729 = 0.0729$

## **4. Applications of Learning Rate Schedulers**
Learning rate schedulers, including ExponentialLR, are widely used in training various machine learning models, especially deep neural networks, across diverse applications such as:
* **Image Classification:** Training Convolutional Neural Networks (CNNs) for tasks like object recognition.
* **Natural Language Processing (NLP):** Training Recurrent Neural Networks (RNNs) and Transformers for tasks like machine translation, text generation, and sentiment analysis.
* **Speech Recognition:** Training models for converting spoken language to text.
* **Reinforcement Learning:** Optimizing policies in reinforcement learning agents.
* **Any optimization problem** where gradient descent or its variants are used.

### meta.json

```json
{
  "id": "154",
  "title": "ExponentialLR Learning Rate Scheduler",
  "difficulty": "easy",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/komaksym",
      "name": "komaksym"
    }
  ]
}
```




### solution.py

```python
class ExponentialLRScheduler:
    def __init__(self, initial_lr, gamma):
        """
        Initializes the ExponentialLR scheduler.

        Args:
            initial_lr (float): The initial learning rate.
            gamma (float): The multiplicative factor of learning rate decay per epoch.
                           (e.g., 0.9 for reducing LR by 10% each epoch).
        """
        self.initial_lr = initial_lr
        self.gamma = gamma

    def get_lr(self, epoch):
        """
        Calculates and returns the current learning rate for a given epoch,
        rounded to 4 decimal places.

        Args:
            epoch (int): The current epoch number (0-indexed).

        Returns:
            float: The calculated learning rate for the current epoch, rounded to 4 decimal places.
        """
        # Apply the decay factor 'gamma' raised to the power of the current 'epoch'
        # to the initial learning rate.
        current_lr = self.initial_lr * (self.gamma**epoch)

        # Round the learning rate to 4 decimal places
        return round(current_lr, 4)
```




### starter_code.py

```python
class ExponentialLRScheduler:
    def __init__(self, initial_lr, gamma):
        # Initialize initial_lr and gamma
        pass

    def get_lr(self, epoch):
        # Calculate and return the learning rate for the given epoch
        pass
```




### tests.json

```json
[
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=0.1, gamma=0.9)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\")",
    "expected_output": "0.1000"
  },
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=0.1, gamma=0.9)\nprint(f\"{scheduler.get_lr(epoch=1):.4f}\")",
    "expected_output": "0.0900"
  },
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=0.1, gamma=0.9)\nprint(f\"{scheduler.get_lr(epoch=2):.4f}\")",
    "expected_output": "0.0810"
  },
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=0.1, gamma=0.9)\nprint(f\"{scheduler.get_lr(epoch=3):.4f}\")",
    "expected_output": "0.0729"
  },
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=1.0, gamma=0.5)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\\n{scheduler.get_lr(epoch=1):.4f}\\n{scheduler.get_lr(epoch=2):.4f}\\n{scheduler.get_lr(epoch=3):.4f}\")",
    "expected_output": "1.0000\n0.5000\n0.2500\n0.1250"
  },
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=0.005, gamma=0.99)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\\n{scheduler.get_lr(epoch=10):.4f}\\n{scheduler.get_lr(epoch=20):.4f}\")",
    "expected_output": "0.0050\n0.0045\n0.0041"
  },
  {
    "test": "scheduler = ExponentialLRScheduler(initial_lr=0.001, gamma=1.0)\nprint(f\"{scheduler.get_lr(epoch=5):.4f}\\n{scheduler.get_lr(epoch=10):.4f}\")",
    "expected_output": "0.0010\n0.0010"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/154_exponentialLR/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/154_exponentialLR/description.md)。Deep-ML：Educational Use Only License。
