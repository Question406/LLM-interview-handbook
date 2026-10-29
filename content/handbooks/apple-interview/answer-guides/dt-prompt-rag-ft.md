---
id: dt-prompt-rag-ft
kind: concept
situation: 知识更新、行为改变和私有检索需要不同办法。
task: 选择最合适的能力载体。
approach: 根据时效、许可与任务缺口比较 prompt、检索和训练。
result: 任务收益、权限隔离与维护成本一起检查。
---

## 可以这样回答

知识更新、行为改变和私有检索需要不同办法。

依次问三个问题：知识经常变，或来源不允许进基础模型，就用带权限的 RAG 或工具；要改回答格式、工具习惯和拒答行为，做 SFT / RL；许可的世界知识属于 pre-training 或 continued PT。租户私有文件走带租户键的检索，不写进权重。
