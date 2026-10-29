---
id: dt-lsh-cluster-code
kind: coding
situation: near-duplicates 关系以候选对形式分散。
task: 合并 cluster 并选择保留代表。
approach: 精确复核后并查集合并，保留策略明确。
result: 检查传递关系与链式误合并，代表可追溯。
---

## 可以这样回答

near-duplicates 关系以候选对形式分散。

对 LSH 候选对先算精确 Jaccard，只给达到阈值的文档对连边，再用并查集求连通分量，得到 near-duplicates cluster。每个 cluster 保留质量最高的一条，缺质量分时才看长度。异常大的 cluster 多半是公共模板造成的误连，要剥掉模板、分域后重新聚类。

测试时，我会检查传递关系与链式误合并，代表可追溯。
