---
id: dt-webarena-traj
kind: concept
situation: 同一网页任务可能有多条正确路径。
task: 以功能目标评价 tool-use trajectories。
approach: 验证终局与副作用，不机械模仿点击顺序。
result: 新任务模板有效，失败 replay 不冒充成功示范。
---

## 可以这样回答

同一网页任务可能有多条正确路径。

不能。同一任务有多条合法路径，判断标准是最终功能 assertion 是否通过，再查过程中有没有改了不该改的状态，逐次点击不必和人类一致。失败 replay 可作负例或恢复材料，不能直接当成功示范。训练实例还要和评测模板 deduplication。
