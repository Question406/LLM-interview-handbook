---
id: dt-reward-pref
kind: concept
situation: 任务正确性和主观偏好需要不同信号。
task: 选择 RM、DPO 或在线 RL。
approach: 按可验证性、探索需求和预算比较。
result: 独立 human evaluation 或执行结果支持选择，不看自家奖励。
---

## 可以这样回答

我会先看任务能不能直接验证。代码是否通过独立测试、工具状态是否正确，这些通常先用执行反馈；开放写作或回答是否有帮助，才更需要 preference labels 和 reward model。

方法上，如果现有 preference pairs 覆盖得不错、主要是在调整回答行为，我会先比较 DPO 这样的离线方法。需要探索新的 tool-use trajectories，而且奖励比较可靠时，再考虑在线 RL。这里还有标注、运行和维护成本的区别。

最后我会用独立的任务结果或 human evaluation 来选。训练奖励更高，只说明模型更会得到这个奖励，不足以证明用户得到更好的答案。
