---
id: dt-semdedup-code
kind: coding
situation: 改写后的重复可能绕过字符串 deduplication。
task: 控制高价值子集的语义重复。
approach: 先便宜 deduplication，再用 embeddingnearest neighbors 复核。
result: 抽查同义与相关但不同的内容，评估成本。
---

## 可以这样回答

改写后的重复可能绕过字符串 deduplication。

MinHash 抓不到换了说法的重复，这一层用 embedding 来补：对已经过精确哈希和 MinHash 的高价值子集，用 ANN 取 top-$k$ nearest neighbors，余弦相似度超过阈值的归入同一个 cluster，保留质量最高的一条。适合许可书、SFT 和通过 verifier 的 synthetic data；成本高，十亿级网页不宜直接全量跑。

测试还要满足这个条件：抽查同义与相关但不同的内容，评估成本。
