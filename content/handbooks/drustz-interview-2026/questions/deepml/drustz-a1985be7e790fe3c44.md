---
id: drustz-a1985be7e790fe3c44
section: deepml
order: 65
level: A
title: Exponential Weighted Average of Rewards
quick: Deep-ML 练习 · Exponential Weighted Average of Rewards
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/161_exponential-weighted-average-of-rewards/description.md
    type: primary
---
### description.md

Given an initial value $Q_1$, a list of $k$ observed rewards $R_1, R_2, \ldots, R_k$, and a step size $\alpha$, implement a function to compute the exponentially weighted average as:

$$(1-\alpha)^k Q_1 + \sum_{i=1}^k \alpha (1-\alpha)^{k-i} R_i$$

This weighting gives more importance to recent rewards, while the influence of the initial estimate $Q_1$ decays over time. Do **not** use running/incremental updates; instead, compute directly from the formula. (This is called the *exponential recency-weighted average*.)


### example.json

```json
{
  "input": "Q1 = 2.0\nrewards = [5.0, 9.0]\nalpha = 0.3\nresult = exp_weighted_average(Q1, rewards, alpha)\nprint(round(result, 4))",
  "output": "5.003",
  "reasoning": "Here, k=2, so the result is: (1-0.3)^2*2.0 + 0.3*(1-0.3)^1*5.0 + 0.3*(1-0.3)^0*9.0 = 0.49*2.0 + 0.21*5.0 + 0.3*9.0 = 0.98 + 1.05 + 2.7 = 4.73 (actually, should be 0.49*2+0.3*0.7*5+0.3*9 = 0.98+1.05+2.7=4.73)"
}
```




### learn.md

### Exponential Recency-Weighted Average

When the environment is nonstationary, it is better to give more weight to recent rewards. The formula $$(1-\alpha)^k Q_1 + \sum_{i=1}^k \alpha (1-\alpha)^{k-i} R_i$$ computes the expected value by exponentially decaying the influence of old rewards and the initial estimate. The parameter $\alpha$ controls how quickly old information is forgotten: higher $\alpha$ gives more weight to new rewards.


### meta.json

```json
{
  "id": "161",
  "title": "Exponential Weighted Average of Rewards",
  "difficulty": "medium",
  "category": "Reinforcement Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ]
}
```




### solution.py

```python
def exp_weighted_average(Q1, rewards, alpha):
    k = len(rewards)
    value = (1 - alpha) ** k * Q1
    for i, Ri in enumerate(rewards):
        value += alpha * (1 - alpha) ** (k - i - 1) * Ri
    return value
```




### starter_code.py

```python
def exp_weighted_average(Q1, rewards, alpha):
    """
    Q1: float, initial estimate
    rewards: list or array of rewards, R_1 to R_k
    alpha: float, step size (0 < alpha <= 1)
    Returns: float, exponentially weighted average after k rewards
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "Q1 = 10.0\nrewards = [4.0, 7.0, 13.0]\nalpha = 0.5\nprint(round(exp_weighted_average(Q1, rewards, alpha), 4))",
    "expected_output": "10.0"
  },
  {
    "test": "Q1 = 0.0\nrewards = [1.0, 1.0, 1.0, 1.0]\nalpha = 0.1\nprint(round(exp_weighted_average(Q1, rewards, alpha), 4))",
    "expected_output": "0.3439"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/161_exponential-weighted-average-of-rewards/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/161_exponential-weighted-average-of-rewards/description.md)。Deep-ML：Educational Use Only License。
