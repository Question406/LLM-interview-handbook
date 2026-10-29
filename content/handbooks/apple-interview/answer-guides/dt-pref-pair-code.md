---
id: dt-pref-pair-code
kind: coding
situation: 差异小、标签弱或长度混杂的 preference pairs 有噪声。
task: 按明确规则筛选可用对。
approach: 先校验同 prompt 与标签，再检查 margin 和长度。
result: edge cases、tie、missing values 与拒收原因准确。
---

## 可以这样回答

差异小、标签弱或长度混杂的 preference pairs 有噪声。

preference pairs 要先过滤再用：丢掉 $y_w\approx y_l$ 的对、长度差过大的对，以及 annotator 自己标了「难分」的对。能执行的任务用独立 verifier 的结果当 margin，不让生成模型给自己打分。Llama 3 公开的排序是 edited > chosen > rejected，弱档不进 DPO。

测试还要满足这个条件：edge cases、tie、missing values 与拒收原因准确。
