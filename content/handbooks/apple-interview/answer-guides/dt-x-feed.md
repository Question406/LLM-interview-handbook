---
id: dt-x-feed
kind: concept
situation: 时效内容会编辑、删除且含许可限制。
task: 构建可撤回的时间化数据流。
approach: 时间分区、规范 URL 与墓碑记录联动。
result: 截止后任务支持收益，旧版本和敏感来源被排除。
---

## 可以这样回答

时效内容会编辑、删除且含许可限制。

按时间分区的流式 pipeline 来设计：摄入时删帖用墓碑记录，过滤做语言识别并去掉广告、机器人和刷屏，转发按 URL deduplication 并保留引用计数，时效源放进 mid-training 或 annealing 阶段。来源要先过许可，公开帖子不等于能进基础模型，大规模汇聚 personally identifiable information (PII) 的时间线要排除。实时数据值不值，用训练截止后的事件问答来证明。
