---
id: dt-tool-gap-factorial
kind: design
situation: 工具名称选对仍可能在参数或结果利用上失败。
task: 定位调用链中真正瓶颈。
approach: 逐项用 oracle 工具、参数、返回信息做 controlled substitution。
result: 能区分假设后才补数据，避免多因素同时改。
---

## 可以这样回答

工具名称选对仍可能在参数或结果利用上失败。

把工具选择、参数构造、执行与结果解释拆开，利用固定工具或注入正确中间结果做受控实验。定位主要失败阶段后，再用等预算数据干预验证；单个指标的改善不能推出端到端改善。
