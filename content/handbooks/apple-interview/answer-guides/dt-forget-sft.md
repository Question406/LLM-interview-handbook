---
id: dt-forget-sft
kind: concept
situation: 新任务 fine-tuning 可能覆盖已有能力。
task: 保住旧任务同时学习新行为。
approach: 做 regression data replay，并通过受控实验调整 data mix。
result: 新旧任务同时评，KL 或 LoRA 不当无遗忘保证。
---

## 可以这样回答

新任务 fine-tuning 可能覆盖已有能力。

通过 replay 旧任务数据来保住已有能力。SFT 数据里留着通用指令、multilingual、安全和 tool calls 这些旧任务，每轮同时评新旧能力，旧能力退步超过阈值就减新任务权重或停训。KL 约束和 LoRA 只能让遗忘变慢，代替不了 replay。
