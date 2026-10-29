---
id: drustz-fedf19f5845ff22ef9
section: deepml
order: 132
level: A
title: Instance Normalization (IN) Implementation
quick: Deep-ML 练习 · Instance Normalization (IN) Implementation
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/143_instance-normalization-in-implementation/description.md
    type: primary
---
### description.md

Implement the Instance Normalization operation for 4D tensors (B, C, H, W) using NumPy. For each instance in the batch and each channel, normalize the spatial dimensions (height and width) by subtracting the mean and dividing by the standard deviation, then apply a learned scale (gamma) and shift (beta).


### example.json

```json
{
  "input": "import numpy as np\nB, C, H, W = 2, 2, 2, 2\nnp.random.seed(42)\nX = np.random.randn(B, C, H, W)\ngamma = np.ones(C)\nbeta = np.zeros(C)\nout = instance_normalization(X, gamma, beta)\nprint(np.round(out, 8))",
  "output": "[[[[-0.08841405 -0.50250083]\n   [ 0.01004046  0.58087442]]\n\n  [[-0.43833369 -0.43832346]\n   [ 0.69114093  0.18551622]]]\n\n [[[-0.17259136  0.51115219]\n   [-0.16849938 -0.17006144]]\n\n  [[ 0.73955155 -0.55463639]\n   [-0.44152783  0.25661268]]]]",
  "reasoning": "The function normalizes each instance and channel across (H, W), then applies the gamma and beta scaling/shifting parameters. This matches standard InstanceNorm behavior."
}
```




### learn.md

## Understanding Instance Normalization

Instance Normalization (IN) is a normalization technique primarily used in image generation and style transfer tasks. Unlike Batch Normalization or Group Normalization, Instance Normalization normalizes each individual sample (or instance) separately, across its spatial dimensions. This is particularly effective in applications like style transfer, where normalization is needed per image to preserve the content while allowing different styles to be applied.

### Concepts

Instance Normalization operates on the principle of normalizing each individual sample independently. This helps to remove the style information from the images, leaving only the content. By normalizing each instance, the method allows the model to focus on the content of the image rather than the variations between images in a batch.

The process of Instance Normalization consists of the following steps:

1. **Compute the Mean and Variance for Each Instance:** For each instance (image), compute the mean and variance across its spatial dimensions.
2. **Normalize the Inputs:** Normalize each instance using the computed mean and variance.
3. **Apply Scale and Shift:** After normalization, apply a learned scale (gamma) and shift (beta) to restore the model's ability to represent the data's original distribution.

### Structure of Instance Normalization for BCHW Input

For an input tensor with the shape **BCHW** , where:
- **B**: batch size,
- **C**: number of channels,
- **H**: height,
- **W**: width,
Instance Normalization operates on the spatial dimensions (height and width) of each instance (image) separately.

#### 1. Mean and Variance Calculation for Each Instance

- For each individual instance in the batch (for each **b** in **B**), the **mean** $\mu_b$ and **variance** $\sigma_b^2$ are computed across the spatial dimensions (height and width), but **independently for each channel**.

  $$ 
  \mu_b = \frac{1}{H \cdot W} \sum_{h=1}^{H} \sum_{w=1}^{W} x_{b,c,h,w}
  $$

  $$
  \sigma_b^2 = \frac{1}{H \cdot W} \sum_{h=1}^{H} \sum_{w=1}^{W} (x_{b,c,h,w} - \mu_b)^2
  $$

  Where:
  - $x_{b,c,h,w}$ is the activation at batch index $b$, channel $c$, height $h$, and width $w$.
  - $H$ and $W$ are the spatial dimensions (height and width).

#### 2. Normalization

Once the mean $\mu_b$ and variance $\sigma_b^2$ have been computed for each instance, the next step is to **normalize** the input for each instance across the spatial dimensions (height and width), for each channel:

$$
\hat{x}_{b,c,h,w} = \frac{x_{b,c,h,w} - \mu_b}{\sqrt{\sigma_b^2 + \epsilon}}
$$

Where:
- $\hat{x}_{b,c,h,w}$ is the normalized activation for the input at batch index $b$, channel index $c$, height $h$, and width $w$.
- $\epsilon$ is a small constant added to the variance for numerical stability.

#### 3. Scale and Shift

After normalization, the next step is to apply a **scale** ($\gamma_c$) and **shift** ($\beta_c$) to the normalized activations for each channel. These learned parameters allow the model to adjust the output distribution for each channel:

$$
y_{b,c,h,w} = \gamma_c \hat{x}_{b,c,h,w} + \beta_c
$$

