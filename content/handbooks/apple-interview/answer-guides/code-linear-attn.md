---
id: code-linear-attn
kind: coding
situation: 历史 attention 的开销随序列增长。
task: 实现核化 attention 的并行与递推形式。
approach: 将历史压成键值统计量，利用结合律累计。
result: 两种计算逐位置一致，说明数值与状态限制。
---

## 可以这样回答

历史 attention 的开销随序列增长。

把 softmax 换成非负核 $\phi(q)^\top\phi(k)$，靠结合律把历史累加成 $S_t=\sum\phi(k)v^\top$ 和 $z_t=\sum\phi(k)$。decode 时只更新这两个量，输出 $\phi(q)^\top S_t/\phi(q)^\top z_t$，状态大小和序列长度无关；训练用的并行形式和这个递推要数值一致。

测试还要满足这个条件：两种计算逐位置一致，说明数值与状态限制。
