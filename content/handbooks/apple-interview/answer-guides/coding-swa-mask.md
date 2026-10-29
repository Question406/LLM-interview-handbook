---
id: coding-swa-mask
kind: coding
situation: 窗口限制与 cache 绝对位置需要同时满足。
task: 只保留窗口内且不在未来的 key。
approach: 用 query 绝对下标判断 causal 和距离。
result: 手算窗口边缘，分别检查 prefill 与 decode 形状。
---

## 可以这样回答

窗口限制与 cache 绝对位置需要同时满足。

把 causal 和窗口两个条件相与：位置 $i$ 只看满足 $i-W \lt j \le i$ 的 key，其他位置设成 $-\infty$。Prefill 偏置是 `[1, 1, T, S]`，decode 只有一个 query，偏置是 `[1, 1, 1, S]`，query 的绝对下标取 cache 长度。

测试时，我会手算窗口边缘，分别检查 prefill 与 decode 形状。
