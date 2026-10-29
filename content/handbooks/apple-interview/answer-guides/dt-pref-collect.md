---
id: dt-pref-collect
kind: concept
situation: preference data 质量取决于比较标准。
task: 稳定收集 current policy 的有效标签。
approach: 定义评价维度、tie 和弃权条件，让 annotators 先标一小批并核对标准。
result: 分歧原因可解释，独立选择质量提高。
---

## 可以这样回答

preference data 质量取决于比较标准。

preference data 的质量主要看 annotation guidelines：先写清比较哪些维度、什么算 tie，再让当前模型生成待比较的回答。一致率 $\kappa$ 低时，先查题目、标准和示例是否含糊，改完再采；分歧来自标准本身时，加 annotator 也压不下去。能执行验证的任务优先用 rule-based reward，人只判断自动检查不了的维度。
