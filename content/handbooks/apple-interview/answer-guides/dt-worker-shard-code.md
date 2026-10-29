---
id: dt-worker-shard-code
kind: coding
situation: 每个 worker 可能各读一遍同样的数据。
task: 让并行迭代覆盖且不重复。
approach: 按 worker/rank 统一分片并记录恢复位置。
result: 多 worker 合并后每条恰好消费一次。
---

## 可以这样回答

每个 worker 可能各读一遍同样的数据。

先把 rank 与 worker 映射成全局消费者编号，再按稳定分片编号取模分配。必须说明 worker 数固定的假设；重新洗牌、弹性扩容和 checkpoint 恢复不能靠这个映射自动解决。

测试还要满足这个条件：多 worker 合并后每条恰好消费一次。
