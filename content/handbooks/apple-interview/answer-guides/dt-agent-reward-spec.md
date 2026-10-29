---
id: dt-agent-reward-spec
kind: design
situation: 模型会优化 scorer 遗漏的条件。
task: 让奖励对应任务与权限约束。
approach: 真实状态为主，过程和成本项明确优先级。
result: 对抗 replay 不易骗分，独立任务结果同步改善。
---

## 可以这样回答

模型会优化 scorer 遗漏的条件。

奖励 $r$ 以 hidden tests 或最终状态检查为准，可以是 0/1，也可以按测试点计分。可见测试的结果只当环境反馈给模型看，不进最终奖励。补丁和标准补丁的文本相似度会压低功能等价但写法不同的解，最多当辅助信号。
