---
id: dt-posttrain-map
kind: guide
situation: 数学、代码和工具需要不同的正确性证据。
task: 先给任务选可靠监督再谈混合。
approach: 可执行任务先验证，主观任务明确偏好协议。
result: 各任务独立验收，不能用总奖励代替能力。
---

## 可以这样回答

数学、代码和工具需要不同的正确性证据。

post-training 的数据单位是题目、trajectories 和 grader，各类任务的 acceptance criteria 就是 grader 如何判断正确性：数学看标准答案、解释器或 Lean，代码看冻结的测试，工具看 schema 和环境状态，agent 还要看 trajectories 能否 replay、多跑几次是否稳定。四类检查各管一个域，要分开建；post-training 要准备的是题目、trajectories 和 grader，多加网页解决不了。
