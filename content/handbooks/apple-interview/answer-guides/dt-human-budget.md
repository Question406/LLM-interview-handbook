---
id: dt-human-budget
kind: design
situation: 专家标注成本高，自动信号也有盲点。
task: 把预算花在会改变决策的样本上。
approach: 代表性、风险、分歧与随机审计结合使用，进行 sampling。
result: 看每标注小时的独立收益及未覆盖错误。
---

## 可以这样回答

专家标注成本高，自动信号也有盲点。

先建立可靠的 evaluation set，再标注 challenging cases，最后扩大数据量。human-review budget 优先保证 annotation guidelines、gold labels 和评测可靠，再标模型失败的 challenging tasks；能执行验证的数学和代码由人写 seed、teacher 扩充、executor 检查，tool-use trajectories 先让模型预跑、人只纠错。均匀撒到所有任务，会把钱花在模型已有的能力上。
