---
id: dt-length-bucket-code
kind: coding
situation: 按篇 sampling 会被短模板支配。
task: 保持目标长度覆盖并遵守预算。
approach: 分长度桶 sampling，条数和 token 分别记账。
result: 检查空桶、长样本与实际 token 占比。
---

## 可以这样回答

按篇 sampling 会被短模板支配。

按 token 数把文档分进长度桶（2k / 8k / 32k），每桶单独设 token 配额，再从桶里按文档抽。文档是 sampling 单位，token 是预算单位。只按文档数随机打乱的话，海量短网页会占满名额，书和长文档被抽得太少。

测试时，我会检查空桶、长样本与实际 token 占比。
