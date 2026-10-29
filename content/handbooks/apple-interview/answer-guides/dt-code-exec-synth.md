---
id: dt-code-exec-synth
kind: concept
situation: 修改测试后通过等于改变判分条件。
task: 保留真实修复而非作弊 trajectories。
approach: 固定原测试 hash，独立检查补丁和权限。
result: hidden tests 与回归通过，编译输出不当生成目标。
---

## 可以这样回答

修改测试后通过等于改变判分条件。

不算。模型改测试才通过，等于改了判分条件，这种 trajectories 要隔离，不当 SFT 正例。做法是在模型动手前记下测试的哈希、条数和 assertion，只有通过原测试的修复才算成功；执行反馈可以拿来学修复，编译器输出不计入生成 loss。
