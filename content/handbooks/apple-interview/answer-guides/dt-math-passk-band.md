---
id: dt-math-passk-band
kind: design
situation: 太容易或完全不会的题都可能缺学习信号。
task: 找到 current policy 可学习的难度范围。
approach: 多次 sampling 估难度，兼顾覆盖和课程变化。
result: 看独立难度段收益，避免只筛出熟题。
---

## 可以这样回答

太容易或完全不会的题都可能缺学习信号。

按当前 student model 每题 sampling $k$ 次、做对几次来切，竞赛名称只能粗分。全对的太易少留；部分对的是中间带，成功 trajectories 做 SFT、错的做负样本；全错的先降难度或找 teacher / 解释器，RLVR 也需要模型有机会拿到非零奖励。换 student 要重切，还要防止中间带被 GSM8K 改写题填满。
