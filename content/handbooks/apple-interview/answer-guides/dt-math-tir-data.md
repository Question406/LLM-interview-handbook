---
id: dt-math-tir-data
kind: design
situation: 纯文字推理和执行程序有不同错误。
task: 为数学任务选择合适的工具监督。
approach: 比较 CoT、程序及混合 trajectories 的可验证性与预算。
result: 同一任务同预算测正确率和工具错误传播。
---

## 可以这样回答

纯文字推理和执行程序有不同错误。

按任务分，需要计算的步骤用 TIR 交给解释器，心算、不等式、证明思路仍用自然语言。PAL / PoT 把题意转成程序，ToRA / OpenMathInstruct 让推理和代码调用交替。代码必须在沙箱里真实执行，最终答案再对 gold labels；解释器输出作为输入，不计入 CE。
