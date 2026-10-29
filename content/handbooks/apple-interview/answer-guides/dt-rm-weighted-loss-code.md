---
id: dt-rm-weighted-loss-code
kind: coding
situation: preference pairs 的 confidence weight 不同甚至全零。
task: 计算稳定的加权 pairwise loss。
approach: softplus 处理分差，用实际权重和 normalization。
result: 手算 log(2)，检查小权重和全零 gradient。
---

## 可以这样回答

preference pairs 的 confidence weight 不同甚至全零。

对 chosen 与 rejected 奖励差使用 softplus，再按 confidence weight normalization。分母是权重总和，不是样本数；全零权重时返回仍连着计算图的零，使 backward 有定义但 gradient 为零。

测试时，我会手算 log(2)，检查小权重和全零 gradient。
