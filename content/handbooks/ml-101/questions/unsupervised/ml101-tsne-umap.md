---
id: "ml101-tsne-umap"
section: "unsupervised"
order: 8
level: "A"
title: "t-SNE 和 UMAP 图能支持哪些结论，不能支持哪些？"
quick: "t-SNE 和 UMAP 适合探索局部邻居与可疑样本，二维图上的簇大小、密度和远距离不能直接当原空间的定量结论。换参数和随机种子检查结构，再回原空间验证距离、标签和聚类稳定性。"
tags: ["ML101", "unsupervised"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "Visualizing Data using t-SNE"
    url: https://jmlr.org/papers/v9/vandermaaten08a.html
    type: primary
  - title: "UMAP: Using UMAP for Clustering"
    url: https://umap-learn.readthedocs.io/en/latest/clustering.html
    type: primary
---

t-SNE 和 UMAP 可以帮助看局部邻域、发现可疑分组，但二维上的“几个岛”不足以证明数据天然分成几类。t-SNE 用低维概率关系拟合高维邻近关系，UMAP 则基于邻居图构造嵌入；压缩都会改变部分几何信息。 [Visualizing Data using t-SNE](https://jmlr.org/papers/v9/vandermaaten08a.html)

例如一团点在二维里被拉成两个岛，可能是局部邻居关系、参数或优化过程共同造成的。UMAP 官方也提醒，嵌入不完整保留密度，可能把原本连续的簇撕开。因此不能仅按岛的面积判断样本多样性，也不能按两个岛的间距直接比较类别差异。 [UMAP: Using UMAP for Clustering](https://umap-learn.readthedocs.io/en/latest/clustering.html)

我会变动邻域参数和随机种子，检查哪些邻居与分组反复出现，再回原空间核对近邻、标签和业务属性。若要做聚类，把降维当作待验证的预处理，与原空间或更高维嵌入的结果比较。

## 追问

**图上混在一起，分类就做不好吗？**
不一定。二维投影可能丢了判别信息，要用独立验证集上的分类指标判断。

**把标签喂给 UMAP 再看分离程度，可以证明模型有效吗？**
不能直接这样证明。标签已经参与表示构造，仍需要未参与拟合的数据评估。

**固定 seed 后图一样，就可信了吗？**
只说明这次配置可重复。还要验证对参数、抽样和数据版本的稳定性。
