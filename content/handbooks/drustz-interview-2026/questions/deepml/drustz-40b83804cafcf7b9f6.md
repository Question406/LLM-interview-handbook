---
id: drustz-40b83804cafcf7b9f6
section: deepml
order: 80
level: A
title: Gridworld Policy Evaluation
quick: Deep-ML 练习 · Gridworld Policy Evaluation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/142_gridworld-policy-evaluation/description.md
    type: primary
---
### description.md

Implement policy evaluation for a 5x5 gridworld. Given a policy (mapping each state to action probabilities), compute the state-value function $V(s)$ for each cell using the Bellman expectation equation. The agent can move up, down, left, or right, receiving a constant reward of -1 for each move. Terminal states (the four corners) are fixed at 0. Iterate until the largest change in $V$ is less than a given threshold. Only use Python built-ins and no external RL libraries.


### example.json

```json
{
  "input": "policy = {(i, j): {'up': 0.25, 'down': 0.25, 'left': 0.25, 'right': 0.25} for i in range(5) for j in range(5)}\ngamma = 0.9\nthreshold = 0.001\nV = gridworld_policy_evaluation(policy, gamma, threshold)\nprint(round(V[2][2], 4))",
  "output": "-7.0902",
  "reasoning": "The policy is uniform (equal chance of each move). The agent receives -1 per step. After iterative updates, the center state value converges to about -7.09, and corners remain at 0."
}
```




### learn.md

# Gridworld Policy Evaluation

In reinforcement learning, **policy evaluation** is the process of computing the state-value function for a given policy. For a gridworld environment, this involves iteratively updating the value of each state based on the expected return following the policy.

## Key Concepts

- **State-Value Function (V):**  
  The expected return when starting from a state and following a given policy.

- **Policy:**  
  A mapping from states to probabilities of selecting each available action.

- **Bellman Expectation Equation:**  
  For each state $s$:
  $$
  V(s) = \sum_{a} \pi(a|s) \sum_{s'} P(s'|s,a) [R(s,a,s') + \gamma V(s')]
  $$
  where:
  - $ \pi(a|s) $ is the probability of taking action $ a $ in state $ s $,
  - $ P(s'|s,a) $ is the probability of transitioning to state $ s' $,
  - $ R(s,a,s') $ is the reward for that transition,
  - $ \gamma $ is the discount factor.

## Algorithm Overview

1. **Initialization:**  
   Start with an initial guess (commonly zeros) for the state-value function $ V(s) $.

2. **Iterative Update:**  
   For each non-terminal state, update the state value using the Bellman expectation equation. Continue updating until the maximum change in value (delta) is less than a given threshold.

3. **Terminal States:**  
   For this example, the four corners of the grid are considered terminal, so their values remain unchanged.

This evaluation method is essential for understanding how "good" each state is under a specific policy, and it forms the basis for more advanced reinforcement learning algorithms.


### meta.json

```json
{
  "id": "142",
  "title": "Gridworld Policy Evaluation",
  "difficulty": "medium",
  "category": "Reinforcement Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/arpitsinghgautam",
      "name": "Arpit Singh Gautam"
    }
  ]
}
```




### solution.py

```python
def gridworld_policy_evaluation(
    policy: dict, gamma: float, threshold: float
) -> list[list[float]]:
    grid_size = 5
    V = [[0.0 for _ in range(grid_size)] for _ in range(grid_size)]
    actions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
    reward = -1
    while True:
        delta = 0.0
        new_V = [row[:] for row in V]
        for i in range(grid_size):
            for j in range(grid_size):
                if (i, j) in [
                    (0, 0),
                    (0, grid_size - 1),
                    (grid_size - 1, 0),
                    (grid_size - 1, grid_size - 1),
                ]:
                    continue
                v = 0.0
                for action, prob in policy[(i, j)].items():
                    di, dj = actions[action]
                    ni = i + di if 0 <= i + di < grid_size else i
                    nj = j + dj if 0 <= j + dj < grid_size else j
                    v += prob * (reward + gamma * V[ni][nj])
                new_V[i][j] = v
                delta = max(delta, abs(V[i][j] - new_V[i][j]))
        V = new_V
        if delta < threshold:
            break
    return V
```




### starter_code.py

```python
def gridworld_policy_evaluation(
    policy: dict, gamma: float, threshold: float
) -> list[list[float]]:
    """
    Evaluate state-value function for a policy on a 5x5 gridworld.

    Args:
        policy: dict mapping (row, col) to action probability dicts
        gamma: discount factor
        threshold: convergence threshold
    Returns:
        5x5 list of floats
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "grid_size = 5\ngamma = 0.9\nthreshold = 0.001\npolicy = {(i, j): {'up': 0.25, 'down': 0.25, 'left': 0.25, 'right': 0.25} for i in range(grid_size) for j in range(grid_size)}\nV = gridworld_policy_evaluation(policy, gamma, threshold)\nprint([round(V[2][2], 4), V[0][0], V[0][4], V[4][0], V[4][4]])",
    "expected_output": "[-7.0902, 0.0, 0.0, 0.0, 0.0]"
  },
  {
    "test": "grid_size = 5\ngamma = 0.9\nthreshold = 0.001\npolicy = {(i, j): {'up': 0.1, 'down': 0.4, 'left': 0.1, 'right': 0.4} for i in range(grid_size) for j in range(grid_size)}\nV = gridworld_policy_evaluation(policy, gamma, threshold)\nprint(round(V[1][3], 4) < 0)",
    "expected_output": "True"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/142_gridworld-policy-evaluation/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/142_gridworld-policy-evaluation/description.md)。Deep-ML：Educational Use Only License。
