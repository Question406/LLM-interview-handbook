---
id: drustz-c5b172f0cbee86b656
section: deepml
order: 79
level: A
title: Grayscale Image Contrast Calculator
quick: Deep-ML 练习 · Grayscale Image Contrast Calculator
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/82_grayscale-image-contrast-calculator/description.md
    type: primary
---
### description.md

Write a Python function to calculate the contrast of a grayscale image using the difference between the maximum and minimum pixel values.


### example.json

```json
{
  "input": "img = np.array([[0, 50], [200, 255]])",
  "output": "255",
  "reasoning": "The function calculates contrast by finding the difference between the maximum (255) and minimum (0) pixel values in the image, resulting in a contrast of 255."
}
```




### learn.md

## Calculating Contrast of a Grayscale Image

Contrast in a grayscale image refers to the difference in luminance or color that makes an object distinguishable. Here are methods to calculate contrast:

### 1. Basic Contrast Calculation

The simplest way to define the contrast of a grayscale image is by using the difference between the maximum and minimum pixel values:

$$
\text{Contrast} = \max(I) - \min(I)
$$

### 2. RMS Contrast

Root Mean Square (RMS) contrast considers the standard deviation of pixel intensities:

$$
\text{RMS Contrast} = \frac{\sigma}{\mu}
$$

### 3. Michelson Contrast

Michelson contrast is defined as:

$$
C = \frac{I_{\text{max}} - I_{\text{min}}}{I_{\text{max}} + I_{\text{min}}}
$$

### Example Calculation

For a grayscale image with pixel values ranging from 50 to 200:

1. **Maximum Pixel Value**: 200  
2. **Minimum Pixel Value**: 50  
3. **Contrast Calculation**:

$$
\text{Contrast} = 200 - 50 = 150
$$

### Applications

Calculating contrast is crucial in:

- Image quality assessment
- Preprocessing in computer vision
- Enhancing visibility in images
- Object detection and analysis


### meta.json

```json
{
  "id": "82",
  "title": "Grayscale Image Contrast Calculator",
  "difficulty": "easy",
  "category": "Computer Vision",
  "video": "https://youtu.be/-IW2yzulQqI?si=gbdhQ5pRkwuDzaDB",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/rittik9",
      "name": "rittik9"
    }
  ],
  "marimo_link": "https://open-deep-ml.github.io/DML-OpenProblem/problem-82"
}
```




### solution.py

```python
import numpy as np


def calculate_contrast(img):
    """
    Calculate the contrast of a grayscale image.
    Args:
        img (numpy.ndarray): 2D array representing a grayscale image with pixel values between 0 and 255.
    Returns:
        float: Contrast value rounded to 3 decimal places.
    """
    # Find the maximum and minimum pixel values
    max_pixel = np.max(img)
    min_pixel = np.min(img)

    # Calculate contrast
    contrast = max_pixel - min_pixel

    return round(float(contrast), 3)
```




### starter_code.py

```python
import numpy as np


def calculate_contrast(img) -> int:
    """
    Calculate the contrast of a grayscale image.
    Args:
            img (numpy.ndarray): 2D array representing a grayscale image with pixel values between 0 and 255.
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(calculate_contrast(np.array([[0, 50], [200, 255]])))",
    "expected_output": "255"
  },
  {
    "test": "print(calculate_contrast(np.array([[128, 128], [128, 128]])))",
    "expected_output": "0"
  },
  {
    "test": "print(calculate_contrast(np.zeros((10, 10), dtype=np.uint8)))",
    "expected_output": "0"
  },
  {
    "test": "print(calculate_contrast(np.ones((10, 10), dtype=np.uint8) * 255))",
    "expected_output": "0"
  },
  {
    "test": "print(calculate_contrast(np.array([[10, 20, 30], [40, 50, 60]])))",
    "expected_output": "50"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/82_grayscale-image-contrast-calculator/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/82_grayscale-image-contrast-calculator/description.md)。Deep-ML：Educational Use Only License。
