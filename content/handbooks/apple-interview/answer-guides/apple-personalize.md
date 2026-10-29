---
id: apple-personalize
kind: design
situation: 个性化知识含私有且经常变化的内容。
task: 选择本地检索还是参数适配。
approach: 按事实更新、风格行为及撤回需求分工。
result: 收益在 on-device 测，私有内容不默认进入共享权重。
---

## 可以这样回答

个性化知识含私有且经常变化的内容。

会变的事实用本地检索，稳定的任务格式用功能 LoRA：比如日程走工具，邮件摘要和通知摘要切换各自的 adapter。公开 adapter 常为 rank 16、16-bit、几十 MB，基础模型冻结 quantization；私有上下文默认留在设备，需要人群统计时再考虑 DP，见 `apple-diff-privacy`。
