---
id: drustz-60eb39af736bb9ed39
section: deepml
order: 37
level: A
title: CosineAnnealingLR Learning Rate Scheduler
quick: Deep-ML 练习 · CosineAnnealingLR Learning Rate Scheduler
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/155_CossineAnnealingLR/description.md
    type: primary
---
### description.md

## Problem

Write a Python class CosineAnnealingLRScheduler to implement a learning rate scheduler based on the Cosine Annealing LR strategy. Your class should have an __init__ method to initialize with an initial_lr (float),  $T_{max}$  (int, the maximum number of iterations/epochs), and min_lr (float, the minimum learning rate) parameters. It should also have a **get_lr(self, epoch)** method that returns the current learning rate for a given epoch (int). The learning rate should follow a cosine annealing schedule. The returned learning rate should be rounded to 4 decimal places. Only use standard Python and the math module for trigonometric functions.

### example.json

```json
{
  "input": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.1, T_max=10, min_lr=0.001)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=2):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=5):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=7):.4f}\")\nprint(f\"{scheduler.get_lr(epoch=10):.4f}\")",
  "output": "0.1000\n0.0905\n0.0505\n0.0214\n0.0010",
  "reasoning": "The learning rate starts at initial_lr (0.1), follows a cosine curve, reaches min_lr (0.001) at T_max (epoch 10), and then cycles back up. Each value is rounded to 4 decimal places."
}
```




### learn.md

# **Learning Rate Schedulers: CosineAnnealingLR**

## **1. Definition**
A **learning rate scheduler** is a technique used in machine learning to adjust the learning rate during the training of a model. The **learning rate** dictates the step size taken in the direction of the negative gradient of the loss function.

**CosineAnnealingLR (Cosine Annealing Learning Rate)** is a scheduler that aims to decrease the learning rate from a maximum value to a minimum value following the shape of a cosine curve. This approach helps in achieving faster convergence while also allowing the model to explore flatter regions of the loss landscape towards the end of training. It is particularly effective for deep neural networks.

## **2. Why Use Learning Rate Schedulers?**
* **Faster Convergence:** A higher initial learning rate allows for quicker movement through the loss landscape.
* **Improved Performance:** A smaller learning rate towards the end of training enables finer adjustments, helping the model converge to a better local minimum and preventing oscillations.
* **Avoiding Local Minima:** The cyclical nature (or a part of it, as often seen in restarts) of cosine annealing can help the optimizer escape shallow local minima.
* **Stability:** Gradual reduction in learning rate promotes training stability.

## **3. CosineAnnealingLR Mechanism**
The learning rate is scheduled according to a cosine function. Over a cycle of $T_{\text{max}}$ epochs, the learning rate decreases from an initial learning rate (often considered the maximum $LR_{\text{max}}$) to a minimum learning rate ($LR_{\text{min}}$).

The formula for the learning rate at a given epoch e is:

$$LR_e = LR_{\text{min}} + 0.5 \times (LR_{\text{initial}} - LR_{\text{min}}) \times \left(1 + \cos\left(\frac{e}{T_{\text{max}}} \times \pi\right)\right)$$

Where:
* $LR_e$: The learning rate at epoch e.
* $LR_{\text{initial}}$: The initial (maximum) learning rate.
* $LR_{\text{min}}$: The minimum learning rate that the schedule will reach.
* $T_{\text{max}}$: The maximum number of epochs in the cosine annealing cycle. The learning rate will reach $LR_{\text{min}}$ at epoch $T_{\text{max}}$.
* e: The current epoch number (0-indexed), clamped between 0 and $T_{\text{max}}$.
* π: The mathematical constant pi (approximately 3.14159).
* $\cos(\cdot)$: The cosine function.

**Example:**
If $LR_{\text{initial}} = 0.1$, $T_{\text{max}} = 10$, and $LR_{\text{min}} = 0.001$:

* **Epoch 0:** 
  $LR_0 = 0.001 + 0.5 \times (0.1 - 0.001) \times (1 + \cos(0)) = 0.001 + 0.0495 \times 2 = 0.1$

* **Epoch 5 (mid-point):** 
  $LR_5 = 0.001 + 0.5 \times (0.1 - 0.001) \times (1 + \cos(\pi/2)) = 0.001 + 0.0495 \times 1 = 0.0505$

* **Epoch 10 (end of cycle):** 
  $LR_{10} = 0.001 + 0.5 \times (0.1 - 0.001) \times (1 + \cos(\pi)) = 0.001 + 0.0495 \times 0 = 0.001$

