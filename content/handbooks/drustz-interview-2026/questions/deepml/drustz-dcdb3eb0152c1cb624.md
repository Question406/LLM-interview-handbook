---
id: drustz-dcdb3eb0152c1cb624
section: deepml
order: 107
level: A
title: Implement Q-Learning Algorithm for MDPs
quick: Deep-ML 练习 · Implement Q-Learning Algorithm for MDPs
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/133_implement-q-learning-algorithm-for-mdps/description.md
    type: primary
---
### description.md

Write a function that implements the Q-Learning algorithm to learn the optimal Q-table for a given Markov Decision Process (MDP). The function should take the number of states, number of actions, transition probabilities matrix, rewards matrix, list of terminal states, learning rate, discount factor, epsilon for exploration, and the number of episodes as inputs. Use these parameters to iteratively update the Q-table based on the Q-Learning update rule, employing an epsilon-greedy strategy for action selection. Ensure the function handles starting from non-terminal states and stops episodes upon reaching a terminal state.

Constraints:
- num_states: Integer greater than or equal to 1.
- num_actions: Integer greater than or equal to 1.
- P: A 3D NumPy array of shape (num_states, num_actions, num_states) where each element is a probability between 0 and 1, and each sub-array sums to 1.
- R: A 2D NumPy array of shape (num_states, num_actions) with float or integer values.
- terminal_states: A list or NumPy array of integers, each between 0 and num_states - 1, with no duplicates.
- alpha: A float between 0 and 1.
- gamma: A float between 0 and 1.
- epsilon: A float between 0 and 1.
- num_episodes: An integer greater than or equal to 1.
The function should return a 2D NumPy array of shape (num_states, num_actions) representing the learned Q-table.


### example.json

```json
{
  "input": "import numpy as np; np.random.seed(42); P = np.array([[[0, 1], [1, 0]], [[1, 0], [1, 0]]]); R = np.array([[1, 0], [0, 0]]); terminal_states = [1]; print(q_learning(2, 2, P, R, terminal_states, 0.1, 0.9, 0.1, 10))",
  "output": "[[0.65132156, 0.052902  ],[0., 0.]]",
  "reasoning": "The Q-Learning algorithm initializes a Q-table with zeros and iteratively updates it over 10 episodes by starting from random non-terminal states, selecting actions via an epsilon-greedy policy, sampling next states and rewards from the provided transition probabilities (P) and rewards (R), and applying the update rule: Q(s, a) += alpha * (reward + gamma * max(Q(next_state)) - Q(s, a)). This process results in the output Q-table [[0.65132156, 0.052902], [0., 0.]], where the values represent learned estimates of state-action values, with the second state's Q-values remaining zero because it is a terminal state and no further actions are taken from there."
}
```




### learn.md

## Q-Learning: Learning Optimal Actions in Markov Decision Processes

Q-Learning is a method in reinforcement learning used to estimate the value of taking specific actions in different states within a Markov Decision Process (MDP). An MDP models decision-making scenarios where the outcomes of actions depend on the current state, and the goal is to maximize long-term rewards. This section breaks down the key concepts step by step, focusing on the underlying mathematics.

### 1. Understanding Markov Decision Processes
A Markov Decision Process is a framework for sequential decision-making. It consists of states, actions, transition probabilities, and rewards. In an MDP, the future state depends only on the current state and the chosen action, not on the history of previous states.

- States represent the situations an agent might encounter.
- Actions are the choices available in each state.
- Transition probabilities describe the likelihood of moving from one state to another after an action.
- Rewards are numerical values that quantify the immediate benefit of taking an action in a state.

For example, imagine navigating a simple grid where each cell is a state, moving right or left is an action, and reaching a goal gives a reward.

### 2. The Q-Value Function
At the heart of Q-Learning is the Q-value, which estimates the total expected reward of taking a specific action in a given state and then following the best possible strategy afterward.

Mathematically, the Q-value for a state $s$ and action $a$ is denoted as $Q(s, a)$. It is defined by the equation:

