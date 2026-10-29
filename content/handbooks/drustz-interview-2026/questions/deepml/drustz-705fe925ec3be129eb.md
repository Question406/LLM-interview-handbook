---
id: drustz-705fe925ec3be129eb
section: deepml
order: 176
level: A
title: Train a Simple GAN on 1D Gaussian Data
quick: Deep-ML 练习 · Train a Simple GAN on 1D Gaussian Data
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/174_train-a-simple-gan-on-1d-gaussian-data/description.md
    type: primary
---
### description.md

In this task, you will train a Generative Adversarial Network (GAN) to learn a one-dimensional Gaussian distribution. The GAN consists of a generator that produces samples from latent noise and a discriminator that estimates the probability that a given sample is real. Both networks should have one hidden layer with ReLU activation in the hidden layer. The generator’s output layer is linear, while the discriminator's output layer uses a sigmoid activation.

You must train the GAN using the standard non-saturating GAN loss for the generator and binary cross-entropy loss for the discriminator. In the NumPy version, parameters should be updated using vanilla gradient descent. In the PyTorch version, parameters should be updated using stochastic gradient descent (SGD) with the specified learning rate. The training loop should alternate between updating the discriminator and the generator each iteration.

Your function must return the trained generator forward function `gen_forward(z)`, which produces generated samples given latent noise.


### example.json

```json
{
  "input": "gen_forward = train_gan(4.0, 1.25, epochs=1000, seed=42)\nz = np.random.normal(0, 1, (500, 1))\nx_gen, _, _ = gen_forward(z)\n(round(np.mean(x_gen), 4), round(np.std(x_gen), 4))",
  "output": "(0.0004, 0.0002)",
  "reasoning": "The test cases call `gen_forward` after training, sample 500 points, and then compute the mean and std."
}
```




### learn.md

## Understanding GANs for 1D Gaussian Data
A Generative Adversarial Network (GAN) consists of two neural networks - a **Generator** $G_\theta$ and a **Discriminator** $D_\phi$ - trained in a minimax game.

### 1. The Roles
- **Generator** $G_\theta(z)$: Takes a latent noise vector $z \sim \mathcal{N}(0, I)$ and outputs a sample intended to resemble the real data.
- **Discriminator** $D_\phi(x)$: Outputs a probability $p \in (0, 1)$ that the input $x$ came from the real data distribution rather than the generator.

### 2. The Objective
The classical GAN objective is:
$$
\min_{\theta} \; \max_{\phi} \; \mathbb{E}_{x \sim p_{\text{data}}} [\log D_\phi(x)] + \mathbb{E}_{z \sim p(z)} [\log (1 - D_\phi(G_\theta(z)))]
$$
Here:
- $p_{\text{data}}$ is the real data distribution.
- $p(z)$ is the prior distribution for the latent noise (often standard normal).

### 3. Practical Losses
In implementation, we minimize:
- **Discriminator loss**:
$$
\mathcal{L}_D = - \left( \frac{1}{m} \sum_{i=1}^m \log D(x^{(i)}_{\text{real}}) + \log(1 - D(x^{(i)}_{\text{fake}})) \right)
$$
- **Generator loss** (non-saturating form):
$$
\mathcal{L}_G = - \frac{1}{m} \sum_{i=1}^m \log D(G(z^{(i)}))
$$

### 4. Forward/Backward Flow
1. **Discriminator step**: Real samples $x_{\text{real}}$ and fake samples $x_{\text{fake}} = G(z)$ are passed through $D$, and $\mathcal{L}_D$ is minimized w.r.t. $\phi$.
2. **Generator step**: Fresh $z$ is sampled, $x_{\text{fake}} = G(z)$ is passed through $D$, and $\mathcal{L}_G$ is minimized w.r.t. $\theta$ while keeping $\phi$ fixed.

### 5. Architecture for This Task
- **Generator**: Fully connected layer ($\mathbb{R}^{\text{latent\_dim}} \to \mathbb{R}^{\text{hidden\_dim}}$) -> ReLU -> Fully connected layer ($\mathbb{R}^{\text{hidden\_dim}} \to \mathbb{R}^1$).
- **Discriminator**: Fully connected layer ($\mathbb{R}^1 \to \mathbb{R}^{\text{hidden\_dim}}$) → ReLU → Fully connected layer ($\mathbb{R}^{\text{hidden\_dim}} \to \mathbb{R}^1$) → Sigmoid.

### 6. Numerical Tips
- Initialize weights with a small Gaussian ($\mathcal{N}(0, 0.01)$).
- Add $10^{-8}$ to logs for numerical stability.
- Use a consistent batch size $m$ for both real and fake samples.
- Always sample fresh noise for the generator on each update.

