---
id: drustz-cb74eff4c4cbe4710e
section: deepml
order: 53
level: A
title: Deep-ML 本地仓库说明与构建工具
quick: Deep-ML 练习 · Deep-ML 本地仓库说明与构建工具
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/.github/workflows/format_questions.yml
    type: primary
---
### format_questions.yml

```yaml
name: Build & Validate Question Bundles

on:
  push:
    branches: [main]
    paths:
      - "questions/**"
      - "utils/**"
      - "schemas/**"
      - ".github/workflows/**" # ensure workflow edits retrigger
  pull_request:
    paths:
      - "questions/**"
      - "utils/**"
      - "schemas/**"
      - ".github/workflows/**"

concurrency:
  group: build-validate-${{ github.ref }}
  cancel-in-progress: true

jobs:
  format-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install deps
        run: |
          set -euo pipefail
          python -m pip install --upgrade pip
          python -m pip install "jsonschema>=4.0,<5"

      # ---------- quick sanity: are we running the right validator? ----------
      - name: Debug validator presence and contents
        run: |
          set -euo pipefail
          echo "Commit:"; git log -1 --oneline
          echo "::group::Search for any other validate_questions.py"
          git ls-files | grep -n 'validate_questions.py' || true
          echo "::endgroup::"
          echo "::group::Show utils/validate_questions.py (first 140 lines)"
          nl -ba utils/validate_questions.py | sed -n '1,140p'
          echo "::endgroup::"
          echo "::group::Check for old SCHEMA line"
          if grep -n 'SCHEMA = json.load(open("schemas/question.schema.json"))' -R utils; then
            echo "Found stale validator code; please ensure only the new path-robust version exists." >&2
            exit 1
          else
            echo "No stale SCHEMA loader found. Good."
          fi
          echo "::endgroup::"

      # ---------- validate schema file itself, fail early & print context ----------
      - name: Validate schema JSON strictly (and print with line numbers)
        run: |
          set -euo pipefail
          echo "::group::schemas/question.schema.json (first 120 lines)"
          nl -ba schemas/question.schema.json | sed -n '1,120p' || true
          echo "::endgroup::"
          echo "Checking schema JSON with python -m json.tool..."
          python -m json.tool schemas/question.schema.json >/dev/null
          echo "Schema is valid JSON."

      # ---------- build ----------
      - name: Build bundles into /build
        run: |
          set -euo pipefail
          python utils/build_bundle.py

      # ---------- verify something was built ----------
      - name: Check build outputs exist
        run: |
          set -euo pipefail
          test -d build || { echo "build/ does not exist"; exit 1; }
          ls -l build || true
          shopt -s nullglob
          files=(build/*.json)
          ((${#files[@]})) || { echo "No build/*.json files found"; exit 1; }

      # ---------- validate ----------
      # Let the script default to build/*.json internally (safer than a fragile shell glob).
      - name: Validate bundles
        run: |
          set -euo pipefail
          python utils/validate_questions.py

      # ---------- artifacts for debugging ----------
      - name: Upload artifacts (build + schema + validator)
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: question-bundles-and-schema
          path: |
            build/*.json
            schemas/question.schema.json
            utils/validate_questions.py
```




### LICENSE

```text
Educational Use Only License

Version 1.0, July 2024

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 8 of this document.

   "Licensor" shall mean the individual or entity offering the License.

   "Licensee" shall mean the individual or entity exercising permissions granted by this License.

   "Work" shall mean the questions, problems, software, or material licensed under these terms.

2. Grant of License.

   Subject to the terms and conditions of this License, the Licensor hereby grants the Licensee a worldwide, royalty-free, non-exclusive, non-transferable license to use, reproduce, and distribute the Work for educational purposes only. 

3. Commercial Use.

   a. The Licensee shall not use the Work for any commercial purposes. Commercial purposes include, but are not limited to, selling, leasing, or using the Work in a commercial product or service.

   b. The Licensor retains the exclusive right to use the Work for commercial purposes.

4. Restrictions.

   a. The Licensee may not sublicense, transfer, or distribute the Work except as expressly permitted under this License.

   b. The Licensee may not use the Work as part of any commercial service or product, including but not limited to online platforms like LeetCode, without the explicit permission of the Licensor.

5. Prohibition of Use in Machine Learning Models.

   The Licensee shall not use the Work as training data for large language models (LLMs) or any other machine learning models. This includes but is not limited to using the Work to improve, enhance, or develop machine learning algorithms.

6. Disclaimer of Warranty.

   The Work is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the Licensor be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the Work or the use or other dealings in the Work.

7. Limitation of Liability.

   In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Licensor be liable to Licensee for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work (including but not limited to damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), even if such Licensor has been advised of the possibility of such damages.

8. Acceptance.

   By using, reproducing, or distributing the Work, the Licensee accepts the terms and conditions of this License. Any violation of the terms of this License will automatically terminate the Licensee's rights under this License.
```




### README.md

# Deep-ML Open Problem Bank

