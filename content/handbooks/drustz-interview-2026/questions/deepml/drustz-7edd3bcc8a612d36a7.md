---
id: drustz-7edd3bcc8a612d36a7
section: deepml
order: 49
level: A
title: Deep-ML legacy · x batch normalization
quick: Deep-ML 练习 · Deep-ML legacy · x batch normalization
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/x_batch_normalization/learn.md
    type: primary
---
### learn.md

## Understanding Batch Normalization

Batch Normalization (BN) is a widely used technique that helps to accelerate the training of deep neural networks and improve model performance. By normalizing the inputs to each layer so that they have a mean of zero and a variance of one, BN stabilizes the learning process, speeds up convergence, and introduces regularization, which can reduce the need for other forms of regularization like dropout.

### Concepts

Batch Normalization operates on the principle of reducing **internal covariate shift**, which occurs when the distribution of inputs to a layer changes during training as the model weights get updated. This can slow down training and make hyperparameter tuning more challenging. By normalizing the inputs, BN reduces this problem, allowing the model to train faster and more reliably.

The process of Batch Normalization consists of the following steps:

1. **Compute the Mean and Variance:** For each mini-batch, compute the mean and variance of the activations for each feature (dimension).
2. **Normalize the Inputs:** Normalize the activations using the computed mean and variance.
3. **Apply Scale and Shift:** After normalization, apply a learned scale (gamma) and shift (beta) to restore the model's ability to represent the data's original distribution.
4. **Training and Inference:** During training, the mean and variance are computed from the current mini-batch. During inference, a running average of the statistics from the training phase is used.

### Structure of Batch Normalization for BCHW Input

For an input tensor with the shape **BCHW**, where:
- **B**: batch size,
- **C**: number of channels,
- **H**: height,
- **W**: width,
the Batch Normalization process operates on specific dimensions based on the task's requirement.

#### 1. Mean and Variance Calculation

- In **Batch Normalization**, we typically normalize the activations **across the batch** and **over the spatial dimensions (height and width)** for each **channel**. This means we calculate the mean and variance **per channel** (C) for the **batch and spatial dimensions** (H, W).

For each channel $c$, we compute the **mean** $\mu_c$ and **variance** $\sigma_c^2$ over the mini-batch and spatial dimensions:

$$
\mu_c = \frac{1}{B \cdot H \cdot W} \sum_{i=1}^{B} \sum_{h=1}^{H} \sum_{w=1}^{W} x_{i,c,h,w}
$$

$$
\sigma_c^2 = \frac{1}{B \cdot H \cdot W} \sum_{i=1}^{B} \sum_{h=1}^{H} \sum_{w=1}^{W} (x_{i,c,h,w} - \mu_c)^2
$$

Where:
- $x_{i,c,h,w}$ is the input activation at batch index $i$, channel $c$, height $h$, and width $w$.
- $B$ is the batch size.
- $H$ and $W$ are the spatial dimensions (height and width).
- $C$ is the number of channels.

The mean and variance are computed **over all spatial positions (H, W)** and **across all samples in the batch (B)** for each **channel (C)**.

#### 2. Normalization

Once the mean $\mu_c$ and variance $\sigma_c^2$ have been computed for each channel, the next step is to **normalize** the input. The normalization is done by subtracting the mean and dividing by the standard deviation (plus a small constant $\epsilon$ for numerical stability):

$$
\hat{x}_{i,c,h,w} = \frac{x_{i,c,h,w} - \mu_c}{\sqrt{\sigma_c^2 + \epsilon}}
$$

Where:
- $\hat{x}_{i,c,h,w}$ is the normalized activation for the input at batch index $i$, channel $c$, height $h$, and width $w$.
- $\epsilon$ is a small constant to avoid division by zero (for numerical stability).

#### 3. Scale and Shift

After normalization, the next step is to apply a **scale** ($\gamma_c$) and **shift** ($\beta_c$) to the normalized activations for each channel. These learned parameters allow the model to adjust the output distribution of each feature, preserving the flexibility of the original activations.

$$
y_{i,c,h,w} = \gamma_c \hat{x}_{i,c,h,w} + \beta_c
$$

Where:
- $\gamma_c$ is the scaling factor for channel $c$.
- $\beta_c$ is the shifting factor for channel $c$.

#### 4. Training and Inference

- **During Training**: The mean and variance are computed for each mini-batch and used for normalization across the batch and spatial dimensions for each channel.
- **During Inference**: The model uses a running average of the statistics (mean and variance) that were computed during training to ensure consistent behavior when deployed.

### Key Points

- **Normalization Across Batch and Spatial Dimensions**: In Batch Normalization for **BCHW** input, the normalization is done **across the batch (B) and spatial dimensions (H, W)** for each **channel (C)**. This ensures that each feature channel has zero mean and unit variance, making the training process more stable.
  
- **Channel-wise Normalization**: Batch Normalization normalizes the activations independently for each **channel (C)** because different channels in convolutional layers often have different distributions and should be treated separately.