$$
Q(s, a) = r(s, a) + \gamma \sum_{s'} P(s' | s, a) \max_{a'} Q(s', a')
$$

Here:
- $r(s, a)$ is the immediate reward received for taking action $a$ in state $s$.
- $\gamma$ (gamma) is the discount factor, a number between 0 and 1 that reduces the importance of future rewards over time (e.g., if $\gamma = 0.9$, rewards in the near future are valued more than those far ahead).
- $P(s' | s, a)$ is the transition probability, representing the likelihood of ending up in state $s'$ after action $a$ in state $s$.
- $\max_{a'} Q(s', a')$ is the maximum Q-value of all possible actions in the next state $s'$, indicating the best future choice.

This equation captures the idea that the Q-value balances immediate rewards with the discounted value of future rewards, helping to identify the most valuable actions over time.

### 3. The Q-Learning Update Rule
Q-Learning updates the Q-value estimates iteratively based on experience, using a simple iterative formula. This process allows the agent to learn from trials without needing to know the full transition probabilities in advance.

The update rule is:

$$
Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]
$$

In this equation:
- $\alpha$ (alpha) is the learning rate, a value between 0 and 1 that controls how much new information overrides old estimates (e.g., if $\alpha = 0.1$, updates are gradual).
- $r$ is the reward observed after taking action $a$ in state $s$.
- $s'$ is the next state that results from the action.
- The term inside the brackets, $r + \gamma \max_{a'} Q(s', a') - Q(s, a)$, is the difference between the estimated Q-value and the actual experienced value, known as the temporal difference error.

This rule refines Q-values over multiple episodes, gradually converging to the optimal values that maximize long-term rewards.

### 4. Balancing Exploration and Exploitation
To learn effectively, Q-Learning must balance exploring new actions (to discover potential rewards) and exploiting known high-value actions.

This is achieved through an epsilon-greedy strategy, where:
- With probability $\epsilon$ (epsilon, a small number like 0.1), a random action is selected to encourage exploration.
- With probability $1 - \epsilon$, the action with the highest Q-value is chosen to exploit current knowledge.

For instance, if $\epsilon = 0.2$, in 20% of decisions, the agent tries something random, while in 80%, it picks the best-known option. Over time, $\epsilon$ can be reduced to favor exploitation as learning progresses.

---

### Example Walkthrough
Consider a simple two-state MDP: State A and State B, with two actions in each (Action 1 and Action 2). Suppose:
- From State A, Action 1 leads to State B with probability 1 and a reward of 1.
- From State B, any action ends the process with a reward of 0 (State B is terminal).
- Let $\gamma = 0.9$ and $\alpha = 0.5$.

Initially, assume all Q-values are 0. In the first episode:
- Start in State A and choose Action 1 (greedily, since all Q-values are equal).
- Move to State B, receive reward 1, and since State B is terminal, the update is:  
  $$
  Q(\text{A}, \text{Action 1}) \leftarrow 0 + 0.5 \left[ 1 + 0.9 \cdot 0 - 0 \right] = 0.5
  $$
- Now, Q(A, Action 1) is 0.5, so in future episodes, Action 1 is more likely in State A.

Through repeated episodes, Q-values adjust to reflect the best long-term rewards, such as prioritizing paths that lead to higher cumulative rewards.


### meta.json

```json
{
  "id": "133",
  "title": "Implement Q-Learning Algorithm for MDPs",
  "difficulty": "medium",
  "category": "Reinforcement Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "moe"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def q_learning(
    num_states, num_actions, P, R, terminal_states, alpha, gamma, epsilon, num_episodes
):
    """
    Implements Q-Learning algorithm to learn the optimal Q-table for a given MDP.

    Parameters:
    - num_states: int, number of states in the MDP
    - num_actions: int, number of actions in the MDP
    - P: NumPy array of shape (num_states, num_actions, num_states), transition probabilities
    - R: NumPy array of shape (num_states, num_actions), rewards for each state-action pair
    - terminal_states: list or NumPy array of integers, indices of terminal states
    - alpha: float, learning rate
    - gamma: float, discount factor
    - epsilon: float, probability of choosing a random action in epsilon-greedy policy
    - num_episodes: int, number of episodes to train

    Returns:
    - Q: NumPy array of shape (num_states, num_actions), the learned Q-table
    """
    Q = np.zeros((num_states, num_actions))

    for episode in range(num_episodes):
        # Start from a random non-terminal state
        state = np.random.choice(
            [s for s in range(num_states) if s not in set(terminal_states)]
        )

        while state not in terminal_states:
            # Epsilon-greedy action selection
            if np.random.rand() < epsilon:
                action = np.random.randint(num_actions)
            else:
                action = np.argmax(Q[state])

            # Sample next state based on transition probabilities
            next_state = np.random.choice(num_states, p=P[state, action])

            # Get reward
            reward = R[state, action]

            # Compute target Q-value
            if next_state in terminal_states:
                target = reward
            else:
                target = reward + gamma * np.max(Q[next_state])

            # Update Q-table
            Q[state, action] += alpha * (target - Q[state, action])

            # Transition to next state
            state = next_state

    return Q
```




### starter_code.py

```python
import numpy as np


def q_learning(
    num_states, num_actions, P, R, terminal_states, alpha, gamma, epsilon, num_episodes
):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np; np.random.seed(42); P = np.array([[[0, 1], [1, 0]], [[1, 0], [1, 0]]]); R = np.array([[1, 0], [0, 0]]); terminal_states = [1]; print(q_learning(2, 2, P, R, terminal_states, 0.1, 0.9, 0.1, 10))",
    "expected_output": "[[0.65132156, 0.052902  ],[0., 0.        ]]"
  },
  {
    "test": "import numpy as np; np.random.seed(42); P = np.array([[[0.5, 0.5], [0, 1]], [[0, 1], [1, 0]]]); R = np.array([[0.5, 1], [0, 0]]); terminal_states = [1]; print(q_learning(2, 2, P, R, terminal_states, 0.5, 0.8, 0.2, 5))",
    "expected_output": "[[0.91785477, 0.5       ],[0., 0.        ]]"
  },
  {
    "test": "import numpy as np; np.random.seed(42); P = np.array([[[1, 0], [0, 1]], [[0.5, 0.5], [0.5, 0.5]]]); R = np.array([[2, 1], [0, 0]]); terminal_states = [0]; print(q_learning(2, 2, P, R, terminal_states, 0.3, 0.7, 0.05, 20))",
    "expected_output": "[[0., 0.],[0., 0.]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/133_implement-q-learning-algorithm-for-mdps/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/133_implement-q-learning-algorithm-for-mdps/description.md)。Deep-ML：Educational Use Only License。