## **4. Applications of Learning Rate Schedulers**
Learning rate schedulers, including CosineAnnealingLR, are widely used in training various machine learning models, especially deep neural networks, across diverse applications such as:
* **Image Classification:** Training Convolutional Neural Networks (CNNs) for tasks like object recognition.
* **Natural Language Processing (NLP):** Training Recurrent Neural Networks (RNNs) and Transformers for tasks like machine translation, text generation, and sentiment analysis.
* **Speech Recognition:** Training models for converting spoken language to text.
* **Reinforcement Learning:** Optimizing policies in reinforcement learning agents.
* **Any optimization problem** where gradient descent or its variants are used.

### meta.json

```json
{
  "id": "155",
  "title": "CosineAnnealingLR Learning Rate Scheduler",
  "difficulty": "medium",
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
import math


class CosineAnnealingLRScheduler:
    def __init__(self, initial_lr, T_max, min_lr):
        """
        Initializes the CosineAnnealingLR scheduler.

        Args:
            initial_lr (float): The initial (maximum) learning rate.
            T_max (int): The maximum number of epochs in the cosine annealing cycle.
                         The learning rate will reach min_lr at this epoch.
            min_lr (float): The minimum learning rate.
        """
        self.initial_lr = initial_lr
        self.T_max = T_max
        self.min_lr = min_lr

    def get_lr(self, epoch):
        """
        Calculates and returns the current learning rate for a given epoch,
        following a cosine annealing schedule and rounded to 4 decimal places.

        Args:
            epoch (int): The current epoch number (0-indexed).

        Returns:
            float: The calculated learning rate for the current epoch, rounded to 4 decimal places.
        """
        # Ensure epoch does not exceed T_max for the calculation cycle,
        # as the cosine formula is typically defined for e from 0 to T_max.
        # Although in practice, schedulers might restart or hold LR after T_max.
        # For this problem, we'll clamp it to T_max if it goes over.
        current_epoch = min(epoch, self.T_max)

        # Calculate the learning rate using the Cosine Annealing formula
        # LR_e = LR_min + 0.5 * (LR_initial - LR_min) * (1 + cos(e / T_max * pi))
        lr = self.min_lr + 0.5 * (self.initial_lr - self.min_lr) * (
            1 + math.cos(current_epoch / self.T_max * math.pi)
        )

        # Round the learning rate to 4 decimal places
        return round(lr, 4)
```




### starter_code.py

```python
import math


class CosineAnnealingLRScheduler:
    def __init__(self, initial_lr, T_max, min_lr):
        # Initialize initial_lr, T_max, and min_lr
        pass

    def get_lr(self, epoch):
        # Calculate and return the learning rate for the given epoch, rounded to 4 decimal places
        pass
```




### tests.json

```json
[
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.1, T_max=10, min_lr=0.001)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\")",
    "expected_output": "0.1000"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.1, T_max=10, min_lr=0.001)\nprint(f\"{scheduler.get_lr(epoch=2):.4f}\")",
    "expected_output": "0.0905"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.1, T_max=10, min_lr=0.001)\nprint(f\"{scheduler.get_lr(epoch=5):.4f}\")",
    "expected_output": "0.0505"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.1, T_max=10, min_lr=0.001)\nprint(f\"{scheduler.get_lr(epoch=7):.4f}\")",
    "expected_output": "0.0214"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.1, T_max=10, min_lr=0.001)\nprint(f\"{scheduler.get_lr(epoch=10):.4f}\")",
    "expected_output": "0.0010"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.05, T_max=50, min_lr=0.0)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\\n{scheduler.get_lr(epoch=25):.4f}\\n{scheduler.get_lr(epoch=50):.4f}\")",
    "expected_output": "0.0500\n0.0250\n0.0000"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.001, T_max=1, min_lr=0.0001)\nprint(f\"{scheduler.get_lr(epoch=0):.4f}\\n{scheduler.get_lr(epoch=1):.4f}\")",
    "expected_output": "0.0010\n0.0001"
  },
  {
    "test": "import math\nscheduler = CosineAnnealingLRScheduler(initial_lr=0.2, T_max=20, min_lr=0.01)\nprint(f\"{scheduler.get_lr(epoch=15):.4f}\")",
    "expected_output": "0.0378"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/155_CossineAnnealingLR/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/155_CossineAnnealingLR/description.md)。Deep-ML：Educational Use Only License。
