---
id: dt-code-oss-instruct
kind: design
situation: 无上下文造代码题容易脱离真实用法。
task: 把许可代码转成有依据的指令任务。
approach: 保留源码语义与出处，执行验证新指令答案。
result: 独立题型有效，许可和近克隆不越界。
---

## 可以这样回答

无上下文造代码题容易脱离真实用法。

从许可仓库抽真实代码片段，让 teacher 照着片段出题，题目会覆盖 API、并发、文件和错误处理这些实际问题，比 teacher 凭空反复出教材题更能保持多样性。片段许可证、执行测试和与 HumanEval 的重叠仍然要查。OSS-Instruct 管覆盖，Evol-Instruct 管难度，两者可以叠着用。
