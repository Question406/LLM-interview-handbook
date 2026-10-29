---
id: drustz-14b7838f7fe462d8af
section: deepml
order: 7
level: A
title: Bernoulli Naive Bayes Classifier
quick: Deep-ML 练习 · Bernoulli Naive Bayes Classifier
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/140_bernoulli-naive-bayes-classifier/description.md
    type: primary
---
### description.md

Write a Python class to implement the Bernoulli Naive Bayes classifier for binary (0/1) feature data. Your class should have two methods: `forward(self, X, y)` to train on the input data (X: 2D NumPy array of binary features, y: 1D NumPy array of class labels) and `predict(self, X)` to output predicted labels for a 2D test matrix X. Use Laplace smoothing (parameter: smoothing=1.0). Return predictions as a NumPy array. Only use NumPy. Predictions must be binary (0 or 1) and you must handle cases where the training data contains only one class. All log/likelihood calculations should use log probabilities for numerical stability.


### example.json

```json
{
  "input": "X = np.array([[1, 0, 1], [1, 1, 0], [0, 0, 1], [0, 1, 0], [1, 1, 1]]); y = np.array([1, 1, 0, 0, 1])\nmodel = NaiveBayes(smoothing=1.0)\nmodel.forward(X, y)\nprint(model.predict(np.array([[1, 0, 1]])))",
  "output": "[1]",
  "reasoning": "The model learns class priors and feature probabilities with Laplace smoothing. For [1, 0, 1], the posterior for class 1 is higher, so the model predicts 1."
}
```




### learn.md

# **Naive Bayes Classifier**

## **1. Definition**

Naive Bayes is a **probabilistic machine learning algorithm** used for **classification tasks**. It is based on **Bayes' Theorem**, which describes the probability of an event based on prior knowledge of related events.

The algorithm assumes that:
- **Features are conditionally independent** given the class label (the "naive" assumption).
- It calculates the posterior probability for each class and assigns the class with the **highest posterior** to the sample.

---

## **2. Bayes' Theorem**

Bayes' Theorem is given by:

$$
P(C | X) = \frac{P(X | C) \times P(C)}{P(X)}
$$

Where:
- $P(C | X)$ **Posterior** probability: the probability of class $C $ given the feature vector $X$
- $P(X | C)$ → **Likelihood**: the probability of the data $X$ given the class
- $P(C)$ → **Prior** probability: the initial probability of class $C$ before observing any data
- $ P(X)$ → **Evidence**: the total probability of the data across all classes (acts as a normalizing constant)

Since $P(X)$ is the same for all classes during comparison, it can be ignored, simplifying the formula to:

$$
P(C | X) \propto P(X | C) \times P(C)
$$
---

### 3 **Bernoulli Naive Bayes**
- Used for **binary data** (features take only 0 or 1 values).
- The likelihood is given by:

$$
P(X | C) = \prod_{i=1}^{n} P(x_i | C)^{x_i} \cdot (1 - P(x_i | C))^{1 - x_i}
$$

---

## **4. Applications of Naive Bayes**

- **Text Classification:** Spam detection, sentiment analysis, and news categorization.
- **Document Categorization:** Sorting documents by topic.
- **Fraud Detection:** Identifying fraudulent transactions or behaviors.
- **Recommender Systems:** Classifying users into preference groups.

--- 


### meta.json

```json
{
  "id": "140",
  "title": "Bernoulli Naive Bayes Classifier",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Coder1010ayush",
      "name": "Coder1010ayush"
    }
  ]
}
```




### solution.py

```python
import numpy as np


class NaiveBayes:
    def __init__(self, smoothing=1.0):
        self.smoothing = smoothing
        self.classes = None
        self.priors = None
        self.likelihoods = None

    def forward(self, X, y):
        self.classes, class_counts = np.unique(y, return_counts=True)
        self.priors = {
            cls: np.log(class_counts[i] / len(y)) for i, cls in enumerate(self.classes)
        }
        self.likelihoods = {}
        for cls in self.classes:
            X_cls = X[y == cls]
            prob = (np.sum(X_cls, axis=0) + self.smoothing) / (
                X_cls.shape[0] + 2 * self.smoothing
            )
            self.likelihoods[cls] = (np.log(prob), np.log(1 - prob))

    def _compute_posterior(self, sample):
        posteriors = {}
        for cls in self.classes:
            posterior = self.priors[cls]
            prob_1, prob_0 = self.likelihoods[cls]
            likelihood = np.sum(sample * prob_1 + (1 - sample) * prob_0)
            posterior += likelihood
            posteriors[cls] = posterior
        return max(posteriors, key=posteriors.get)

    def predict(self, X):
        return np.array([self._compute_posterior(sample) for sample in X])
```




### starter_code.py

```python
import numpy as np


class NaiveBayes:
    def __init__(self, smoothing=1.0):
        # Initialize smoothing
        pass

    def forward(self, X, y):
        # Fit model to binary features X and labels y
        pass

    def predict(self, X):
        # Predict class labels for test set X
        pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nmodel = NaiveBayes(smoothing=1.0)\nX = np.array([[1, 0, 1], [1, 1, 0], [0, 0, 1], [0, 1, 0], [1, 1, 1]])\ny = np.array([1, 1, 0, 0, 1])\nmodel.forward(X, y)\nprint(model.predict(np.array([[1, 0, 1]])))",
    "expected_output": "[1]"
  },
  {
    "test": "import numpy as np\nmodel = NaiveBayes(smoothing=1.0)\nX = np.array([[0], [1], [0], [1]])\ny = np.array([0, 1, 0, 1])\nmodel.forward(X, y)\nprint(model.predict(np.array([[0], [1]])))",
    "expected_output": "[0 1]"
  },
  {
    "test": "import numpy as np\nmodel = NaiveBayes(smoothing=1.0)\nX = np.array([[0, 0], [1, 0], [0, 1]])\ny = np.array([0, 1, 0])\nmodel.forward(X, y)\nprint(model.predict(np.array([[1, 1]])))",
    "expected_output": "[0]"
  },
  {
    "test": "import numpy as np\nnp.random.seed(42)\nmodel = NaiveBayes(smoothing=1.0)\nX = np.random.randint(0, 2, (100, 5))\ny = np.random.choice([0, 1], size=100)\nmodel.forward(X, y)\nX_test = np.random.randint(0, 2, (10, 5))\npred = model.predict(X_test)\nprint(pred.shape)",
    "expected_output": "(10,)"
  },
  {
    "test": "import numpy as np\nmodel = NaiveBayes(smoothing=1.0)\nX = np.random.randint(0, 2, (10, 3))\ny = np.zeros(10)\nmodel.forward(X, y)\nX_test = np.random.randint(0, 2, (3, 3))\nprint(model.predict(X_test))",
    "expected_output": "[0, 0, 0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/140_bernoulli-naive-bayes-classifier/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/140_bernoulli-naive-bayes-classifier/description.md)。Deep-ML：Educational Use Only License。
