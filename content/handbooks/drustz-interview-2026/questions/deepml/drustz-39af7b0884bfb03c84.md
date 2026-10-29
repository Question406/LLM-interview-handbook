---
id: drustz-39af7b0884bfb03c84
section: deepml
order: 54
level: A
title: Derivative of a Polynomial
quick: Deep-ML 练习 · Derivative of a Polynomial
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/116_derivative-of-a-polynomial/description.md
    type: primary
---
### description.md

Implement a function that computes the derivative of a polynomial term of the form `c * x^n` at a given point `x`, where `c` is a coefficient and `n` is the exponent. The function should return the value of the derivative, accounting for the coefficient in the power rule. This is useful for understanding how polynomials change at specific points in machine learning optimization problems.


### example.json

```json
{
  "input": "poly_term_derivative(2.0, 3.0, 2.0)",
  "output": "12.0",
  "reasoning": "For the term 2 * x^2, the derivative is 2 * 2 * x^(2-1) = 4 * x. At x = 3, this evaluates to 4 * 3 = 12.0."
}
```




### learn.md

## Derivative of a Polynomial

A function's derivative is a way of quantifying the function's slope at a given point. It allows us to understand whether the function is increasing, decreasing or flat at specific input. 

Taking the derivative of a polynomial at a single point follows a straight-forward rule. This question will show the rule and the edge case you should be on the look-out for.

### Mathematical Definition

When calculating the slope of a function $f(x)$, we usually require two points $x_{1}$ and $x_{2}$ and use the following formula:

$$
\frac{f(x_{2}) - f(x_{1})}{x_{2} - x_{1}}
$$

A derivative generalizes that notion by calculating the slope of a function at a specific point.
A derivative of a function $f(x)$ is mathematically defined as:

$$
\frac{d f(x)}{d x} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$

Where:
- $x$ is the input to the function
- $h$ is the "step", which is equivalent to the difference $x_{2} - x_{1}$ in the two-point slope-formula

Taking the limit as the step grows smaller and smaller, allow us to quantify the slope at a certain point, instead of having to consider two points as in other methods of finding the slope.

When taking the derivative of a polynomial function $x^{n}$, where $n \neq 0$, then the derivative is: $n x^{n-1}$. In the special case where $n = 0$ then the derivative is zero. This is because $x^{0} = 1$ if $x \neq 0$.

A positive derivative indicates that the function is increasing in that point, a negative derivative indicates that the function is decreasing at that point. A derivative equal to zero indicates that the function is flat, which could potentially indicate a function's minimum or maximum.


### meta.json

```json
{
  "id": "116",
  "title": "Derivative of a Polynomial",
  "difficulty": "easy",
  "category": "calculus",
  "video": "https://youtu.be/xoRFwJdDT0A",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Selbl",
      "name": "Selbl"
    }
  ]
}
```




### solution.py

```python
def poly_term_derivative(c: float, x: float, n: float) -> float:
    if n == 0.0:
        return 0.0
    return round(c * n * (x ** (n - 1)), 4)
```




### starter_code.py

```python
def poly_term_derivative(c: float, x: float, n: float) -> float:
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(poly_term_derivative(2.0, 3.0, 2.0))",
    "expected_output": "12.0"
  },
  {
    "test": "print(poly_term_derivative(1.5, 4.0, 0.0))",
    "expected_output": "0.0"
  },
  {
    "test": "print(poly_term_derivative(3.0, 2.0, 3.0))",
    "expected_output": "36.0"
  },
  {
    "test": "print(poly_term_derivative(0.5, 5.0, 1.0))",
    "expected_output": "0.5"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/116_derivative-of-a-polynomial/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/116_derivative-of-a-polynomial/description.md)。Deep-ML：Educational Use Only License。
