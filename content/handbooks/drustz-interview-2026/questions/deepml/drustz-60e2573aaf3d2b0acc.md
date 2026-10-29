---
id: drustz-60e2573aaf3d2b0acc
section: deepml
order: 63
level: A
title: Epsilon-Greedy Action Selection for n-Armed Bandit
quick: Deep-ML 练习 · Epsilon-Greedy Action Selection for n-Armed Bandit
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/158_epsilon-greedy-action-selection-for-n-armed-bandit/description.md
    type: primary
---
### description.md

Implement the epsilon-greedy method for action selection in an n-armed bandit problem. Given a set of estimated action values (Q-values), select an action using the epsilon-greedy policy: with probability epsilon, choose a random action; with probability 1 - epsilon, choose the action with the highest estimated value.


### example.json

```json
{
  "input": "Q = np.array([0.5, 2.3, 1.7])\nepsilon = 0.0\naction = epsilon_greedy(Q, epsilon)\nprint(action)",
  "output": "1",
  "reasoning": "With epsilon=0.0 (always greedy), the highest Q-value is 2.3 at index 1, so the function always returns 1."
}
```




### learn.md

### Epsilon-Greedy Policy

The epsilon-greedy method is a fundamental action selection strategy used in reinforcement learning, especially for solving the n-armed bandit problem. The key idea is to balance **exploration** (trying new actions) and **exploitation** (choosing the best-known action):

- With probability $\varepsilon$ (epsilon), the agent explores by selecting an action at random.
- With probability $1-\varepsilon$, it exploits by choosing the action with the highest estimated value (greedy choice).

The epsilon-greedy policy is simple to implement and provides a way to avoid getting stuck with suboptimal actions due to insufficient exploration.


### meta.json

```json
{
  "id": "158",
  "title": "Epsilon-Greedy Action Selection for n-Armed Bandit",
  "difficulty": "easy",
  "category": "Reinforcement Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": []
}
```




### solution.py

```python
import numpy as np


def epsilon_greedy(Q, epsilon=0.1):
    if np.random.rand() < epsilon:
        return np.random.randint(len(Q))
    else:
        return int(np.argmax(Q))
```




### starter_code.py

```python
import numpy as np


def epsilon_greedy(Q, epsilon=0.1):
    """
    Selects an action using epsilon-greedy policy.
    Q: np.ndarray of shape (n,) -- estimated action values
    epsilon: float in [0, 1]
    Returns: int, selected action index
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nnp.random.seed(0)\nprint([epsilon_greedy(np.array([1, 2, 3]), epsilon=0.0) for _ in range(5)])",
    "expected_output": "[2, 2, 2, 2, 2]"
  },
  {
    "test": "import numpy as np\nnp.random.seed(1)\nprint([epsilon_greedy(np.array([5, 2, 1]), epsilon=1.0) for _ in range(5)])",
    "expected_output": "[0, 1, 1, 0, 0]"
  },
  {
    "test": "import numpy as np\nnp.random.seed(42)\nresults = [epsilon_greedy(np.array([1.5, 2.5, 0.5]), epsilon=0.5) for _ in range(10)]\nprint(results)",
    "expected_output": "[1, 0, 1, 1, 1, 0, 1, 0, 0, 0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/158_epsilon-greedy-action-selection-for-n-armed-bandit/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/158_epsilon-greedy-action-selection-for-n-armed-bandit/description.md)。Deep-ML：Educational Use Only License。
