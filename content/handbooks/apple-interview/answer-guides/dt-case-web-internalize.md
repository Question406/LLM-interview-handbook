---
id: dt-case-web-internalize
kind: concept
situation: 运行时 skill 有效但长期占上下文。
task: 判断能否将行为迁移到模型权重。
approach: 带 skill 做 sampling 筛选，去 skill 训练并独立验收。
result: 不带 skill 的新任务也改善，避免只学模板。
---

## 可以这样回答

运行时 skill 有效但长期占上下文。

带着 skill sampling，用渲染、功能、视觉三道检查过滤，训练时把 skill 从 prompt 里拿掉做 SFT，之后再上 RL。最值钱的样本是「不带 skill 失败、带 skill 成功」的那些，它们正好是 skill 补上的能力。
