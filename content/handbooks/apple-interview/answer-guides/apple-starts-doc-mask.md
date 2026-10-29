---
id: apple-starts-doc-mask
kind: coding
situation: 同一行包含多篇独立文档。
task: 同时得到文档号、段内位置和可见性。
approach: 起点累计编号，传播最近起点，再组合三种 mask 条件。
result: 手算两篇文档，确认不跨文档且不看未来。
---

## 可以这样回答

同一行包含多篇独立文档。

对 starts 做 cumsum 得到文档编号，用 cummax 传播最近起点下标，再相减得到段内位置。可见性是同文档、key 不晚于 query、两端有效三个条件同时成立。

测试时，我会手算两篇文档，确认不跨文档且不看未来。
