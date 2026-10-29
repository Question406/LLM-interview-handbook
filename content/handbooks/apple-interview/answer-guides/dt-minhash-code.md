---
id: dt-minhash-code
kind: coding
situation: 全量两两比较网页不可扩展。
task: 找到 near-duplicates 候选并准确复核。
approach: MinHash 压签名，LSH 召回候选，精确 Jaccard 确认。
result: 对照暴力 nearest neighbors，报告候选数和漏召回。
---

## 可以这样回答

全量两两比较网页不可扩展。

先把文档拆成 shingle 集合并生成 MinHash 签名，再用 LSH 分段找候选：签名某一维相等的概率等于 Jaccard，任一 band 完全相等就进候选。候选最后仍要用精确 Jaccard 复核。规模分析要估候选对数，因为总成本取决于候选数量。

测试时，我会对照暴力 nearest neighbors，报告候选数和漏召回。