**Your Task**: Implement the training loop to learn the parameters $\theta$ and $\phi$, and return the trained `gen_forward(z)` function. The evaluation (mean/std of generated samples) will be handled in the test cases.


### meta.json

```json
{
  "id": "174",
  "title": "Train a Simple GAN on 1D Gaussian Data",
  "difficulty": "hard",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "moe"
    }
  ],
  "pytorch_difficulty": "medium"
}
```




### solution.py

```python
import torch
import torch.nn as nn
import torch.optim as optim


def train_gan(
    mean_real: float,
    std_real: float,
    latent_dim: int = 1,
    hidden_dim: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 5000,
    batch_size: int = 128,
    seed: int = 42,
):
    torch.manual_seed(seed)

    class Generator(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, 1)
            )

        def forward(self, z):
            return self.net(z)

    class Discriminator(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(1, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            return self.net(x)

    G = Generator()
    D = Discriminator()

    # Use SGD as requested
    opt_G = optim.SGD(G.parameters(), lr=learning_rate)
    opt_D = optim.SGD(D.parameters(), lr=learning_rate)
    criterion = nn.BCELoss()

    for _ in range(epochs):
        # Real and fake batches
        real_data = torch.normal(mean_real, std_real, size=(batch_size, 1))
        noise = torch.randn(batch_size, latent_dim)
        fake_data = G(noise)

        # ----- Discriminator step -----
        opt_D.zero_grad()
        pred_real = D(real_data)
        pred_fake = D(fake_data.detach())
        loss_real = criterion(pred_real, torch.ones_like(pred_real))
        loss_fake = criterion(pred_fake, torch.zeros_like(pred_fake))
        loss_D = loss_real + loss_fake
        loss_D.backward()
        opt_D.step()

        # ----- Generator step -----
        opt_G.zero_grad()
        pred_fake = D(fake_data)
        # non-saturating generator loss: maximize log D(G(z)) -> minimize -log D(G(z))
        loss_G = criterion(pred_fake, torch.ones_like(pred_fake))
        loss_G.backward()
        opt_G.step()

    return G.forward
```




### starter_code.py

```python
import torch
import torch.nn as nn
import torch.optim as optim


def train_gan(
    mean_real: float,
    std_real: float,
    latent_dim: int = 1,
    hidden_dim: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 5000,
    batch_size: int = 128,
    seed: int = 42,
):
    torch.manual_seed(seed)
    # Your PyTorch implementation here
    pass
```




### tests.json

```json
[
  {
    "test": "gen_forward = train_gan(4.0, 1.25, epochs=100, seed=42)\nz = torch.randn(500, 1)\nx_gen = gen_forward(z)\nprint((round(x_gen.mean().item(), 4), round(x_gen.std().item(), 4)))",
    "expected_output": "(0.4725, 0.3563)"
  },
  {
    "test": "gen_forward = train_gan(0.0, 1.0, epochs=50, seed=0)\nz = torch.randn(300, 1)\nx_gen = gen_forward(z)\nprint((round(x_gen.mean().item(), 4), round(x_gen.std().item(), 4)))",
    "expected_output": "(0.0644, 0.244)"
  }
]
```




### solution.py

