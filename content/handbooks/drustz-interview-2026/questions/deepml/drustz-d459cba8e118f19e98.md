---
id: drustz-d459cba8e118f19e98
section: deepml
order: 81
level: A
title: Implement a Dense Block with 2D Convolutions
quick: Deep-ML 练习 · Implement a Dense Block with 2D Convolutions
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/137_implement-a-dense-block-with-2d-convolutions/description.md
    type: primary
---
### description.md

Create a function `dense_net_block` that performs the forward pass of a **DenseNet dense block** on a batch of images stored in an **NHWC** NumPy tensor `input_data` (shape `(N, H, W, C0)`). The block must run `num_layers` iterations; at each iteration it should (i) apply **ReLU** to the running feature tensor, (ii) convolve it with the corresponding kernel from `kernels` (using stride 1, no bias, and symmetric zero-padding so that `H` and `W` are preserved), and (iii) concatenate the convolution output (whose channel count equals `growth_rate`) to the running tensor along the channel axis. Every kernel `kernels[l]` therefore has shape `(kh, kw, C0 + l x growth_rate, growth_rate)`, where `(kh, kw)` equals `kernel_size` (default `(3, 3)`). After the final layer the function must return a tensor of shape `(N, H, W, C0 + num_layers x growth_rate)`. If any kernel's input-channel dimension does not match the current feature-map channels, the function should raise a `ValueError`.


### example.json

```json
{
  "input": "X = np.random.randn(1, 2, 2, 1); kernels = [np.random.randn(3, 3, 2 + i*1, 1) * 0.01 for i in range(2)]; print(dense_net_block(X, 2, 1, kernels))",
  "reasoning": "Each dense block layer concatenates its output to the existing feature maps, expanding the number of output channels by 1 per layer (the growth rate). After 2 layers, the original 2 channels become 4.",
  "output": "[[[[ 4.96714153e-01, -1.38264301e-01, -2.30186127e-03, -6.70426255e-05]]]]"
}
```




### learn.md

## Understanding Dense Blocks and 2D Convolutions

Dense blocks are a key innovation in the DenseNet architecture. Each layer receives input from **all** previous layers, leading to rich feature reuse and efficient gradient flow.

### Dense Block Concept
For a dense block:
- **Each layer**: Applies ReLU, then 2D convolution, and then concatenates the output to previous features.
- Mathematically:
$$
x_l = H_l([x_0, x_1, \ldots, x_{l-1}])
$$
where $H_l(\cdot)$ is the convolution and activation operations.

### 2D Convolution Basics
A 2D convolution at a position $(i, j)$ for input $X$ and kernel $K$ is:
$$
Y[i, j] = \sum_{m=0}^{k_h - 1} \sum_{n=0}^{k_w - 1} X[i + m, j + n] \cdot K[m, n]
$$

### Padding to Preserve Spatial Dimensions
To preserve height and width:
$$
\text{padding} = \frac{k - 1}{2}
$$

### Dense Block Growth
- Each layer adds $\text{growth rate}$ channels.
- After $L$ layers, total channels = input channels + $L \times \text{growth rate}$.

### Putting It All Together
1️⃣ Start with an input tensor.  
2️⃣ Repeat for $\text{num layers}$:
- Apply ReLU activation.
- Apply 2D convolution (with padding).
- Concatenate the output along the channel dimension.

By understanding these core principles, you’re ready to build the dense block function!


### meta.json

```json
{
  "id": "137",
  "title": "Implement a Dense Block with 2D Convolutions",
  "difficulty": "hard",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def conv2d(x, kernel, padding=0):
    if padding > 0:
        x_padded = np.pad(
            x, ((0, 0), (padding, padding), (padding, padding), (0, 0)), mode='constant'
        )
    else:
        x_padded = x
    batch_size, in_height, in_width, in_channels = x_padded.shape
    kh, kw, _, out_channels = kernel.shape
    out_height = in_height - kh + 1
    out_width = in_width - kw + 1
    output = np.zeros((batch_size, out_height, out_width, out_channels))
    for b in range(batch_size):
        for i in range(out_height):
            for j in range(out_width):
                for c_out in range(out_channels):
                    sum_val = 0.0
                    for c_in in range(in_channels):
                        sum_val += np.sum(
                            x_padded[b, i : i + kh, j : j + kw, c_in]
                            * kernel[:, :, c_in, c_out]
                        )
                    output[b, i, j, c_out] = sum_val
    return output


def dense_net_block(input_data, num_layers, growth_rate, kernels, kernel_size=(3, 3)):
    kh, kw = kernel_size
    padding = (kh - 1) // 2
    concatenated_features = input_data.copy()
    for l in range(num_layers):
        activated = np.maximum(concatenated_features, 0.0)
        conv_output = conv2d(activated, kernels[l], padding=padding)
        concatenated_features = np.concatenate(
            [concatenated_features, conv_output], axis=3
        )
    return concatenated_features
```




### starter_code.py

```python
import numpy as np


def dense_net_block(input_data, num_layers, growth_rate, kernels, kernel_size=(3, 3)):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nnp.random.seed(42)\nX = np.random.randn(1, 1, 1, 2)\nkernels = [np.random.randn(3, 3, 2 + i*1, 1) * 0.01 for i in range(2)]\nprint(dense_net_block(X, 2, 1, kernels))",
    "expected_output": "[[[[ 4.96714153e-01, -1.38264301e-01, -2.30186127e-03, -6.70426255e-05]]]]"
  },
  {
    "test": "import numpy as np\n\nnp.random.seed(42)\nX = np.random.randn(1, 2, 3, 2)\nkernels = [np.random.randn(3, 3, 2 + i*1, 1) * 0.01 for i in range(2)]\nprint(dense_net_block(X, 2, 1, kernels))",
    "expected_output": "[[[[ 0.49671415, -0.1382643 , -0.0308579 , -0.01845547], [ 0.64768854, 1.52302986, -0.0041634 , -0.0161227 ], [-0.23415337, -0.23413696, -0.02678915, 0.00295656]], [[ 1.57921282, 0.76743473, 0.00334109, -0.04043312], [-0.46947439, 0.54256004, -0.04493715, 0.00983633], [-0.46341769, -0.46572975, -0.03523526, 0.02832019]]]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/137_implement-a-dense-block-with-2d-convolutions/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/137_implement-a-dense-block-with-2d-convolutions/description.md)。Deep-ML：Educational Use Only License。
