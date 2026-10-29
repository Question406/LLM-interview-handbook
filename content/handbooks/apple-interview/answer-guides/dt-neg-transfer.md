---
id: dt-neg-transfer
kind: design
situation: 补一种能力同时损伤另一种。
task: 保住重要旧能力并定位冲突来源。
approach: 检查预算挤占，做 data mix 与来源替换对照。
result: 新旧 evaluation slices 都达 threshold，否则减权或停止。
---

## 可以这样回答

补一种能力同时损伤另一种。

训练前先列出必须保住的旧能力（英语通用、安全、格式、已经做好的核心任务），固定评测和允许波动；data mix 里给这些域设最低 token 份额，新数据比例逐步提高。旧能力超出波动就先降新来源的比例。目标任务涨了就发版，旧能力可能已经悄悄掉了。
