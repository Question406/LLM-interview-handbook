---
id: dt-adapter-vs-base
kind: design
situation: 能力缺口可能是普遍知识，也可能是局部行为。
task: 选择 base model 数据或 feature adapter。
approach: 按共享程度、更新频率和隐私范围做对照。
result: 目标改善且通用能力、部署成本达标。
---

## 可以这样回答

能力缺口可能是普遍知识，也可能是局部行为。

看问题影响多少个功能。多个功能共有的缺口，比如工具 schema、multilingual 指令、有证据支持的拒答，补进 base model post-training；只属于一个功能的固定格式或口吻，训 feature adapter；用户私有偏好留在 on-device。全回 base model SFT 或全交给 LoRA，都说明范围没切清。
