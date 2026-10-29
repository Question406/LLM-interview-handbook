---
id: drustz-7d0eed9f592dd42b48
section: deepml
order: 10
level: A
title: Binomial Distribution Probability
quick: Deep-ML 练习 · Binomial Distribution Probability
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/79_binomial-distribution-probability/description.md
    type: primary
---
### description.md

Write a Python function to calculate the probability of achieving exactly k successes in n independent Bernoulli trials, each with probability p of success, using the Binomial distribution formula.


### example.json

```json
{
  "input": "n = 6, k = 2, p = 0.5",
  "output": "0.23438",
  "reasoning": "The function calculates the Binomial probability, the intermediate steps include calculating the binomial coefficient, raising p and (1-p) to the appropriate powers, and multiplying the results."
}
```




### learn.md

## Understanding the Binomial Distribution

The Binomial distribution is a discrete probability distribution that models the number of successes in a fixed number of independent Bernoulli trials, each with the same probability of success.

### Mathematical Formulation

The probability of achieving exactly $k$ successes in $n$ trials is given by the formula:

$$
P(X = k) = \binom{n}{k} \cdot p^k \cdot (1-p)^{n-k}
$$

- **$n$**: Total number of trials  
- **$k$**: Number of successes  
- **$p$**: Probability of success on each trial  
- $\binom{n}{k}$: The number of ways to choose $k$ successes from $n$ trials, calculated as:

$$
\binom{n}{k} = \frac{n!}{k!(n-k)!}
$$

### Implementation Steps

1. Calculate $\binom{n}{k}$ using factorials.  
2. Raise $p$ to the power of $k$ and $(1-p)$ to the power of $(n-k)$.  
3. Multiply these results to get the probability.

### Example Calculation

Given:

- $n = 5$  
- $k = 2$  
- $p = 0.4$  

Step-by-step:

1. Calculate $\binom{n}{k}$:

$$
\binom{5}{2} = \frac{5!}{2!(5-2)!} = \frac{5 \cdot 4}{2 \cdot 1} = 10
$$

2. Calculate $p^k \cdot (1-p)^{n-k}$:

$$
0.4^2 \cdot (1-0.4)^3 = 0.16 \cdot 0.216 = 0.03456
$$

3. Multiply results:

$$
P(X = 2) = 10 \cdot 0.03456 = 0.3456
$$

The probability of exactly 2 successes is $0.3456$.

### Applications

The Binomial distribution is widely used in:

- Quality control and defect analysis  
- Survey analysis  
- Medical trials  
- Modeling success/failure experiments  

It provides insights into the likelihood of various outcomes in scenarios with two possible results (e.g., success or failure).


### meta.json

```json
{
  "id": "79",
  "title": "Binomial Distribution Probability",
  "difficulty": "medium",
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


def binomial_probability(n, k, p):
    """
    Calculate the probability of achieving exactly k successes in n independent Bernoulli trials,
    each with probability p of success, using the Binomial distribution formula.
    :param n: Total number of trials
    :param k: Number of successes
    :param p: Probability of success on each trial
    :return: Probability of k successes in n trials
    """
    # Calculate binomial coefficient (n choose k)
    binomial_coeff = math.comb(n, k)
    # Calculate the probability using the binomial formula
    probability = binomial_coeff * (p**k) * ((1 - p) ** (n - k))
    # Return the probability, rounded to five decimal places
    return round(probability, 5)
```




### starter_code.py

```python
import math


def binomial_probability(n, k, p):
    """
    Calculate the probability of achieving exactly k successes in n independent Bernoulli trials,
    each with probability p of success, using the Binomial distribution formula.
    """
    # Your code here
    return round(probability, 5)
```




### tests.json

```json
[
  {
    "test": "print(binomial_probability(6, 2, 0.5))",
    "expected_output": "0.23438"
  },
  {
    "test": "print(binomial_probability(6, 4, 0.7))",
    "expected_output": "0.32414"
  },
  {
    "test": "print(binomial_probability(3, 3, 0.9))",
    "expected_output": "0.729"
  },
  {
    "test": "print(binomial_probability(5, 0, 0.3))",
    "expected_output": "0.16807"
  },
  {
    "test": "print(binomial_probability(7, 2, 0.1))",
    "expected_output": "0.124"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/79_binomial-distribution-probability/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/79_binomial-distribution-probability/description.md)。Deep-ML：Educational Use Only License。