A community-maintained collection of machine learning coding challenges.  
Each problem lives in its own folder (`questions/<id>_<slug>/`) so contributors can edit Markdown, Python, and JSON files naturally.  
A build script assembles everything into a single JSON file used by [deep-ml.com](https://deep-ml.com).

---

## 📁 Repository Layout

```text
.
├─ questions/
│  ├─ _template/                ← Copy this to start a new problem
│  ├─ 101_grpo_objective/
│  │   ├─ meta.json
│  │   ├─ description.md
│  │   ├─ learn.md
│  │   ├─ starter_code.py
│  │   ├─ solution.py
│  │   ├─ example.json
│  │   ├─ tests.json
│  │   ├─ tinygrad/
│  │   │   ├─ starter_code.py
│  │   │   ├─ solution.py
│  │   │   └─ tests.json
│  │   └─ pytorch/
│  │       ├─ starter_code.py
│  │       ├─ solution.py
│  │       └─ tests.json
│  └─ ...
│
├─ schemas/
│  └─ question.schema.json     ← JSON-Schema used for validation
│
├─ utils/
│  ├─ build_bundle.py          ← folder → build/*.json bundler
│  ├─ validate_questions.py    ← schema validator
│  └─ make_question_template.py← template folder generator
│
└─ .github/workflows/
   └─ format_questions.yml     ← GitHub Action: validate on PR/push
```



---

## 🛠️ Adding a New Question

1. **Copy the template**

```bash
cp -r questions/_template questions/123_my_problem
```



2. **Fill in the fields**

- `meta.json`: question ID, title, category, difficulty, etc.
- `description.md`: problem statement
- `learn.md`: explanation and background
- `starter_code.py`, `solution.py`: reference implementation
- `example.json`: input/output + reasoning
- `tests.json`: list of `{ "test": "...", "expected_output": "..." }`
- Optional language support under `tinygrad/` and `pytorch/`

3. **Run local validation**

```bash
python utils/build_bundle.py && python utils/validate_questions.py
```



4. **Open a Pull Request**

CI will build and validate your changes automatically.

---

## 🧪 Schema Validation

The schema ensures:

- Required fields are present
- Optional `tinygrad_*`, `pytorch_*` are allowed
- No invalid or extra fields

Each question must pass validation before it can be merged.

---

## 🤖 GitHub Actions

Located in `.github/workflows/format_questions.yml`, this runs:

1. `build_bundle.py` – compiles all question folders
2. `validate_questions.py` – checks for schema and structure errors

CI fails if anything is invalid.

---

## 📜 License

All problems are for **educational use only**.  
See `LICENSE` file for full terms. 

---

## 🙋 Need Help?

Open an issue or visit our Discord: [来源链接](https://discord.gg/JwMePfMZAV)

### Note: 
for current PRs I will still work on making the other parts of the problem like i did before but it would be faster if you added the needed info


### folder_list.txt

```text
.git
.github
example_problem
Problems
__pycache__
```




### json_to_files.py

```python

```




### problems_folder_list.txt

```text
100_Softsign
102_Swish
103_SELU
104_logistic_regression
105_train_softmaxreg
106_train_logreg
107_masked_attention
10_Calculate_cov_matrix
110_METEOR
111_PMI
112_cross_entropy_loss
113_early_stopping
11_Linear_equations_jacobi
12_svd_2x2_singular_values
13_determinant_4x4
14_linear_regression_normal_equation
15_linear_regression_gradient_descent
16_feature_scaling
17_k_means_clustering
18_cross_validation_split
19_PCA
1_matrix_times_vector
20_decision_tree_learning
21_pegasos_kernel_svm
22_sigmoid
23_softmax
24_single_neuron
25_Single_Neuron_with_Backpropagation
26_Autograd
28_svd_2x2_eign
2_transpose_matrix
32_polynomial_features
33_random_subsets
35 - Vector to Matrix
39_log_softmax
3_reshape_matrix
41_simple_conv2d_layer
42_relu_activation_function
43_ridge_loss
44_leaky_relu
45_linear_kernel
46_precision
47_gradient_descent
48_rref
4_calculate_mean_by_row_or_column
50_lasso_regression_gradient_descent
51_OSA_distance
52_recall
53_self_attention
54_RNN_layer
55_2D_translation_matrix
57_gauss_seidel
58_gaussian_elimination_partial_pivoting
5_scalar_multiplication_of_a_matrix
60_TF-IDF
61_f_score
63_conjugate_gradient
64_gini_impurity
65_compressed_row_sparse_matrix
66_orthogonal_projection
67_compressed_column_sparse_matrix
69_r-squared
6_calculate_eigenvalues
70_image_brightness_calculator
71_Room_Mean_Square_Error
73_Dice_Score
74_hdc_bundling_binding
75_classification_performance_metrics
76_Cosine_Similarity
77_classification_performance_metrics
78_binomial_distribution
78_descriptive_stats
7_transform_matrix
80_normal_distribution
81_poisson_distribution
82_image_basic_contrast_calculator
83_vector_dot_product
84_phi_transformation
85_Positional_encoding
86_overfitting_underfitting
87_adam_optimizer
88_GPT_2
8_Calculate_2x2_Matrix_Inverse
94_multi_head_attention
95_phi_correlation_coefficient
96_Hard_Sigmoid
97_ELU
98_PReLU
99_Softplus
9_matrixmul
BM25
interactive_learn
MAE
```




### requirements.txt

```text
altair==5.2.0
attrs==23.2.0
blinker==1.7.0
cachetools==5.3.3
certifi==2024.2.2
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
gitdb==4.0.11
GitPython==3.1.42
idna==3.6
Jinja2==3.1.3
jsonschema==4.21.1
jsonschema-specifications==2023.12.1
markdown-it-py==3.0.0
MarkupSafe==2.1.5
mdurl==0.1.2
numpy==1.26.4
packaging==23.2
pandas==2.2.1
pillow==10.2.0
pistonpy==0.0.3
protobuf==4.25.3
pyarrow==15.0.1
pydeck==0.8.1b0
Pygments==2.17.2
python-dateutil==2.9.0.post0
pytz==2024.1
referencing==0.33.0
requests==2.31.0
rich==13.7.1
rpds-py==0.18.0
setuptools==68.2.2
six==1.16.0
smmap==5.0.1
streamlit==1.32.2
streamlit-ace==0.1.1
tenacity==8.2.3
toml==0.10.2
toolz==0.12.1
tornado==6.4
typing==3.7.4.3
typing_extensions==4.10.0
tzdata==2024.1
urllib3==2.2.1
watchdog==4.0.0
wheel==0.41.2
```




### build_bundle.py

```python
#!/usr/bin/env python
"""
Walk questions/* folders → emit build/<id>.json bundles.
"""

import json, pathlib, re

ROOT = pathlib.Path("questions")
OUTDIR = pathlib.Path("build")
OUTDIR.mkdir(exist_ok=True)


def load_text(p):
    return p.read_text(encoding="utf-8").rstrip("\n")


def load_json(p):
    return json.loads(load_text(p))


def bundle_one(folder: pathlib.Path):
    meta = load_json(folder / "meta.json")

    meta["description"] = load_text(folder / "description.md")
    meta["learn_section"] = load_text(folder / "learn.md")
    meta["starter_code"] = load_text(folder / "starter_code.py")
    meta["solution"] = load_text(folder / "solution.py")
    meta["example"] = load_json(folder / "example.json")
    meta["test_cases"] = load_json(folder / "tests.json")

    if "marimo_link" in meta:
        meta["marimo_link"] = meta["marimo_link"]

    for lang in ("tinygrad", "pytorch"):
        sub = folder / lang
        if sub.exists():
            if (sub / "starter_code.py").exists():
                meta[f"{lang}_starter_code"] = load_text(sub / "starter_code.py")
            if (sub / "solution.py").exists():
                meta[f"{lang}_solution"] = load_text(sub / "solution.py")
            if (sub / "tests.json").exists():
                meta[f"{lang}_test_cases"] = load_json(sub / "tests.json")

    out_path = OUTDIR / f"{meta['id']}.json"
    out_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"✓ bundled {out_path.name}")


def main():
    for qdir in sorted(
        p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('_')
    ):
        bundle_one(qdir)


if __name__ == "__main__":
    main()
```




### convert_single_question.py

```python
#!/usr/bin/env python
"""
convert_single_question.py
──────────────────────────
Paste ONE question dict into QUESTION_DICT and run:

    python utils/convert_single_question.py

The script splits it into:

questions/<id>_<slug>/
    ├─ meta.json
    ├─ description.md
    ├─ learn.md
    ├─ starter_code.py
    ├─ solution.py
    ├─ example.json
    ├─ tests.json
    ├─ tinygrad/   (optional)
    └─ pytorch/    (optional)
"""

import base64
import json
import pathlib
import re
from typing import Any, Dict

# ── 1️⃣  EDIT YOUR QUESTION HERE ────────────────────────────────────────────
QUESTION_DICT: Dict[str, Any] = {
    "description": "In this task, you will train a Generative Adversarial Network (GAN) to learn a one-dimensional Gaussian distribution. The GAN consists of a generator that produces samples from latent noise and a discriminator that estimates the probability that a given sample is real. Both networks should have one hidden layer with ReLU activation in the hidden layer. The generator’s output layer is linear, while the discriminator's output layer uses a sigmoid activation.\n\nYou must train the GAN using the standard non-saturating GAN loss for the generator and binary cross-entropy loss for the discriminator. In the NumPy version, parameters should be updated using vanilla gradient descent. In the PyTorch version, parameters should be updated using stochastic gradient descent (SGD) with the specified learning rate. The training loop should alternate between updating the discriminator and the generator each iteration.\n\nYour function must return the trained generator forward function `gen_forward(z)`, which produces generated samples given latent noise.",
    "id": "174",
    "test_cases": [
        {
            "test": "gen_forward = train_gan(4.0, 1.25, epochs=1000, seed=42)\nz = np.random.normal(0, 1, (500, 1))\nx_gen, _, _ = gen_forward(z)\nprint((round(np.mean(x_gen), 4), round(np.std(x_gen), 4)))",
            "expected_output": "(0.0004, 0.0002)",
        },
        {
            "test": "gen_forward = train_gan(0.0, 1.0, epochs=500, seed=0)\nz = np.random.normal(0, 1, (300, 1))\nx_gen, _, _ = gen_forward(z)\nprint((round(np.mean(x_gen), 4), round(np.std(x_gen), 4)))",
            "expected_output": "(-0.0002, 0.0002)",
        },
        {
            "test": "gen_forward = train_gan(-2.0, 0.5, epochs=1500, seed=123)\nz = np.random.normal(0, 1, (400, 1))\nx_gen, _, _ = gen_forward(z)\nprint((round(np.mean(x_gen), 4), round(np.std(x_gen), 4)))",
            "expected_output": "(-0.0044, 0.0002)",
        },
    ],
    "solution": "import numpy as np\n\ndef relu(x):\n    return np.maximum(0, x)\n\ndef sigmoid(x):\n    return 1 / (1 + np.exp(-x))\n\ndef train_gan(mean_real: float, std_real: float, latent_dim: int = 1, hidden_dim: int = 16, learning_rate: float = 0.001, epochs: int = 5000, batch_size: int = 128, seed: int = 42):\n    np.random.seed(seed)\n    data_dim = 1\n\n    # Initialize generator weights\n    w1_g = np.random.normal(0, 0.01, (latent_dim, hidden_dim))\n    b1_g = np.zeros(hidden_dim)\n    w2_g = np.random.normal(0, 0.01, (hidden_dim, data_dim))\n    b2_g = np.zeros(data_dim)\n\n    # Initialize discriminator weights\n    w1_d = np.random.normal(0, 0.01, (data_dim, hidden_dim))\n    b1_d = np.zeros(hidden_dim)\n    w2_d = np.random.normal(0, 0.01, (hidden_dim, 1))\n    b2_d = np.zeros(1)\n\n    def disc_forward(x):\n        h1 = np.dot(x, w1_d) + b1_d\n        a1 = relu(h1)\n        logit = np.dot(a1, w2_d) + b2_d\n        p = sigmoid(logit)\n        return p, logit, a1, h1\n\n    def gen_forward(z):\n        h1 = np.dot(z, w1_g) + b1_g\n        a1 = relu(h1)\n        x_gen = np.dot(a1, w2_g) + b2_g\n        return x_gen, a1, h1\n\n    for epoch in range(epochs):\n        # Sample real data\n        x_real = np.random.normal(mean_real, std_real, batch_size)[:, None]\n        z = np.random.normal(0, 1, (batch_size, latent_dim))\n        x_fake, _, _ = gen_forward(z)\n\n        # Discriminator forward\n        p_real, _, a1_real, h1_real = disc_forward(x_real)\n        p_fake, _, a1_fake, h1_fake = disc_forward(x_fake)\n\n        # Discriminator gradients\n        grad_logit_real = - (1 - p_real) / batch_size\n        grad_a1_real = grad_logit_real @ w2_d.T\n        grad_h1_real = grad_a1_real * (h1_real > 0)\n        grad_w1_d_real = x_real.T @ grad_h1_real\n        grad_b1_d_real = np.sum(grad_h1_real, axis=0)\n        grad_w2_d_real = a1_real.T @ grad_logit_real\n        grad_b2_d_real = np.sum(grad_logit_real, axis=0)\n\n        grad_logit_fake = p_fake / batch_size\n        grad_a1_fake = grad_logit_fake @ w2_d.T\n        grad_h1_fake = grad_a1_fake * (h1_fake > 0)\n        grad_w1_d_fake = x_fake.T @ grad_h1_fake\n        grad_b1_d_fake = np.sum(grad_h1_fake, axis=0)\n        grad_w2_d_fake = a1_fake.T @ grad_logit_fake\n        grad_b2_d_fake = np.sum(grad_logit_fake, axis=0)\n\n        grad_w1_d = grad_w1_d_real + grad_w1_d_fake\n        grad_b1_d = grad_b1_d_real + grad_b1_d_fake\n        grad_w2_d = grad_w2_d_real + grad_w2_d_fake\n        grad_b2_d = grad_b2_d_real + grad_b2_d_fake\n\n        w1_d -= learning_rate * grad_w1_d\n        b1_d -= learning_rate * grad_b1_d\n        w2_d -= learning_rate * grad_w2_d\n        b2_d -= learning_rate * grad_b2_d\n\n        # Generator update\n        z = np.random.normal(0, 1, (batch_size, latent_dim))\n        x_fake, a1_g, h1_g = gen_forward(z)\n        p_fake, _, a1_d, h1_d = disc_forward(x_fake)\n\n        grad_logit_fake = - (1 - p_fake) / batch_size\n        grad_a1_d = grad_logit_fake @ w2_d.T\n        grad_h1_d = grad_a1_d * (h1_d > 0)\n        grad_x_fake = grad_h1_d @ w1_d.T\n\n        grad_a1_g = grad_x_fake @ w2_g.T\n        grad_h1_g = grad_a1_g * (h1_g > 0)\n        grad_w1_g = z.T @ grad_h1_g\n        grad_b1_g = np.sum(grad_h1_g, axis=0)\n        grad_w2_g = a1_g.T @ grad_x_fake\n        grad_b2_g = np.sum(grad_x_fake, axis=0)\n\n        w1_g -= learning_rate * grad_w1_g\n        b1_g -= learning_rate * grad_b1_g\n        w2_g -= learning_rate * grad_w2_g\n        b2_g -= learning_rate * grad_b2_g\n\n    return gen_forward",
    "difficulty": "hard",
    "pytorch_difficulty": "medium",
    "video": "",
    "likes": "0",
    "dislikes": "0",
    "example": {
        "input": "gen_forward = train_gan(4.0, 1.25, epochs=1000, seed=42)\nz = np.random.normal(0, 1, (500, 1))\nx_gen, _, _ = gen_forward(z)\n(round(np.mean(x_gen), 4), round(np.std(x_gen), 4))",
        "output": "(0.0004, 0.0002)",
        "reasoning": "The test cases call `gen_forward` after training, sample 500 points, and then compute the mean and std.",
    },
    "category": "Deep Learning",
    "pytorch_starter_code": "aW1wb3J0IHRvcmNoCmltcG9ydCB0b3JjaC5ubiBhcyBubgppbXBvcnQgdG9yY2gub3B0aW0gYXMgb3B0aW0KCmRlZiB0cmFpbl9nYW4obWVhbl9yZWFsOiBmbG9hdCwgc3RkX3JlYWw6IGZsb2F0LCBsYXRlbnRfZGltOiBpbnQgPSAxLCBoaWRkZW5fZGltOiBpbnQgPSAxNiwgbGVhcm5pbmdfcmF0ZTogZmxvYXQgPSAwLjAwMSwgZXBvY2hzOiBpbnQgPSA1MDAwLCBiYXRjaF9zaXplOiBpbnQgPSAxMjgsIHNlZWQ6IGludCA9IDQyKToKICAgIHRvcmNoLm1hbnVhbF9zZWVkKHNlZWQpCiAgICAjIFlvdXIgUHlUb3JjaCBpbXBsZW1lbnRhdGlvbiBoZXJlCiAgICBwYXNz",
    "title": "Train a Simple GAN on 1D Gaussian Data",
    "createdAt": "August 13, 2025 at 11:01:53 AM UTUTC-4",
    "contributor": [{"profile_link": "https://github.com/moe18", "name": "moe"}],
    "pytorch_test_cases": [
        {
            "test": "gen_forward = train_gan(4.0, 1.25, epochs=100, seed=42)\nz = torch.randn(500, 1)\nx_gen = gen_forward(z)\nprint((round(x_gen.mean().item(), 4), round(x_gen.std().item(), 4)))",
            "expected_output": "(0.4725, 0.3563)",
        },
        {
            "test": "gen_forward = train_gan(0.0, 1.0, epochs=50, seed=0)\nz = torch.randn(300, 1)\nx_gen = gen_forward(z)\nprint((round(x_gen.mean().item(), 4), round(x_gen.std().item(), 4)))",
            "expected_output": "(0.0644, 0.244)",
        },
    ],
    "learn_section": "## Understanding GANs for 1D Gaussian Data\nA Generative Adversarial Network (GAN) consists of two neural networks - a **Generator** $G_\\theta$ and a **Discriminator** $D_\\phi$ - trained in a minimax game.\n\n### 1. The Roles\n- **Generator** $G_\\theta(z)$: Takes a latent noise vector $z \\sim \\mathcal{N}(0, I)$ and outputs a sample intended to resemble the real data.\n- **Discriminator** $D_\\phi(x)$: Outputs a probability $p \\in (0, 1)$ that the input $x$ came from the real data distribution rather than the generator.\n\n### 2. The Objective\nThe classical GAN objective is:\n$$\n\\min_{\\theta} \\; \\max_{\\phi} \\; \\mathbb{E}_{x \\sim p_{\\text{data}}} [\\log D_\\phi(x)] + \\mathbb{E}_{z \\sim p(z)} [\\log (1 - D_\\phi(G_\\theta(z)))]\n$$\nHere:\n- $p_{\\text{data}}$ is the real data distribution.\n- $p(z)$ is the prior distribution for the latent noise (often standard normal).\n\n### 3. Practical Losses\nIn implementation, we minimize:\n- **Discriminator loss**:\n$$\n\\mathcal{L}_D = - \\left( \\frac{1}{m} \\sum_{i=1}^m \\log D(x^{(i)}_{\\text{real}}) + \\log(1 - D(x^{(i)}_{\\text{fake}})) \\right)\n$$\n- **Generator loss** (non-saturating form):\n$$\n\\mathcal{L}_G = - \\frac{1}{m} \\sum_{i=1}^m \\log D(G(z^{(i)}))\n$$\n\n### 4. Forward/Backward Flow\n1. **Discriminator step**: Real samples $x_{\\text{real}}$ and fake samples $x_{\\text{fake}} = G(z)$ are passed through $D$, and $\\mathcal{L}_D$ is minimized w.r.t. $\\phi$.\n2. **Generator step**: Fresh $z$ is sampled, $x_{\\text{fake}} = G(z)$ is passed through $D$, and $\\mathcal{L}_G$ is minimized w.r.t. $\\theta$ while keeping $\\phi$ fixed.\n\n### 5. Architecture for This Task\n- **Generator**: Fully connected layer ($\\mathbb{R}^{\\text{latent\\_dim}} \\to \\mathbb{R}^{\\text{hidden\\_dim}}$) -> ReLU -> Fully connected layer ($\\mathbb{R}^{\\text{hidden\\_dim}} \\to \\mathbb{R}^1$).\n- **Discriminator**: Fully connected layer ($\\mathbb{R}^1 \\to \\mathbb{R}^{\\text{hidden\\_dim}}$) → ReLU → Fully connected layer ($\\mathbb{R}^{\\text{hidden\\_dim}} \\to \\mathbb{R}^1$) → Sigmoid.\n\n### 6. Numerical Tips\n- Initialize weights with a small Gaussian ($\\mathcal{N}(0, 0.01)$).\n- Add $10^{-8}$ to logs for numerical stability.\n- Use a consistent batch size $m$ for both real and fake samples.\n- Always sample fresh noise for the generator on each update.\n\n**Your Task**: Implement the training loop to learn the parameters $\\theta$ and $\\phi$, and return the trained `gen_forward(z)` function. The evaluation (mean/std of generated samples) will be handled in the test cases.",
    "pytorch_solution": "aW1wb3J0IHRvcmNoCmltcG9ydCB0b3JjaC5ubiBhcyBubgppbXBvcnQgdG9yY2gub3B0aW0gYXMgb3B0aW0KCmRlZiB0cmFpbl9nYW4obWVhbl9yZWFsOiBmbG9hdCwgc3RkX3JlYWw6IGZsb2F0LCBsYXRlbnRfZGltOiBpbnQgPSAxLCBoaWRkZW5fZGltOiBpbnQgPSAxNiwgbGVhcm5pbmdfcmF0ZTogZmxvYXQgPSAwLjAwMSwgZXBvY2hzOiBpbnQgPSA1MDAwLCBiYXRjaF9zaXplOiBpbnQgPSAxMjgsIHNlZWQ6IGludCA9IDQyKToKICAgIHRvcmNoLm1hbnVhbF9zZWVkKHNlZWQpCgogICAgY2xhc3MgR2VuZXJhdG9yKG5uLk1vZHVsZSk6CiAgICAgICAgZGVmIF9faW5pdF9fKHNlbGYpOgogICAgICAgICAgICBzdXBlcigpLl9faW5pdF9fKCkKICAgICAgICAgICAgc2VsZi5uZXQgPSBubi5TZXF1ZW50aWFsKAogICAgICAgICAgICAgICAgbm4uTGluZWFyKGxhdGVudF9kaW0sIGhpZGRlbl9kaW0pLAogICAgICAgICAgICAgICAgbm4uUmVMVSgpLAogICAgICAgICAgICAgICAgbm4uTGluZWFyKGhpZGRlbl9kaW0sIDEpCiAgICAgICAgICAgICkKICAgICAgICBkZWYgZm9yd2FyZChzZWxmLCB6KToKICAgICAgICAgICAgcmV0dXJuIHNlbGYubmV0KHopCgogICAgY2xhc3MgRGlzY3JpbWluYXRvcihubi5Nb2R1bGUpOgogICAgICAgIGRlZiBfX2luaXRfXyhzZWxmKToKICAgICAgICAgICAgc3VwZXIoKS5fX2luaXRfXygpCiAgICAgICAgICAgIHNlbGYubmV0ID0gbm4uU2VxdWVudGlhbCgKICAgICAgICAgICAgICAgIG5uLkxpbmVhcigxLCBoaWRkZW5fZGltKSwKICAgICAgICAgICAgICAgIG5uLlJlTFUoKSwKICAgICAgICAgICAgICAgIG5uLkxpbmVhcihoaWRkZW5fZGltLCAxKSwKICAgICAgICAgICAgICAgIG5uLlNpZ21vaWQoKQogICAgICAgICAgICApCiAgICAgICAgZGVmIGZvcndhcmQoc2VsZiwgeCk6CiAgICAgICAgICAgIHJldHVybiBzZWxmLm5ldCh4KQoKICAgIEcgPSBHZW5lcmF0b3IoKQogICAgRCA9IERpc2NyaW1pbmF0b3IoKQoKICAgICMgVXNlIFNHRCBhcyByZXF1ZXN0ZWQKICAgIG9wdF9HID0gb3B0aW0uU0dEKEcucGFyYW1ldGVycygpLCBscj1sZWFybmluZ19yYXRlKQogICAgb3B0X0QgPSBvcHRpbS5TR0QoRC5wYXJhbWV0ZXJzKCksIGxyPWxlYXJuaW5nX3JhdGUpCiAgICBjcml0ZXJpb24gPSBubi5CQ0VMb3NzKCkKCiAgICBmb3IgXyBpbiByYW5nZShlcG9jaHMpOgogICAgICAgICMgUmVhbCBhbmQgZmFrZSBiYXRjaGVzCiAgICAgICAgcmVhbF9kYXRhID0gdG9yY2gubm9ybWFsKG1lYW5fcmVhbCwgc3RkX3JlYWwsIHNpemU9KGJhdGNoX3NpemUsIDEpKQogICAgICAgIG5vaXNlID0gdG9yY2gucmFuZG4oYmF0Y2hfc2l6ZSwgbGF0ZW50X2RpbSkKICAgICAgICBmYWtlX2RhdGEgPSBHKG5vaXNlKQoKICAgICAgICAjIC0tLS0tIERpc2NyaW1pbmF0b3Igc3RlcCAtLS0tLQogICAgICAgIG9wdF9ELnplcm9fZ3JhZCgpCiAgICAgICAgcHJlZF9yZWFsID0gRChyZWFsX2RhdGEpCiAgICAgICAgcHJlZF9mYWtlID0gRChmYWtlX2RhdGEuZGV0YWNoKCkpCiAgICAgICAgbG9zc19yZWFsID0gY3JpdGVyaW9uKHByZWRfcmVhbCwgdG9yY2gub25lc19saWtlKHByZWRfcmVhbCkpCiAgICAgICAgbG9zc19mYWtlID0gY3JpdGVyaW9uKHByZWRfZmFrZSwgdG9yY2guemVyb3NfbGlrZShwcmVkX2Zha2UpKQogICAgICAgIGxvc3NfRCA9IGxvc3NfcmVhbCArIGxvc3NfZmFrZQogICAgICAgIGxvc3NfRC5iYWNrd2FyZCgpCiAgICAgICAgb3B0X0Quc3RlcCgpCgogICAgICAgICMgLS0tLS0gR2VuZXJhdG9yIHN0ZXAgLS0tLS0KICAgICAgICBvcHRfRy56ZXJvX2dyYWQoKQogICAgICAgIHByZWRfZmFrZSA9IEQoZmFrZV9kYXRhKQogICAgICAgICMgbm9uLXNhdHVyYXRpbmcgZ2VuZXJhdG9yIGxvc3M6IG1heGltaXplIGxvZyBEKEcoeikpIC0+IG1pbmltaXplIC1sb2cgRChHKHopKQogICAgICAgIGxvc3NfRyA9IGNyaXRlcmlvbihwcmVkX2Zha2UsIHRvcmNoLm9uZXNfbGlrZShwcmVkX2Zha2UpKQogICAgICAgIGxvc3NfRy5iYWNrd2FyZCgpCiAgICAgICAgb3B0X0cuc3RlcCgpCgogICAgcmV0dXJuIEcuZm9yd2FyZA==",
    "starter_code": "import numpy as np\n\ndef train_gan(mean_real: float, std_real: float, latent_dim: int = 1, hidden_dim: int = 16, learning_rate: float = 0.001, epochs: int = 5000, batch_size: int = 128, seed: int = 42):\n    \"\"\"\n    Train a simple GAN to learn a 1D Gaussian distribution.\n\n    Args:\n        mean_real: Mean of the target Gaussian\n        std_real: Std of the target Gaussian\n        latent_dim: Dimension of the noise input to the generator\n        hidden_dim: Hidden layer size for both networks\n        learning_rate: Learning rate for gradient descent\n        epochs: Number of training epochs\n        batch_size: Training batch size\n        seed: Random seed for reproducibility\n\n    Returns:\n        gen_forward: A function that takes z and returns generated samples\n    \"\"\"\n    # Your code here\n    pass",
}


# ────────────────────────────────────────────────────────────────────────────


# ---------- helpers ---------------------------------------------------------
def slugify(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-z]+", "-", text.lower())
    return re.sub(r"-{2,}", "-", text).strip("-")[:50]


def maybe_b64(s: str) -> str:
    try:
        if len(s) % 4 == 0 and re.fullmatch(r"[0-9A-Za-z+/=\n\r]+", s):
            return base64.b64decode(s).decode("utf-8")
    except Exception:
        pass
    return s


def write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")


def write_json(path: pathlib.Path, obj: Any) -> None:
    write_text(path, json.dumps(obj, indent=2, ensure_ascii=False))


# ---------- converter -------------------------------------------------------
def convert_one(q: Dict[str, Any]) -> None:
    folder = pathlib.Path("questions") / f"{q['id']}_{slugify(q['title'])}"
    folder.mkdir(parents=True, exist_ok=True)

    # meta.json
    meta = {
        "id": q["id"],
        "title": q["title"],
        "difficulty": q["difficulty"],
        "category": q["category"],
        "video": q.get("video", ""),
        "likes": q.get("likes", "0"),
        "dislikes": q.get("dislikes", "0"),
        "contributor": q.get("contributor", []),
    }
    for opt in ("tinygrad_difficulty", "pytorch_difficulty", "marimo_link"):
        if opt in q:
            meta[opt] = q[opt]
    write_json(folder / "meta.json", meta)

    # core files
    write_text(folder / "description.md", q["description"])
    write_text(folder / "learn.md", q["learn_section"])
    write_text(folder / "starter_code.py", q["starter_code"])
    write_text(folder / "solution.py", q["solution"])
    write_json(folder / "example.json", q["example"])
    write_json(folder / "tests.json", q["test_cases"])

    # optional language-specific extras
    for lang in ("tinygrad", "pytorch"):
        sc, so, tc = (f"{lang}_starter_code", f"{lang}_solution", f"{lang}_test_cases")
        if any(k in q for k in (sc, so, tc)):
            sub = folder / lang
            if sc in q:
                write_text(sub / "starter_code.py", maybe_b64(q[sc]))
            if so in q:
                write_text(sub / "solution.py", maybe_b64(q[so]))
            if tc in q:
                write_json(sub / "tests.json", q[tc])

    # success message (relative if possible)
    try:
        rel = folder.relative_to(pathlib.Path.cwd())
    except ValueError:
        rel = folder
    print(f"✓  Created {rel}")


# ---------- main ------------------------------------------------------------
def main() -> None:
    convert_one(QUESTION_DICT)


if __name__ == "__main__":
    main()
```




### make_question_template.py

```python
#!/usr/bin/env python
import json, pathlib, textwrap

TEMPLATE = pathlib.Path("questions/_template")
LANGS = ["tinygrad", "pytorch"]


def w(path, txt):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(txt.rstrip() + "\n")


def main():
    META = {
        "id": "XXX",
        "title": "TITLE GOES HERE",
        "difficulty": "medium",
        "category": "Machine Learning",
        "video": "",
        "likes": "0",
        "dislikes": "0",
        "contributor": [],
        "tinygrad_difficulty": "",
        "pytorch_difficulty": "",
    }
    w(TEMPLATE / "meta.json", json.dumps(META, indent=2))
    w(TEMPLATE / "description.md", "## Problem\n\nDescribe the task.")
    w(TEMPLATE / "learn.md", "## Solution Explanation\n\nExplain here.")
    w(TEMPLATE / "starter_code.py", "def your_function(...):\n    pass")
    w(TEMPLATE / "solution.py", "def your_function(...):\n    ...")
    w(
        TEMPLATE / "example.json",
        json.dumps({"input": "...", "output": "...", "reasoning": "..."}, indent=2),
    )
    w(
        TEMPLATE / "tests.json",
        json.dumps(
            [{"test": "print(your_function(...))", "expected_output": "..."}], indent=2
        ),
    )
    for lang in LANGS:
        sub = TEMPLATE / lang
        w(sub / "starter_code.py", "def your_function(...):\n    pass")
        w(sub / "solution.py", "def your_function(...):\n    ...")
        w(
            sub / "tests.json",
            json.dumps(
                [{"test": "print(your_function(...))", "expected_output": "..."}],
                indent=2,
            ),
        )
    print("Template ready at questions/_template/")


if __name__ == "__main__":
    main()
```




### validate_questions.py

```python
#!/usr/bin/env python
"""
Validate build/*.json (or files passed on the CLI) against schemas/question.schema.json
"""

import json
import pathlib
import sys
from json.decoder import JSONDecodeError
from jsonschema import Draft7Validator, exceptions as js_exceptions

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA_PATH = (HERE / ".." / "schemas" / "question.schema.json").resolve()


def load_json_strict(path: pathlib.Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except JSONDecodeError as e:
        # Helpful context around the error location
        text = path.read_text(encoding="utf-8", errors="replace")
        start = max(e.pos - 60, 0)
        end = min(e.pos + 60, len(text))
        snippet = text[start:end]
        pointer = " " * (e.pos - start) + "^"
        print(
            f"\n❌ JSON parse error in {path} @ line {e.lineno}, col {e.colno}: {e.msg}"
        )
        print("   Context:")
        print(snippet)
        print(pointer)
        raise


def load_schema():
    if not SCHEMA_PATH.exists():
        print(f"❌ Schema not found at {SCHEMA_PATH}")
        sys.exit(1)
    schema = load_json_strict(SCHEMA_PATH)
    try:
        Draft7Validator.check_schema(schema)
    except js_exceptions.SchemaError as se:
        print("❌ The schema file is not a valid Draft-07 JSON Schema.")
        print("   ", se.message)
        sys.exit(1)
    return schema


def validate_file(validator: Draft7Validator, fp: pathlib.Path) -> bool:
    try:
        data = load_json_strict(fp)
    except JSONDecodeError:
        print(f"   (Could not parse {fp.name} as JSON.)")
        return False

    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        print(f"❌ {fp.name}")
        for e in errors:
            path = "/".join(map(str, e.path)) or "(root)"
            print("   •", path, "-", e.message)
        return False
    else:
        print(f"✓ {fp.name}")
        return True


def main():
    schema = load_schema()
    validator = Draft7Validator(schema)

    # Files passed on CLI? Use those. Otherwise default to build/*.json
    args = [pathlib.Path(a) for a in sys.argv[1:]]
    if args:
        files = []
        for a in args:
            if a.is_dir():
                files.extend(sorted(a.glob("*.json")))
            else:
                files.append(a)
    else:
        files = sorted((HERE / ".." / "build").resolve().glob("*.json"))

    if not files:
        print("No JSON files found to validate.")
        sys.exit(0)

    ok = True
    for fp in files:
        ok = validate_file(validator, fp) and ok

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/.github/workflows/format_questions.yml](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/.github/workflows/format_questions.yml)。Deep-ML：Educational Use Only License。
