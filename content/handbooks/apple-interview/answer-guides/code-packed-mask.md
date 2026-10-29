---
id: code-packed-mask
kind: coding
situation: 一条 packed 序列包含多个独立样本。
task: 根据 document offsets 构造块对角 causal mask。
approach: 先定位 doc id，再比较同段与先后位置。
result: 各段首尾和空段不能引入跨文档可见性。
---

## 可以这样回答

一条 packed 序列包含多个独立样本。

用 prefix sum `cu_seqlens` 给每个位置算出所属的 doc id，keep 的条件是同一文档且 $j\le i$。跨文档的位置要设成 $-\infty$，否则后一条样本能看到前一条。

测试还要满足这个条件：各段首尾和空段不能引入跨文档可见性。
