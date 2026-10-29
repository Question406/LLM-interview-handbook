---
id: msft-constrained-decode
kind: concept
situation: 下游工具需要结构化且可解析的输出。
task: 保证格式同时保留答案质量。
approach: 用文法限制合法 token，内容仍单独评价。
result: 分别报告解析率、事实正确与运行权限。
---

## 可以这样回答

下游工具需要结构化且可解析的输出。

约束 decoding 把 JSON Schema / 文法变成逐 token mask，保证机器接口的字段和语法合法。格式约束也会改变生成分布，multi-step reasoning 可先得出结果再填结构。验收分别看可解析率与答案正确率，副作用与权限仍由工具运行时检查。
