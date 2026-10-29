---
id: dt-distill-forward-kl-code
kind: coding
situation: teacher 和 student 的分布方向不能混用。
task: 实现有效 token 上的 temperature-scaled distillationKL。
approach: teacher 冻结，vocabulary 维求和，再按 token 平均。
result: 同分布 KL 为零，检查温度系数与 teacher gradient。
---

## 可以这样回答

teacher 和 student 的分布方向不能混用。

本题用 teacher 分布到 student 分布的 forward KL，在 vocabulary 维求和，再按有效 token 平均并乘温度平方。teacher 必须冻结，不能把 KL 的输入顺序或对 vocabulary 的平均与 token 平均混淆。

测试还要满足这个条件：同分布 KL 为零，检查温度系数与 teacher gradient。
