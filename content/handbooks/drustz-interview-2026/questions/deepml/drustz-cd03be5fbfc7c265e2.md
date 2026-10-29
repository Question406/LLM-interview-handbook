---
id: drustz-cd03be5fbfc7c265e2
section: deepml
order: 137
level: A
title: Linear Regression - Power Grid Optimization
quick: Deep-ML 练习 · Linear Regression - Power Grid Optimization
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/92_linear-regression-power-grid-optimization/description.md
    type: primary
---
### description.md

It is the year 2157. Mars has its first thriving colony, and energy consumption is steadily on the rise. As the lead data scientist, you have daily power usage measurements (10 days) affected by both a growing linear trend and a daily fluctuation. The fluctuation follows the formula  $f_{i}$  = 10 x sin(2π x i / 10), where i is the day number (1 through 10). Your challenge is to remove this known fluctuation from each data point, fit a linear regression model to the detrended data, predict day 15's base consumption, add back the fluctuation for day 15, and finally include a 5% safety margin. The final answer must be an integer, ensuring you meet the colony's future needs.


### example.json

```json
{
  "input": "Daily consumption data for 10 days: [150, 165, 185, 195, 210, 225, 240, 260, 275, 290]",
  "output": "404",
  "reasoning": "For each of the 10 days, we subtract the daily fluctuation given by 10xsin(2πxi/10). We then perform linear regression on the resulting values, predict day 15’s base usage, and add back the day 15 fluctuation. Finally, we apply a 5% margin. Running the provided solution code yields 404 for this dataset."
}
```




### learn.md

## Balancing Trend and Fluctuation with Math

When dealing with time-series data, it's common to see both a long-term trend and periodic fluctuations. In this challenge, the daily fluctuation for day $i$ is given by:

$$
f_i = 10 \times \sin\left(\frac{2\pi \times i}{10}\right).
$$

### Steps to Solve

1. **Fluctuation Removal**: Subtract $f_i$ from each day's consumption to isolate the colony's base usage.

2. **Linear Regression**: Fit a linear model $y = mx + b$ using the detrended values. The slope $m$ and intercept $b$ are calculated using the least squares method:

$$
m = \frac{n \sum(x_i y_i) - (\sum x_i)(\sum y_i)}{n \sum(x_i^2) - (\sum x_i)^2}, \quad b = \frac{\sum y_i - m \sum x_i}{n}.
$$

Here, $n$ is the number of data points (10 in this case).

3. **Forecast**: Use the regression line to predict the base consumption for day 15, $x = 15$:

$$
\text{base}_{15} = m \times 15 + b.
$$

4. **Add Back Fluctuation**: Compute $f_{15} = 10 \times \sin\left(\frac{2\pi \times 15}{10}\right)$ and add it to the base prediction:

$$
\text{pred}_{15} = \text{base}_{15} + f_{15}.
$$

5. **Round and Add Safety Margin**: Round $\text{pred}_{15}$ to the nearest integer and then apply a 5% upward safety margin to ensure sufficient capacity:

$$
\text{final}_{15} = \lceil 1.05 \times \text{round}(\text{pred}_{15}) \rceil.
$$

### Summary

By following these steps **removing the fluctuation**, **fitting the linear model**, **predicting day 15**'s base consumption, **restoring the fluctuation**, and **applying a safety margin** you'll arrive at a robust energy requirement forecast for the colony's future needs.


### meta.json

```json
{
  "id": "92",
  "title": "Linear Regression - Power Grid Optimization",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://groundzeroai.netlify.app/",
      "name": "GroundZero AI"
    }
  ]
}
```




### solution.py

```python
import math

PI = 3.14159


def power_grid_forecast(consumption_data):
    # consumption_data: list of 10 daily consumption values
    # days: 1 through 10
    days = list(range(1, 11))
    n = len(days)

    # 1) Remove daily fluctuation f_i = 10 * sin(2π * i / 10)
    detrended = []
    for i, cons in zip(days, consumption_data):
        fluctuation_i = 10 * math.sin((2 * PI * i) / 10)
        detrended_value = cons - fluctuation_i
        detrended.append(detrended_value)

    # 2) Perform linear regression on the detrended data
    sum_x = sum(days)
    sum_y = sum(detrended)
    sum_xy = sum(x * y for x, y in zip(days, detrended))
    sum_x2 = sum(x**2 for x in days)

    # slope (m) and intercept (b) for y = m*x + b
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
    b = (sum_y - m * sum_x) / n

    # 3) Predict day 15's base usage
    day_15_base = m * 15 + b

    # 4) Add back daily fluctuation for day 15
    day_15_fluctuation = 10 * math.sin((2 * PI * 15) / 10)
    day_15_prediction = day_15_base + day_15_fluctuation

    # 5) Round and add 5% safety margin
    day_15_rounded = round(day_15_prediction)
    final_15 = math.ceil(day_15_rounded * 1.05)

    return final_15
```




### starter_code.py

```python
import math

PI = 3.14159


def power_grid_forecast(consumption_data):
    # 1) Subtract the daily fluctuation (10 * sin(2π * i / 10)) from each data point.
    # 2) Perform linear regression on the detrended data.
    # 3) Predict day 15's base consumption.
    # 4) Add the day 15 fluctuation back.
    # 5) Round, then add a 5% safety margin (rounded up).
    # 6) Return the final integer.
    pass
```




### tests.json

```json
[
  {
    "test": "print(power_grid_forecast([150, 165, 185, 195, 210, 225, 240, 260, 275, 290]))",
    "expected_output": "404"
  },
  {
    "test": "print(power_grid_forecast([160, 170, 190, 200, 215, 230, 245, 265, 280, 295]))",
    "expected_output": "407"
  },
  {
    "test": "print(power_grid_forecast([140, 158, 180, 193, 205, 220, 237, 255, 270, 288]))",
    "expected_output": "404"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/92_linear-regression-power-grid-optimization/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/92_linear-regression-power-grid-optimization/description.md)。Deep-ML：Educational Use Only License。
