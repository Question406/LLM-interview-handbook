---
id: dt-cost-per-gain
kind: project
situation: 生成量大不代表投入值得。
task: 按预算决定继续或换方案。
approach: 把标注、执行、训练和验收计入边际成本。
result: 每单位成本的独立收益及风险支持投入。
---

## 可以这样回答

生成量大不代表投入值得。

按数据源一行一行报：目标任务的提升、regression tasks 有没有掉、contamination rate，以及花掉的 GPU 小时和人工小时。再测边际收益，这个源再加 10% 目标任务还涨不涨，涨不动就停止扩量。条数和 token 数只说明规模，证明不了价值。
