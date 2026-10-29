---
id: dt-annotator-protocol
kind: concept
situation: 标准含糊会让更多人重复不同理解。
task: 建立可复用且可检查的 annotation guidelines。
approach: 明确维度、tie、弃权和 edge cases。
result: 一致性与错误审计改善，合法分歧被保留。
---

## 可以这样回答

标准含糊会让更多人重复不同理解。

先写协议再开标，每个维度写清定义、正例、反例和不允许的判断捷径，再让两人独立标、算一致率。一致率低先查原因，是协议含糊、题本身不可比还是有长度捷径，查清了再决定要不要加人。AFM 报告里 20-30% 的 preference pairs 人与人之间不同意，他们用 cohesion 挑更容易达成一致的 prompt。
