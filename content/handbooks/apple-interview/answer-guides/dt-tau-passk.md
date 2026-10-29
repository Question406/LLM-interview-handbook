---
id: dt-tau-passk
kind: concept
situation: 单次通过可能来自运气。
task: 测量多次执行的一致可靠性。
approach: 同任务多次重置，核对政策和数据库状态。
result: 连续成功与至少一次成功分开报告。
---

## 可以这样回答

单次通过可能来自运气。

因为一次通过可能是运气。τ-bench 看同题多次运行是否都遵守政策、正确更新数据库：gpt-4o 零售 $\mathrm{pass}^{1}$ 约 61%，到 $\mathrm{pass}^{8}$ 只剩约 25%。用 $\mathrm{pass}^{k}$ 当进 SFT 和发版的 evaluation gate，训练仍可用单次状态奖励；trajectories 还要查必经只读调用，用户模拟和 grader 标签需独立复核。
