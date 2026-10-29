---
id: drustz-74ec78c47d6d3e247a
section: deepml
order: 68
level: A
title: Find Captain Redbeard's Hidden Treasure
quick: Deep-ML 练习 · Find Captain Redbeard's Hidden Treasure
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/127_find-captain-redbeard-s-hidden-treasure/description.md
    type: primary
---
### description.md

Captain Redbeard, the most daring pirate of the seven seas, has uncovered a mysterious ancient map. Instead of islands, it shows a strange wavy curve, and the treasure lies at the lowest point of the land! (watch out for those tricky local mins)

The land's height at any point $x$ is given by:

f(x) =  $x^4$  -  $3x^3$  + 2


**Your Mission:**
Implement a Python function that finds the value of $x$ where $f(x)$ reaches its minimum, starting from any random initial position.


### example.json

```json
{
  "input": "start_x = 0.0",
  "output": "min float value",
  "reasoning": "Cant really give you a example without giving the solution... so ya"
}
```




### learn.md

## How to Find the Minimum of a Function

To find the minimum of a function like

$$
f(x) = x^4 - 3x^3 + 2
$$

we can use a technique called **gradient descent**.

### Steps:

1. **Find the Derivative**
   - The derivative (slope) tells us which direction the function is increasing or decreasing.
   - For this problem, the derivative is:
     $$
     f'(x) = 4x^3 - 9x^2
     $$

2. **Move Opposite the Slope**
   - If the slope is positive, move left.
   - If the slope is negative, move right.
   - Update the position by:
     $$
     x_{new} = x_{old} - \text{learning rate} \times f'(x_{old})
     $$

3. **Repeat**
   - Keep updating $x$ until the change is very small (below a tolerance).

### Why Does This Work?
- If you always move downhill along the slope, you eventually reach a bottom a local minimum.

### Important Terms
- **Learning Rate**: How big a step to take each update.
- **Tolerance**: How close successive steps must be to stop.
- **Local Minimum**: A point where the function value is lower than nearby points.

In this problem, Captain Redbeard finds the hidden treasure by moving downhill until he reaches the lowest point!


### meta.json

```json
{
  "id": "127",
  "title": "Find Captain Redbeard's Hidden Treasure",
  "difficulty": "medium",
  "category": "Calculus",
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

```text
def find_treasure(start_x: float) -> float:
	learning_rate = 0.1, tolerance = 1e-6, max_iters = 10000)    def gradient(x):
        return 4 * x**3 - 9 * x**2  # derivative of x^4 - 3x^3 + 2

    x = start_x
    for _ in range(max_iters):
        grad = gradient(x)
        new_x = x - learning_rate * grad
        if abs(new_x - x) < tolerance:
            break
        x = new_x
    return round(x, 4)
```




### starter_code.py

```python
def find_treasure(start_x: float) -> float:
    """
      Find the x-coordinate where f(x) = x^4 - 3x^3 + 2 is minimized.

    Returns:
          float: The x-coordinate of the minimum point.
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(abs(find_treasure(-1) - 2.25) < 1e-2)",
    "expected_output": "True"
  },
  {
    "test": "print(abs(find_treasure(1.0) - 2.25) < 1e-2)",
    "expected_output": "True"
  },
  {
    "test": "print(abs(find_treasure(3.0) - 2.25) < 1e-2)",
    "expected_output": "True"
  }
]
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/127_find-captain-redbeard-s-hidden-treasure/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/127_find-captain-redbeard-s-hidden-treasure/description.md)。Deep-ML：Educational Use Only License。
