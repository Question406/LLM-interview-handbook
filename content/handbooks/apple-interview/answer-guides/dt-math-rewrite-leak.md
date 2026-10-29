---
id: dt-math-rewrite-leak
kind: design
situation: 改写会保留原题答案与结构。
task: 区分训练增强和 evaluation contamination。
approach: 先按原题家族划分，评价题不参与生成。
result: 改写 deduplication 与未见新题共同检查泛化。
---

## 可以这样回答

改写会保留原题答案与结构。

三条都满足才算增强：seed 不来自冻结评测题、答案重新计算、评测用独立题目。训练和测试都围着 GSM8K 同一题族时，换数字、换问法也可能只是让模型记住题族，换到 SVAMP、GSM-Hard 就掉分。看到合成集自称 MATH 提高 15%，先查 seed 和重叠。
