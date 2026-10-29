---
id: drustz-ab8727d1f3dc7271c1
section: deepml
order: 51
level: A
title: Deep-ML legacy · x instance normalization
quick: Deep-ML 练习 · Deep-ML legacy · x instance normalization
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/x_instance_normalization/learn.md
    type: primary
---
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

### solution.py

```python
import numpy as np


def instance_normalization(
    X: np.ndarray, gamma: np.ndarray, beta: np.ndarray, epsilon: float = 1e-5
) -> np.ndarray:
    """
    Perform Instance Normalization.

    Args:
    X: numpy array of shape (B, C, H, W), input data
    gamma: numpy array of shape (C,), scale parameter
    beta: numpy array of shape (C,), shift parameter
    epsilon: small constant to avoid division by zero

    Returns:
    norm_X: numpy array of shape (B, C, H, W), normalized output
    """
    # Compute mean and variance across the feature dimensions
    mean = np.mean(X, axis=(2, 3), keepdims=True)  # Mean over (H, W)
    variance = np.var(X, axis=(2, 3), keepdims=True)  # Variance over (H, W)

    # Normalize
    X_norm = (X - mean) / np.sqrt(variance + epsilon)

    # Scale and shift
    norm_X = gamma * X_norm + beta
    return norm_X


# Test cases for each normalization
def test_normalizations():
    # Test case: Instance Normalization
    B, C, H, W = 2, 2, 2, 2  # Batch size, Channels, Height, Width
    np.random.seed(42)
    X = np.random.randn(B, C, H, W)
    gamma = np.ones(C).reshape(1, C, 1, 1)
    beta = np.zeros(C).reshape(1, C, 1, 1)

    num_groups = 2
    actual_output = instance_normalization(X, gamma, beta, num_groups)
    expected_output = [
        [
            [[-0.08841405, -0.50250083], [0.01004046, 0.58087442]],
            [[-0.43833369, -0.43832346], [0.69114093, 0.18551622]],
        ],
        [
            [[-0.17259136, 0.51115219], [-0.16849938, -0.17006144]],
            [[0.73955155, -0.55463639], [-0.44152783, 0.25661268]],
        ],
    ]
    np.testing.assert_array_almost_equal(
        actual_output, expected_output, decimal=6, err_msg="Test case 1 failed"
    )

    # Test different input
    np.random.seed(101)
    X = np.random.randn(B, C, H, W)
    actual_output = instance_normalization(X, gamma, beta, num_groups)
    expected_output = [
        [
            [[0.90981361, -0.33429942], [-0.16681702, -0.40869718]],
            [[0.40560315, -0.22047364], [-0.56160247, 0.37647295]],
        ],
        [
            [[-0.9411801, 0.60077322], [0.48264645, -0.14223957]],
            [[0.20283074, -0.38711656], [-0.49567481, 0.67996064]],
        ],
    ]
    np.testing.assert_array_almost_equal(
        actual_output, expected_output, decimal=6, err_msg="Test case 2 failed"
    )

    # Test different params
    gamma = np.ones(C).reshape(1, C, 1, 1) * 0.5
    beta = np.ones(C).reshape(1, C, 1, 1)
    actual_output = instance_normalization(X, gamma, beta, num_groups)
    expected_output = [
        [
            [[1.45490681, 0.83285029], [0.91659149, 0.79565141]],
            [[1.20280158, 0.88976318], [0.71919877, 1.18823648]],
        ],
        [
            [[0.52940995, 1.30038661], [1.24132322, 0.92888021]],
            [[1.10141537, 0.80644172], [0.75216259, 1.33998032]],
        ],
    ]
    np.testing.assert_array_almost_equal(
        actual_output, expected_output, decimal=6, err_msg="Test case 3 failed"
    )


if __name__ == "__main__":
    test_normalizations()
    print("All normalization tests passed.")
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/Problems/x_instance_normalization/learn.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/x_instance_normalization/learn.md)。Deep-ML：Educational Use Only License。
