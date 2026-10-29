---
id: dt-agent-swegym
kind: design
situation: 仓库可执行性决定反馈是否可信。
task: 将修复任务转成可重复训练环境。
approach: 固定代码快照、依赖和 hidden tests，保存 tool-use trajectories。
result: 重置能复现，补丁正确且没有修改评测器。
---

## 可以这样回答

仓库可执行性决定反馈是否可信。

SWE-Gym 把真实 Python 任务、可执行环境和单测做成一个训练工厂：current policy sampling，测试判成败，成功 trajectories 做 SFT，成败 trajectories 一起训 outcome verifier。任务池要和评测隔开。过测只是必要条件，改测试、漏回归和环境漂移要另外拦。
