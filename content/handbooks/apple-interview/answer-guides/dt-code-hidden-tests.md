---
id: dt-code-hidden-tests
kind: design
situation: 公开样例覆盖很有限。
task: 防止模型只适应已见测试。
approach: 公开反馈与隐藏验收分离，扩充独立 edge-case tests。
result: 原测试与新测试都通过且没有修改 grader。
---

## 可以这样回答

公开样例覆盖很有限。

三套测试三种用途：公开测试给模型当改代码的反馈，hidden tests 决定能不能当正例和 RL 奖励，EvalPlus 或新竞赛题做独立评测。hidden tests 要固定哈希，改过测试的 trajectories 要隔离；只过了公开样例或只是编译成功，都不算正确解。
