---
id: drustz-1edbf87af537a94e1f
section: deepml
order: 86
level: A
title: Implement AdaBoost Fit Method
quick: Deep-ML 练习 · Implement AdaBoost Fit Method
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/38_implement-adaboost-fit-method/description.md
    type: primary
---
### description.md

Write a Python function `adaboost_fit` that implements the fit method for an AdaBoost classifier. The function should take in a 2D numpy array `X` of shape `(n_samples, n_features)` representing the dataset, a 1D numpy array `y` of shape `(n_samples,)` representing the labels, and an integer `n_clf` representing the number of classifiers. The function should initialize sample weights, find the best thresholds for each feature, calculate the error, update weights, and return a list of classifiers with their parameters.


### example.json

```json
{
  "input": "X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])\n    y = np.array([1, 1, -1, -1])\n    n_clf = 3\n\n    clfs = adaboost_fit(X, y, n_clf)\n    print(clfs)",
  "output": "(example format, actual values may vary):\n    # [{'polarity': 1, 'threshold': 2, 'feature_index': 0, 'alpha': 0.5},\n    #  {'polarity': -1, 'threshold': 3, 'feature_index': 1, 'alpha': 0.3},\n    #  {'polarity': 1, 'threshold': 4, 'feature_index': 0, 'alpha': 0.2}]",
  "reasoning": "The function fits an AdaBoost classifier on the dataset X with the given labels y and number of classifiers n_clf. It returns a list of classifiers with their parameters, including the polarity, threshold, feature index, and alpha values"
}
```




### learn.md


## Understanding AdaBoost

AdaBoost, short for Adaptive Boosting, is an ensemble learning method that combines multiple weak classifiers to create a strong classifier. The basic idea is to fit a sequence of weak learners on weighted versions of the data.

### Implementing the Fit Method for an AdaBoost Classifier

1. **Initialize Weights**  
   Start by initializing the sample weights uniformly:
   $$
   w_i = \frac{1}{N}, \text{ where } N \text{ is the number of samples}
   $$

2. **Iterate Through Classifiers**  
   For each classifier, determine the best threshold for each feature to minimize the error.

3. **Calculate Error and Flip Polarity**  
   If the error is greater than 0.5, flip the polarity:
   $$
   \text{error} = \sum_{i=1}^N w_i [y_i \neq h(x_i)]
   $$
   $$
   \text{if error} > 0.5: \text{error} = 1 - \text{error}, \text{ and flip the polarity}
   $$

4. **Calculate Alpha**  
   Compute the weight (alpha) of the classifier based on its error rate:
   $$
   \alpha = \frac{1}{2} \ln \left( \frac{1 - \text{error}}{\text{error} + 1e-10} \right)
   $$

5. **Update Weights**  
   Adjust the sample weights based on the classifier's performance and normalize them:
   $$
   w_i = w_i \exp(-\alpha y_i h(x_i))
   $$
   $$
   w_i = \frac{w_i}{\sum_{j=1}^N w_j}
   $$

6. **Save Classifier**  
   Store the classifier with its parameters.

### Key Insight
This method helps in focusing more on the misclassified samples in subsequent rounds, thereby improving the overall performance.


### meta.json

```json
{
  "id": "38",
  "title": "Implement AdaBoost Fit Method",
  "difficulty": "hard",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/eriklindernoren/ML-From-Scratch",
      "name": "Erik Linder-Nor\u00e9n"
    },
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ]
}
```




### solution.py

```python
import math
import numpy as np


def adaboost_fit(X, y, n_clf):
    n_samples, n_features = np.shape(X)
    w = np.full(n_samples, (1 / n_samples))
    clfs = []

    for _ in range(n_clf):
        clf = {}
        min_error = float('inf')

        for feature_i in range(n_features):
            feature_values = np.expand_dims(X[:, feature_i], axis=1)
            unique_values = np.unique(feature_values)

            for threshold in unique_values:
                p = 1
                prediction = np.ones(np.shape(y))
                prediction[X[:, feature_i] < threshold] = -1
                error = sum(w[y != prediction])

                if error > 0.5:
                    error = 1 - error
                    p = -1

                if error < min_error:
                    clf['polarity'] = p
                    clf['threshold'] = threshold
                    clf['feature_index'] = feature_i
                    min_error = error

        clf['alpha'] = 0.5 * math.log((1.0 - min_error) / (min_error + 1e-10))
        predictions = np.ones(np.shape(y))
        negative_idx = X[:, clf['feature_index']] < clf['threshold']
        if clf['polarity'] == -1:
            negative_idx = np.logical_not(negative_idx)
        predictions[negative_idx] = -1
        w *= np.exp(-clf['alpha'] * y * predictions)
        w /= np.sum(w)
        clfs.append(clf)

    return clfs
```




### starter_code.py

```python
import numpy as np
import math


def adaboost_fit(X, y, n_clf):
    n_samples, n_features = np.shape(X)
    w = np.full(n_samples, (1 / n_samples))
    clfs = []

    # Your code here

    return clfs
```




### tests.json

```json
[
  {
    "test": "X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])\ny = np.array([1, 1, -1, -1])\nn_clf = 3\nclfs = adaboost_fit(X, y, n_clf)\nprint(clfs)",
    "expected_output": "[{'polarity': -1, 'threshold': 3, 'feature_index': 0, 'alpha': 11.512925464970229}, {'polarity': -1, 'threshold': 3, 'feature_index': 0, 'alpha': 11.512925464970229}, {'polarity': -1, 'threshold': 3, 'feature_index': 0, 'alpha': 11.512925464970229}]"
  },
  {
    "test": "X = np.array([[8, 7], [3, 4], [5, 9], [4, 0], [1, 0], [0, 7], [3, 8], [4, 2], [6, 8], [0, 2]])\ny = np.array([1, -1, 1, -1, 1, -1, -1, -1, 1, 1])\nn_clf = 2\nclfs = adaboost_fit(X, y, n_clf)\nprint(clfs)",
    "expected_output": "[{'polarity': 1, 'threshold': 5, 'feature_index': 0, 'alpha': 0.6931471803099453}, {'polarity': -1, 'threshold': 3, 'feature_index': 0, 'alpha': 0.5493061439673882}]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/38_implement-adaboost-fit-method/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/38_implement-adaboost-fit-method/description.md)。Deep-ML：Educational Use Only License。
