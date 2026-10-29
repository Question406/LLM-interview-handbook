---
id: drustz-bbc0de23e63e6d66c7
section: deepml
order: 154
level: A
title: Policy Gradient with REINFORCE
quick: Deep-ML 练习 · Policy Gradient with REINFORCE
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/122_policy-gradient-with-reinforce/description.md
    type: primary
---
### description.md

Implement the policy gradient estimator using the REINFORCE algorithm. The policy is parameterized by a 2D NumPy array `theta` of shape `(num_states, num_actions)`. The policy for each state is computed via softmax over `theta[s, :]`. Given a list of episodes (each a list of (state, action, reward) tuples), compute the average gradient of the log-policy multiplied by the return at each time step.


### example.json

```json
{
  "input": "theta = np.zeros((2,2)); episodes = [[(0,1,0), (1,0,1)], [(0,0,0)]]",
  "output": "[[-0.25, 0.25], [0.25, -0.25]]",
  "reasoning": "Episode 1 contributes a positive gradient from reward 1 at t=1; episode 2 adds zero. Result is averaged across episodes."
}
```




### learn.md

## REINFORCE and Policy Gradient Estimation

The REINFORCE algorithm computes gradients of the expected return with respect to policy parameters using Monte Carlo samples of episodes.

### Softmax Policy
Given $\theta$ with shape (num_states, num_actions), we define the probability of action $a$ in state $s$ as:

$$
\pi(a \mid s; \theta) = \frac{\exp(\theta[s, a])}{\sum_{a'} \exp(\theta[s, a'])}
$$

### REINFORCE Gradient
For an episode with transitions $(s_t, a_t, r_t)$ and returns $G_t = \sum_{k=t}^T r_k$:

$$
\nabla_\theta J(\theta) \approx \sum_t \nabla_\theta \log \pi(a_t \mid s_t) \cdot G_t
$$

### Log-Policy Gradient
To compute $\nabla_\theta \log \pi(a_t \mid s_t)$:

- For $\theta[s_t, a_t]$: $1 - \pi(a_t \mid s_t)$
- For $\theta[s_t, a']$, where $a' \neq a_t$: $-\pi(a' \mid s_t)$
- All other entries: 0

### Final Estimate
For multiple episodes:

$$
\hat{\nabla}_\theta J(\theta) = \frac{1}{N} \sum_{i=1}^N \sum_{t=0}^{T_i} \nabla_\theta \log \pi(a_t^i \mid s_t^i) \cdot G_t^i
$$

This algorithm works even without value function estimation, making it a foundational method in policy-based reinforcement learning.


### meta.json

```json
{
  "id": "122",
  "title": "Policy Gradient with REINFORCE",
  "difficulty": "hard",
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
import numpy as np


def compute_policy_gradient(theta, episodes):
    def softmax(x):
        x = x - np.max(x)
        exps = np.exp(x)
        return exps / np.sum(exps)

    grad = np.zeros_like(theta)
    for episode in episodes:
        rewards = [step[2] for step in episode]
        returns = np.cumsum(rewards[::-1])[::-1]
        for t, (s, a, _), G in zip(range(len(episode)), episode, returns):
            probs = softmax(theta[s])
            grad_log_pi = np.zeros_like(theta)
            grad_log_pi[s, :] = -probs
            grad_log_pi[s, a] += 1
            grad += grad_log_pi * G
    return grad / len(episodes)
```




### starter_code.py

```python
import numpy as np


def compute_policy_gradient(
    theta: np.ndarray, episodes: list[list[tuple[int, int, float]]]
) -> np.ndarray:
    """
    Estimate the policy gradient using REINFORCE.

    Args:
        theta: (num_states x num_actions) policy parameters.
        episodes: List of episodes, where each episode is a list of (state, action, reward).

    Returns:
        Average policy gradient (same shape as theta).
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "theta = np.zeros((2,2)); episodes = [[(0,1,0), (1,0,1)], [(0,0,0)]]; print(np.round(compute_policy_gradient(theta, episodes), 4))",
    "expected_output": "[[-0.25  0.25]\n [ 0.25 -0.25]]"
  },
  {
    "test": "theta = np.zeros((2,2)); episodes = [[(0,0,0)], [(0,1,0), (1,1,0)]]; print(np.round(compute_policy_gradient(theta, episodes), 4))",
    "expected_output": "[[0. 0.]\n [0. 0.]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/122_policy-gradient-with-reinforce/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/122_policy-gradient-with-reinforce/description.md)。Deep-ML：Educational Use Only License。
