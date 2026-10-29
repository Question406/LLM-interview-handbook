---
id: dt-agent-rft-recipe
kind: design
situation: 奖励和环境接口决定可训练行为。
task: 解释公开 RFT 中的数据职责。
approach: 明确任务、可见观察、评分与 resampling。
result: 奖励有独立验证，公开接口不推成内部配方。
---

## 可以这样回答

奖励和环境接口决定可训练行为。

先在接近生产的任务分布上跑 baseline，把 prompt、任务范围和工具调好，确认还有提升空间再上 RFT。每条 rollout 用独立环境；reward 先检查 correctness，通过后再评 style，不给「尝试」部分分。多次 sampling 都找不到更好的解，训练就没有学习信号。
