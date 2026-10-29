---
id: drustz-8edf52400fdfb78a33
section: deepml
order: 153
level: A
title: Poisson Distribution Probability Calculator
quick: Deep-ML 练习 · Poisson Distribution Probability Calculator
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/81_poisson-distribution-probability-calculator/description.md
    type: primary
---
### description.md

Write a Python function to calculate the probability of observing exactly k events in a fixed interval using the Poisson distribution formula. The function should take k (number of events) and lam (mean rate of occurrences) as inputs and return the probability rounded to 5 decimal places.


### example.json

```json
{
  "input": "k = 3, lam = 5",
  "output": "0.14037",
  "reasoning": "The function calculates the probability for a given number of events occurring in a fixed interval, based on the mean rate of occurrences."
}
```




### learn.md

## Understanding Poisson Distribution

The Poisson distribution is a discrete probability distribution that expresses the probability of a given number of events occurring in a fixed interval of time or space, provided these events occur with a known constant mean rate and independently of the time since the last event.

### Mathematical Definition

The probability of observing \( k \) events in a given interval is defined as:

$$
P(k; \lambda) = \frac{\lambda^k e^{-\lambda}}{k!}
$$

- **\( k \)**: Number of events (non-negative integer)
- **\( \lambda \)**: The mean number of events in the given interval (rate parameter)
- **\( e \)**: Euler's number, approximately 2.718

### Key Properties

- **Mean**: \( \lambda \)
- **Variance**: \( \lambda \)
- The Poisson distribution is used for modeling rare or random events.

### Example Calculation

Suppose the mean number of calls received in an hour (\( \lambda \)) is 5. Calculate the probability of receiving exactly 3 calls in an hour:

1. **Substitute into the formula**:
   $$
   P(3; 5) = \frac{5^3 e^{-5}}{3!}
   $$

2. **Calculate step-by-step**:
   $$
   P(3; 5) = \frac{125 \cdot e^{-5}}{6} \approx 0.14037
   $$

### Applications

The Poisson distribution is widely used in:

- Modeling the number of arrivals at a queue (e.g., calls at a call center)
- Counting occurrences over time (e.g., number of emails received per hour)
- Biology (e.g., distribution of mutations in a DNA strand)
- Traffic flow analysis (e.g., number of cars passing through an intersection)

This distribution is essential for understanding and predicting rare events in real-world scenarios.


### meta.json

```json
{
  "id": "81",
  "title": "Poisson Distribution Probability Calculator",
  "difficulty": "easy",
  "category": "Probability",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/BhardwajArjit",
      "name": "Arjit Bhardwaj"
    }
  ]
}
```




### solution.py

```python
import math


def poisson_probability(k, lam):
    """
    Calculate the probability of observing exactly k events in a fixed interval,
    given the mean rate of events lam, using the Poisson distribution formula.
    :param k: Number of events (non-negative integer)
    :param lam: The average rate (mean) of occurrences in a fixed interval
    :return: Probability of k events occurring
    """
    # Calculate the Poisson probability using the formula
    probability = (lam**k) * math.exp(-lam) / math.factorial(k)
    # Return the probability, rounded to five decimal places
    return round(probability, 5)
```




### starter_code.py

```python
import math


def poisson_probability(k, lam):
    """
    Calculate the probability of observing exactly k events in a fixed interval,
    given the mean rate of events lam, using the Poisson distribution formula.
    :param k: Number of events (non-negative integer)
    :param lam: The average rate (mean) of occurrences in a fixed interval
    """
    # Your code here
    pass
    return round(val, 5)
```




### tests.json

```json
[
  {
    "test": "print(poisson_probability(3, 5))",
    "expected_output": "0.14037"
  },
  {
    "test": "print(poisson_probability(0, 5))",
    "expected_output": "0.00674"
  },
  {
    "test": "print(poisson_probability(2, 10))",
    "expected_output": "0.00227"
  },
  {
    "test": "print(poisson_probability(1, 1))",
    "expected_output": "0.36788"
  },
  {
    "test": "print(poisson_probability(20, 20))",
    "expected_output": "0.08884"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/81_poisson-distribution-probability-calculator/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/81_poisson-distribution-probability-calculator/description.md)。Deep-ML：Educational Use Only License。
