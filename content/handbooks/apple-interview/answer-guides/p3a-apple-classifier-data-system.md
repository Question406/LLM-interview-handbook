---
id: p3a-apple-classifier-data-system
kind: design
situation: 一个分类器还不足以构成可维护系统。
task: 从标签到上线反馈说明完整流程。
approach: 先简单 baseline，再围绕错误改数据和阈值。
result: 划分不 leakage、关键 evaluation slices 和版本监控可用。
---

## 可以这样回答

一个分类器还不足以构成可维护系统。

先定义标签与误判代价，建立简单分类器，再把标注、分组切分、阈值、部署与反馈串起来。系统质量取决于标签是否稳定、输入是否一致和错误是否被监测，不是只看模型复杂度。
