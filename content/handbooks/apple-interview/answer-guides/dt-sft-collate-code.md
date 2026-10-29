---
id: dt-sft-collate-code
kind: coding
situation: 对话长度不一，截断可能删光监督。
task: 组成有效 batch 并正确标记 labels。
approach: 先定截断契约，再按真实位置生成 mask。
result: 检查真实 pad_id、无回答和超长样本。
---

## 可以这样回答

对话长度不一，截断可能删光监督。

先按明确的截断规则裁剪，再按 token 位置构造 attention mask 和 labels；padding 与 prompt 不参与 loss。不能通过 token 是否等于 pad_id 判断 padding，因为真实 token 也可能使用相同 ID。

测试时，我会检查真实 pad_id、无回答和超长样本。
