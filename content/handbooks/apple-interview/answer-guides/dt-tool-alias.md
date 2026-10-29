---
id: dt-tool-alias
kind: concept
situation: 换名称就失败可能是接口记忆。
task: 训练工具语义而非固定字符串。
approach: 同任务变化 schema 与工具名，保持功能可比。
result: 新接口仍能选对和填对参数。
---

## 可以这样回答

换名称就失败可能是接口记忆。

多半学的是接口。检验方法是同一任务换工具名和 schema 再评，原接口能完成、换名就失败，说明模型依赖接口记忆。训练时同一能力要覆盖多套工具名和 schema，示范格式贴近部署时真正注入的工具规格，并在 dataset card 的 `surface` 中记录接口版本。
