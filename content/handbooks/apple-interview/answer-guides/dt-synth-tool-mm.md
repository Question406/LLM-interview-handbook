---
id: dt-synth-tool-mm
kind: design
situation: 合法 JSON 或好看截图不代表任务完成。
task: 构建带环境反馈的工具/multimodal 样本。
approach: 从状态与证据生成任务，真实执行后核验。
result: 同初态能 replay，新任务和视觉变化可迁移。
---

## 可以这样回答

合法 JSON 或好看截图不代表任务完成。

工具和视觉是两条 pipeline，要分别讲生成和验证。工具数据在可重置的执行环境里生成，reference model 调用工具，人能回滚纠错，保存成功路径和被放弃的尝试，oracle 是环境状态，最后一句话说得对不算数。视觉数据要补详细描述、代码渲染的图表和可核验问答，还要教模型拒绝回答图中没有的信息。
