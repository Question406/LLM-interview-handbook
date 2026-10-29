---
id: dt-lima-vs-scale
kind: concept
situation: 少量精标与海量 pre-training 看似矛盾。
task: 区分学习知识与学习回答行为。
approach: 先判断 base model 已有能力，再选示范或覆盖数据。
result: 比较能力题和行为题，不把文风迁移当知识提升。
---

## 可以这样回答

少量精标与海量 pre-training 看似矛盾。

两个阶段解决的问题不同。LIMA 的 1000 条精标示范，教的是已有能力的模型怎么回答；pre-training 让模型学到知识、覆盖更多任务。base model 本来不会的事，少量漂亮示范补不上，False Promise 也发现模仿 teacher 的风格不等于学到 teacher 的能力。
