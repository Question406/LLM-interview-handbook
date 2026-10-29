---
id: dt-simhash-code
kind: coding
situation: 短文本的 shingle 集合很小。
task: 快速寻找短文本 near-duplicates。
approach: 加权哈希位投票，再用汉明距离筛候选。
result: 小样本与相似度直觉对齐，说明适用范围。
---

## 可以这样回答

短文本的 shingle 集合很小。

SimHash 把每个特征哈希到 $f$ 维，按权重给每个 bit 投 +1 或 -1，最后取各维的符号当指纹，汉明距离小就是 near-duplicates。它适合短标题、URL 和 query，因为短文本的 shingle 集合太小，Jaccard 不稳；长网页 near-duplicates 仍用 `dt-minhash-code` 的 Jaccard。

测试还要满足这个条件：小样本与相似度直觉对齐，说明适用范围。
