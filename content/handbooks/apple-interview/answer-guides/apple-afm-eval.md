---
id: apple-afm-eval
kind: design
situation: on-device 系统受延迟、能耗和隐私约束。
task: 定义用户任务真正成功的条件。
approach: 任务指标与设备成本、安全约束并列测量。
result: 同硬件同预算比较，语言分组和关键风险达标。
---

## 可以这样回答

on-device 系统受延迟、能耗和隐私约束。

我会分别评任务质量、证据支持、安全、系统性能和隐私，再决定 on-device 模型能否上线。BLEU 只看 n-gram 重叠，既看不出摘要漏限定词，也测不到热降频或邮件是否离开设备，所以只能当辅助回归指标。
