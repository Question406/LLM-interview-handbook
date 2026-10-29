---
id: dt-novel-bootstrap
kind: concept
situation: 未标注 corpus 很多，人工只能看少量。
task: 从 seed 逐轮发现有价值的新覆盖。
approach: 质量、新颖度和不确定性结合，人工复核更新。
result: 独立能力收益持续才迭代，不只找离群噪声。
---

## 可以这样回答

未标注 corpus 很多，人工只能看少量。

从少量 seed 开始迭代：seed 来自冻结评测的失败案例、研究集和许可领域 hard examples，用小分类器给未标注数据打分，综合质量、新颖度和不确定性挑出值得人看的样本，标完更新分类器再筛下一轮。分类器可以用合成标签起步、按语言做 calibration；每轮看冻结评测有没有真的改善，边际收益停了就停。
