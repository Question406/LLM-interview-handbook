---
id: dt-case-web-skill
kind: concept
situation: base model 可能已有能力但缺有效引导。
task: 用低成本方法检验缺口是否可唤起。
approach: 先在上下文加 skill 与同任务 baseline 对照。
result: 收益稳定且调用成本高时再考虑训练内化。
---

## 可以这样回答

base model 可能已有能力但缺有效引导。

先写一份几百 token 的设计 skill 放进上下文，当天就能对照。skill 能修好的部分说明模型会、只是缺引导，适合之后训进权重；修不好的才要去造数据。效果稳定、调用频繁、上下文成本明显的时候，就该把它训进模型。
