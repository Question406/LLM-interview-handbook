---
id: dt-ifeval-overlay
kind: concept
situation: 评测题直接训练会失去评价意义。
task: 构造同类但独立的指令约束数据。
approach: 从自有任务组合可同时满足的规则。
result: 内容和格式分别检查，新语言验证 checker。
---

## 可以这样回答

评测题直接训练会失去评价意义。

不能。IFEval 的 541 条英文题是 evaluation set，拿来训就失去评测意义。要借它的思路另造 training set：从自己的 SFT 数据抽任务、叠同类的可执行约束，生成独立的 RLVR 数据；同时检查约束能否同时满足，按语言改写 checker，并单独评内容质量，免得只学会格式。