- **Numerical Stability**: The small constant $\epsilon$ is added to the variance to avoid numerical instability when dividing by the square root of variance, especially when the variance is very small.

- **Improved Gradient Flow**: By reducing internal covariate shift, Batch Normalization allows the gradients to flow more easily during backpropagation, helping the model train faster and converge more reliably.

- **Regularization Effect**: Batch Normalization introduces noise into the training process because it relies on the statistics of a mini-batch. This noise acts as a form of regularization, which can prevent overfitting and improve generalization.

### Why Normalize Over Batch and Spatial Dimensions?

- **Across Batch**: Normalizing across the batch helps to stabilize the input distribution across all samples in a mini-batch. This allows the model to avoid the problem of large fluctuations in the input distribution as weights are updated.
  
- **Across Spatial Dimensions**: In convolutional networks, the spatial dimensions (height and width) are highly correlated, and normalizing over these dimensions ensures that the activations are distributed consistently throughout the spatial field, helping to maintain a stable learning process.

- **Channel-wise Normalization**: Each channel can have its own distribution of values, and normalization per channel ensures that each feature map is scaled and shifted independently, allowing the model to learn representations that are not overly sensitive to specific channels' scaling.

By normalizing across the batch and spatial dimensions and applying a per-channel transformation, Batch Normalization helps reduce internal covariate shift and speeds up training, leading to faster convergence and better overall model performance.

### solution.py

```python
import numpy as np


def batch_normalization(
    X: np.ndarray, gamma: np.ndarray, beta: np.ndarray, epsilon: float = 1e-5
) -> np.ndarray:
    """
    Perform Batch Normalization.

    Args:
    X: numpy array of shape (B, C, H, W), input data
    gamma: numpy array of shape (C,), scale parameter
    beta: numpy array of shape (C,), shift parameter
    epsilon: small constant to avoid division by zero

    Returns:
    norm_X: numpy array of shape (B, C, H, W), normalized output
    """
    # Compute mean and variance across the batch and spatial dimensions
    mean = np.mean(X, axis=(0, 2, 3), keepdims=True)  # Mean over (B, H, W)
    variance = np.var(X, axis=(0, 2, 3), keepdims=True)  # Variance over (B, H, W)

    # Normalize
    X_norm = (X - mean) / np.sqrt(variance + epsilon)

    # Scale and shift
    norm_X = gamma * X_norm + beta
    return norm_X


# Test cases for batch normalization
def test_batch_normalizations():
    # Test case: Batch Normalization
    B, C, H, W = 2, 2, 2, 2  # Batch size, Channels, Height, Width
    np.random.seed(42)
    X = np.random.randn(B, C, H, W)
    gamma = np.ones(C).reshape(1, C, 1, 1)
    beta = np.zeros(C).reshape(1, C, 1, 1)

    # Test batch normalization
    actual_output = batch_normalization(X, gamma, beta)
    expected_output = [
        [
            [[0.42859934, -0.51776438], [0.65360963, 1.95820707]],
            [[0.02353721, 0.02355215], [1.67355207, 0.93490043]],
        ],
        [
            [[-1.01139563, 0.49692747], [-1.00236882, -1.00581468]],
            [[0.45676349, -1.50433085], [-1.33293647, -0.27503802]],
        ],
    ]
    np.testing.assert_array_almost_equal(
        actual_output, expected_output, decimal=6, err_msg="Test case 1 failed"
    )

    # Test different input
    np.random.seed(101)
    X = np.random.randn(B, C, H, W)
    actual_output = batch_normalization(X, gamma, beta)
    expected_output = [
        [
            [[1.81773164, 0.16104096], [0.38406453, 0.06197112]],
            [[1.00432932, -0.37139956], [-1.12098938, 0.94031919]],
        ],
        [
            [[-1.94800122, 0.25029395], [0.08188579, -0.80898678]],
            [[0.34878049, -0.99452891], [-1.24171594, 1.43520478]],
        ],
    ]
    np.testing.assert_array_almost_equal(
        actual_output, expected_output, decimal=6, err_msg="Test case 2 failed"
    )

    # Test different params
    gamma = np.ones(C).reshape(1, C, 1, 1) * 0.5
    beta = np.ones(C).reshape(1, C, 1, 1)
    actual_output = batch_normalization(X, gamma, beta)
    expected_output = [
        [
            [[1.90886582, 1.08052048], [1.19203227, 1.03098556]],
            [[1.50216466, 0.81430022], [0.43950531, 1.4701596]],
        ],
        [
            [[0.02599939, 1.12514697], [1.04094289, 0.59550661]],
            [[1.17439025, 0.50273554], [0.37914203, 1.71760239]],
        ],
    ]
    np.testing.assert_array_almost_equal(
        actual_output, expected_output, decimal=6, err_msg="Test case 3 failed"
    )


if __name__ == "__main__":
    test_batch_normalizations()
    print("All normalization tests passed.")
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/Problems/x_batch_normalization/learn.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/x_batch_normalization/learn.md)。Deep-ML：Educational Use Only License。
