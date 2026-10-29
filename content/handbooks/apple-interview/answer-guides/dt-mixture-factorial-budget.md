---
id: dt-mixture-factorial-budget
kind: concept
situation: 两类数据单独有效，混合反而掉点。
task: 区分交互、预算挤占和测量问题。
approach: 做受控组合及等 token 对照，检查 task slices。
result: 联合收益和 negative transfer 需同条件证据支持。
---

## 可以这样回答

两类数据单独有效，混合反而掉点。

用固定总预算的四组实验估计单独效果与交互，排查替换基础数据、重复率、gradient 与格式冲突。单独收益不能简单相加，组合表现差也不能直接推出“这两种能力互斥”。
