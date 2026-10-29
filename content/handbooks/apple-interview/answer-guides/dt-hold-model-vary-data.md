---
id: dt-hold-model-vary-data
kind: concept
situation: 模型或算力变化会混淆数据收益。
task: 让增益能 attribution 于具体数据变化。
approach: 固定训练条件，只替换一项数据因素。
result: 同套独立评测比较，并验证规模迁移。
---

## 可以这样回答

模型或算力变化会混淆数据收益。

固定架构、训练设置和算力预算，只换一项数据因素，用同一套固定评测比较目标任务和其他能力。DataComp、DataComp-LM 和 FineWeb-Edu 都是这个对照思路。small model 也能做，但选出的方案最后要在 large model 上确认一次。
