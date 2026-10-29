---
id: afm-web-synthetic-loop
kind: design
situation: 真实 seed 很少，teacher 可以批量生成，但生成量不代表训练价值。
task: 扩大任务覆盖，同时控制错误、近重复和 evaluation leakage。
approach: 先按任务家族隔离真实评估，再做 generation、verification、deduplication 和训练对照。
result: 在独立真实任务上优于等预算 baseline，且 long-tail 不退化。
---

## 可以这样回答

我会先把少量真实样本按任务家族分开，留出一部分不参与生成和选择。否则 teacher 把 seed 改写很多遍，训练和测试看起来不同，实际还是同一批问题。

假设要补 tool-use 参数错误，我会从训练 seed 提炼任务规则，生成参数组合和 boundary conditions，再让 teacher 产生候选动作。生成只是第一步；每条还需要通过 schema 检查、实际执行与终局核验。格式正确不等于业务正确。

我会保留失败原因，而不是只保留成功样本。这样能看到某类任务是不是全部被筛掉了，也能区分 teacher 不会做和环境本身出错。对可用结果再做 task-level deduplication，控制常见模板的占比。

第一轮我会比较原始 seed、等 token 的简单扩写、以及经过 verification 的 targeted synthetic data。只有第三组在独立真实任务上有稳定增益，我才会继续扩规模。这个方案可以讨论，但不能把它写成我已经生产过的数据集。
