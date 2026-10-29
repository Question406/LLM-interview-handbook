---
id: coding-attn-mask
kind: coding
situation: causal、padding 和 document boundaries 同时影响可见性。
task: 构造指定形状和语义的 attention bias。
approach: 分别广播条件再相与，明确 bool 和加性 mask 约定。
result: 检查全屏蔽行、跨文档和 cache 位置。
---

## 可以这样回答

causal、padding 和 document boundaries 同时影响可见性。

先把 causal $j\le i$、key 非 pad、query 与 key 同文档三个条件按位与，再生成 `[B, 1, T, S]` 的加性 bias。合法位填 $0$，非法位填 $-\infty$；比如 packing 后第二篇文档不能读第一篇，一行全屏蔽时还要由 softmax 端处理 NaN。

测试时，我会检查全屏蔽行、跨文档和 cache 位置。
