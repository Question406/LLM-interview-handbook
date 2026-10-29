---
id: apple-rank-adapter
kind: design
situation: 检索事实和学习偏好是不同个性化需求。
task: 比较低秩适配与本地检索。
approach: 按隐私、更新频率与可撤回性设计。
result: 用户任务改善且隔离、遗忘与成本可检查。
---

## 可以这样回答

检索事实和学习偏好是不同个性化需求。

会变的事实走本地检索，稳定格式和任务行为走 LoRA；按用户训练时，数据和权重应留在设备。公开产品 adapter 常为 rank 16，开发者 toolkit 提到 rank 32，16-bit 存储约几十 MB，可在冻结 quantization 底模上热切换；遗忘和版本绑定也要设计。
