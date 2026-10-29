---
id: drustz-90ea722ac9ec8cc115
section: deepml
order: 40
level: A
title: Deep-ML legacy · 120 bhattacharya distance
quick: Deep-ML 练习 · Deep-ML legacy · 120 bhattacharya distance
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/120_bhattacharya_distance/learn.md
    type: primary
---
### learn.md


# Learn Section

## Understanding Bhattacharyya Distance

**Bhattacharyya Distance (BD)** is a concept in statistics used to measure the **similarity** or **overlap** between two probability distributions **P(x)** and **Q(x)** on the same domain **x**.  

This differs from **KL Divergence**, which measures the **loss of information** when projecting one probability distribution onto another (reference distribution).  

### **Bhattacharyya Distance Formula**
The Bhattacharyya distance is defined as:  

$$
BC (P, Q) = \sum \sqrt{P(X) \cdot Q(X)}
$$

$$
BD (P, Q) = -\ln(BC (P, Q))
$$

where **BC (P, Q)** is the **Bhattacharyya coefficient**.  

### **Key Properties**
1. **BD is always non-negative**:  
   $$ BD \geq 0 $$
2. **Symmetric in nature**:  
   $$ BD (P, Q) = BD (Q, P) $$
3. **Applications**:  
   - Risk assessment  
   - Stock predictions  
   - Feature scaling  
   - Classification problems  

### **Example Calculation**
Consider two probability distributions **P(x)** and **Q(x)**:  

$$
P(x) = [0.1, 0.2, 0.3, 0.4], \quad Q(x) = [0.4, 0.3, 0.2, 0.1]
$$

1. **Bhattacharyya Coefficient**:  

$$
BC (P, Q) = \sum \sqrt{P(X) \cdot Q(X)} = 0.8898
$$

2. **Bhattacharyya Distance**:  

$$
BD (P, Q) = -\ln(BC (P, Q)) = -\ln(0.8898) = 0.1166
$$

This illustrates how BD quantifies the **overlap** between two probability distributions.  

    

### solution.py

```python
import numpy as np


def bhattacharyya_distance(p: list[float], q: list[float]) -> float:

    if len(p) != len(q):
        return 0.0

    p, q = np.array(p), np.array(q)

    BC = np.sum(np.sqrt(p * q))  #### Bhattacharya coefficient

    DB = -np.log(BC)  #### Bhattacharya distance

    return round(DB, 4)


def test_bhattacharyya_distance() -> None:

    # Test Case 1
    p = [0.1, 0.2, 0.3, 0.4]
    q = [0.4, 0.3, 0.2, 0.1]
    assert bhattacharyya_distance(p, q) == 0.1166

    # Test Case 2
    p = [0.7, 0.2, 0.1]
    q = [0.4, 0.3, 0.3]
    assert bhattacharyya_distance(p, q) == 0.0541

    # Test Case 3
    p = []
    q = [0.5, 0.4, 0.1]
    assert bhattacharyya_distance(p, q) == 0.0

    # Test Case 4
    p = [0.6, 0.4]
    q = [0.1, 0.7, 0.2]
    assert bhattacharyya_distance(p, q) == 0.0

    # Test Case 5
    p = [0.6, 0.2, 0.1, 0.1]
    q = [0.1, 0.2, 0.3, 0.4]
    assert bhattacharyya_distance(p, q) == 0.2007


if __name__ == '__main__':
    test_bhattacharyya_distance()
    print('All Bhattacharyya Distance test cases passed')
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/Problems/120_bhattacharya_distance/learn.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/Problems/120_bhattacharya_distance/learn.md)。Deep-ML：Educational Use Only License。