Where:
- $\gamma_c$ is the scaling factor for channel $c$.
- $\beta_c$ is the shifting factor for channel $c$.

#### 4. Training and Inference

- **During Training**: The mean and variance are computed for each instance in the mini-batch and used for normalization.
- **During Inference**: The model uses the running averages of the statistics (mean and variance) computed during training to ensure consistent behavior in production.

### Key Points

- **Instance-wise Normalization**: Instance Normalization normalizes each image independently, across its spatial dimensions (height and width) and across the channels.
  
- **Style Transfer**: This normalization technique is widely used in **style transfer** tasks, where each image must be normalized independently to allow for style information to be adjusted without affecting the content.

- **Batch Independence**: Instance Normalization does not depend on the batch size, as normalization is applied per instance, making it suitable for tasks where per-image normalization is critical.

- **Numerical Stability**: A small constant $\epsilon$ is added to the variance to avoid numerical instability when dividing by the square root of the variance.

- **Improved Training in Style-Related Tasks**: Instance Normalization helps to remove unwanted style-related variability across different images, allowing for better performance in tasks like style transfer, where the goal is to separate content and style information.

### Why Normalize Over Instances?

- **Content Preservation**: By normalizing each image individually, Instance Normalization allows the model to preserve the content of the images while adjusting the style. This makes it ideal for style transfer and other image manipulation tasks.
  
- **Batch Independence**: Unlike Batch Normalization, which requires large batch sizes to compute statistics, Instance Normalization normalizes each image independently, making it suitable for tasks where the batch size is small or varies.

- **Reducing Style Variability**: Instance Normalization removes the variability in style information across a batch, allowing for a consistent representation of content across different images.

In summary, Instance Normalization is effective for image-based tasks like style transfer, where the goal is to normalize each image independently to preserve its content while allowing style modifications.


### meta.json

```json
{
  "id": "143",
  "title": "Instance Normalization (IN) Implementation",
  "difficulty": "medium",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/nzomi",
      "name": "nzomi"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def instance_normalization(
    X: np.ndarray, gamma: np.ndarray, beta: np.ndarray, epsilon: float = 1e-5
) -> np.ndarray:
    # Reshape gamma, beta for broadcasting: (1, C, 1, 1)
    gamma = gamma.reshape(1, -1, 1, 1)
    beta = beta.reshape(1, -1, 1, 1)
    mean = np.mean(X, axis=(2, 3), keepdims=True)
    var = np.var(X, axis=(2, 3), keepdims=True)
    X_norm = (X - mean) / np.sqrt(var + epsilon)
    return gamma * X_norm + beta
```




### starter_code.py

```python
import numpy as np


def instance_normalization(
    X: np.ndarray, gamma: np.ndarray, beta: np.ndarray, epsilon: float = 1e-5
) -> np.ndarray:
    """
    Perform Instance Normalization over a 4D tensor X of shape (B, C, H, W).
    gamma: scale parameter of shape (C,)
    beta: shift parameter of shape (C,)
    epsilon: small value for numerical stability
    Returns: normalized array of same shape as X
    """
    # TODO: Implement Instance Normalization
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nB, C, H, W = 2, 2, 2, 2\nnp.random.seed(42)\nX = np.random.randn(B, C, H, W)\ngamma = np.ones(C)\nbeta = np.zeros(C)\nout = instance_normalization(X, gamma, beta)\nprint(np.round(out[1][1], 4))",
    "expected_output": "[[ 1.4005, -1.0503] [-0.8361, 0.486 ]]"
  },
  {
    "test": "import numpy as np\nB, C, H, W = 2, 2, 2, 2\nnp.random.seed(101)\nX = np.random.randn(B, C, H, W)\ngamma = np.ones(C)\nbeta = np.zeros(C)\nout = instance_normalization(X, gamma, beta)\nprint(np.round(out[1][0], 4))",
    "expected_output": "[[-1.537, 0.9811], [ 0.7882, -0.2323]]"
  },
  {
    "test": "import numpy as np\nB, C, H, W = 2, 2, 2, 2\nnp.random.seed(101)\nX = np.random.randn(B, C, H, W)\ngamma = np.ones(C) * 0.5\nbeta = np.ones(C)\nout = instance_normalization(X, gamma, beta)\nprint(np.round(out[0][0], 4))",
    "expected_output": "[[1.8542, 0.6861], [0.8434, 0.6163]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/143_instance-normalization-in-implementation/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/143_instance-normalization-in-implementation/description.md)。Deep-ML：Educational Use Only License。