```python
import numpy as np


def relu(x):
    return np.maximum(0, x)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def train_gan(
    mean_real: float,
    std_real: float,
    latent_dim: int = 1,
    hidden_dim: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 5000,
    batch_size: int = 128,
    seed: int = 42,
):
    np.random.seed(seed)
    data_dim = 1

    # Initialize generator weights
    w1_g = np.random.normal(0, 0.01, (latent_dim, hidden_dim))
    b1_g = np.zeros(hidden_dim)
    w2_g = np.random.normal(0, 0.01, (hidden_dim, data_dim))
    b2_g = np.zeros(data_dim)

    # Initialize discriminator weights
    w1_d = np.random.normal(0, 0.01, (data_dim, hidden_dim))
    b1_d = np.zeros(hidden_dim)
    w2_d = np.random.normal(0, 0.01, (hidden_dim, 1))
    b2_d = np.zeros(1)

    def disc_forward(x):
        h1 = np.dot(x, w1_d) + b1_d
        a1 = relu(h1)
        logit = np.dot(a1, w2_d) + b2_d
        p = sigmoid(logit)
        return p, logit, a1, h1

    def gen_forward(z):
        h1 = np.dot(z, w1_g) + b1_g
        a1 = relu(h1)
        x_gen = np.dot(a1, w2_g) + b2_g
        return x_gen, a1, h1

    for epoch in range(epochs):
        # Sample real data
        x_real = np.random.normal(mean_real, std_real, batch_size)[:, None]
        z = np.random.normal(0, 1, (batch_size, latent_dim))
        x_fake, _, _ = gen_forward(z)

        # Discriminator forward
        p_real, _, a1_real, h1_real = disc_forward(x_real)
        p_fake, _, a1_fake, h1_fake = disc_forward(x_fake)

        # Discriminator gradients
        grad_logit_real = -(1 - p_real) / batch_size
        grad_a1_real = grad_logit_real @ w2_d.T
        grad_h1_real = grad_a1_real * (h1_real > 0)
        grad_w1_d_real = x_real.T @ grad_h1_real
        grad_b1_d_real = np.sum(grad_h1_real, axis=0)
        grad_w2_d_real = a1_real.T @ grad_logit_real
        grad_b2_d_real = np.sum(grad_logit_real, axis=0)

        grad_logit_fake = p_fake / batch_size
        grad_a1_fake = grad_logit_fake @ w2_d.T
        grad_h1_fake = grad_a1_fake * (h1_fake > 0)
        grad_w1_d_fake = x_fake.T @ grad_h1_fake
        grad_b1_d_fake = np.sum(grad_h1_fake, axis=0)
        grad_w2_d_fake = a1_fake.T @ grad_logit_fake
        grad_b2_d_fake = np.sum(grad_logit_fake, axis=0)

        grad_w1_d = grad_w1_d_real + grad_w1_d_fake
        grad_b1_d = grad_b1_d_real + grad_b1_d_fake
        grad_w2_d = grad_w2_d_real + grad_w2_d_fake
        grad_b2_d = grad_b2_d_real + grad_b2_d_fake

        w1_d -= learning_rate * grad_w1_d
        b1_d -= learning_rate * grad_b1_d
        w2_d -= learning_rate * grad_w2_d
        b2_d -= learning_rate * grad_b2_d

        # Generator update
        z = np.random.normal(0, 1, (batch_size, latent_dim))
        x_fake, a1_g, h1_g = gen_forward(z)
        p_fake, _, a1_d, h1_d = disc_forward(x_fake)

        grad_logit_fake = -(1 - p_fake) / batch_size
        grad_a1_d = grad_logit_fake @ w2_d.T
        grad_h1_d = grad_a1_d * (h1_d > 0)
        grad_x_fake = grad_h1_d @ w1_d.T

        grad_a1_g = grad_x_fake @ w2_g.T
        grad_h1_g = grad_a1_g * (h1_g > 0)
        grad_w1_g = z.T @ grad_h1_g
        grad_b1_g = np.sum(grad_h1_g, axis=0)
        grad_w2_g = a1_g.T @ grad_x_fake
        grad_b2_g = np.sum(grad_x_fake, axis=0)

        w1_g -= learning_rate * grad_w1_g
        b1_g -= learning_rate * grad_b1_g
        w2_g -= learning_rate * grad_w2_g
        b2_g -= learning_rate * grad_b2_g

    return gen_forward
```




### starter_code.py

```python
import numpy as np


def train_gan(
    mean_real: float,
    std_real: float,
    latent_dim: int = 1,
    hidden_dim: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 5000,
    batch_size: int = 128,
    seed: int = 42,
):
    """
    Train a simple GAN to learn a 1D Gaussian distribution.

    Args:
        mean_real: Mean of the target Gaussian
        std_real: Std of the target Gaussian
        latent_dim: Dimension of the noise input to the generator
        hidden_dim: Hidden layer size for both networks
        learning_rate: Learning rate for gradient descent
        epochs: Number of training epochs
        batch_size: Training batch size
        seed: Random seed for reproducibility

    Returns:
        gen_forward: A function that takes z and returns generated samples
    """
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "gen_forward = train_gan(4.0, 1.25, epochs=1000, seed=42)\nz = np.random.normal(0, 1, (500, 1))\nx_gen, _, _ = gen_forward(z)\nprint((round(np.mean(x_gen), 4), round(np.std(x_gen), 4)))",
    "expected_output": "(0.0004, 0.0002)"
  },
  {
    "test": "gen_forward = train_gan(0.0, 1.0, epochs=500, seed=0)\nz = np.random.normal(0, 1, (300, 1))\nx_gen, _, _ = gen_forward(z)\nprint((round(np.mean(x_gen), 4), round(np.std(x_gen), 4)))",
    "expected_output": "(-0.0002, 0.0002)"
  },
  {
    "test": "gen_forward = train_gan(-2.0, 0.5, epochs=1500, seed=123)\nz = np.random.normal(0, 1, (400, 1))\nx_gen, _, _ = gen_forward(z)\nprint((round(np.mean(x_gen), 4), round(np.std(x_gen), 4)))",
    "expected_output": "(-0.0044, 0.0002)"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/174_train-a-simple-gan-on-1d-gaussian-data/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/174_train-a-simple-gan-on-1d-gaussian-data/description.md)。Deep-ML：Educational Use Only License。
