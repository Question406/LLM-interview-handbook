---
id: dt-response-logprob-code
kind: coding
situation: 序列得分容易漏 shift 或混入 prompt。
task: 批量得到回答的序列 log probability。
approach: 从目标 token 位置取分，再按回答 mask 求和。
result: 核对 EOS 与 padding，并区分求和和长度平均。
---

## 可以这样回答

序列得分容易漏 shift 或混入 prompt。

先用前一位置 logits 预测后一 token，再按目标位置的回答 mask 选取 log probability。序列概率取 token log probability 的和；长度平均是另一种评分，不能无说明替换标准 DPO 的序列求和。

测试时，我会核对 EOS 与 padding，并区分求和和长度平均。
