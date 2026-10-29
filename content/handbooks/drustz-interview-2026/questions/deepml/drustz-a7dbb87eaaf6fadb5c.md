---
id: drustz-a7dbb87eaaf6fadb5c
section: deepml
order: 15
level: A
title: Calculate Computational Efficiency of MoE
quick: Deep-ML 练习 · Calculate Computational Efficiency of MoE
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/123_calculate-computational-efficiency-of-moe/description.md
    type: primary
---
### description.md

Calculate the computational cost savings of an MoE layer compared to a dense layer, as discussed in the paper 'Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.' Given the number of experts, sparsity (number of active experts), and input/output dimensions, compute the floating-point operations (FLOPs) for both and determine the savings percentage.


### example.json

```json
{
  "input": "compute_efficiency(1000, 2, 512, 512)",
  "output": "99.8",
  "reasoning": "Dense layer FLOPs: 1000 * 512 * 512 = 262,144,000. MoE FLOPs: 2 * 512 * 512 = 524,288. Savings:  ((262,144,000 - 524,288) / 262,144,000) x 100 ≈ 99.8%."
}
```




### learn.md


## Understanding MoE Efficiency

The paper *"Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer"* introduces the idea of activating only a few expert networks per input to drastically reduce computation. This is known as **conditional computation**, and it allows models to scale to billions of parameters without significantly increasing cost.

---

### Key Idea

In a **dense layer**, every input goes through the full set of parameters.  
In a **Mixture-of-Experts (MoE)** layer, only $k$ out of $n$ experts are active for each input.

---

### FLOPs Formulas

Let:
- $d_{in}$ = input dimension  
- $d_{out}$ = output dimension  
- $n$ = total experts  
- $k$ = active experts per input  

Then:
- **Dense layer FLOPs**:  
  $$
  \text{FLOPs}_{\text{dense}} = n \cdot d_{in} \cdot d_{out}
  $$
- **MoE layer FLOPs**:  
  $$
  \text{FLOPs}_{\text{moe}} = k \cdot d_{in} \cdot d_{out}
  $$
- **Efficiency gain**:
  $$
  \text{Savings}(\%) = \left( \frac{\text{FLOPs}_{\text{dense}} - \text{FLOPs}_{\text{moe}}}{\text{FLOPs}_{\text{dense}}} \right) \cdot 100
  $$

---

### Example

Suppose:
- $n = 1000$, $k = 2$  
- $d_{in} = d_{out} = 512$  

Then:
- MoE FLOPs = $2 \cdot 512 \cdot 512 = 524,\!288$  
- Full dense (all 1000 experts): $1000 \cdot 512 \cdot 512 = 262,\!144,\!000$  
- Savings:
  $$
  \left( \frac{262,\!144,\!000 - 524,\!288}{262,\!144,\!000} \right) \cdot 100 \approx 99.8\%
  $$

This means the MoE layer uses just **0.2%** of the computation compared to a full dense version — an enormous gain in efficiency.

---

### Summary

By activating only a small number of experts per input, MoE layers reduce computation while maintaining high model capacity. This makes it feasible to train outrageously large models efficiently.


### meta.json

```json
{
  "id": "123",
  "title": "Calculate Computational Efficiency of MoE",
  "difficulty": "easy",
  "category": "Deep Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe Chabot"
    }
  ]
}
```




### solution.py

```python
def compute_efficiency(n_experts, k_active, d_in, d_out):
    dense_flops = n_experts * d_in * d_out
    moe_flops = k_active * d_in * d_out
    savings = (dense_flops - moe_flops) / dense_flops * 100
    return round(savings, 1)
```




### starter_code.py

```python
def compute_efficiency(n_experts, k_active, d_in, d_out):
    """
    Calculate computational savings of MoE vs. dense layer.

    Args:
        n_experts: Total number of experts
        k_active: Number of active experts (sparsity)
        d_in: Input dimension
        d_out: Output dimension

    Returns:
        Percentage savings in FLOPs
    """
    pass
```




### tests.json

```json
[
  {
    "test": "print(round(compute_efficiency(1000, 2, 512, 512),1))",
    "expected_output": "99.8"
  },
  {
    "test": "print(round(compute_efficiency(10, 2, 256, 256),1))",
    "expected_output": "80.0"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/123_calculate-computational-efficiency-of-moe/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/123_calculate-computational-efficiency-of-moe/description.md)。Deep-ML：Educational Use Only License。
