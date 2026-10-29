---
id: dt-userlog-contrast
kind: concept
situation: 生产对话不自动具有训练许可。
task: 合法构建对话监督数据。
approach: 先确认用途再筛质量，或用许可研究集复现。
result: 许可、版本和标签可信，隐式反馈偏差被审计。
---

## 可以这样回答

生产对话不自动具有训练许可。

先确认这些对话有没有训练许可，再过 data quality checks：PII、毒性、deduplication、可复现的数据版本都要查。没有许可的生产日志，换成知情同意的研究集、许可 corpus 和按失败类型合成的复现。日志做了匿名化也不等于获得训练许可，点赞、重试这类隐式信号还要处理偏差。
