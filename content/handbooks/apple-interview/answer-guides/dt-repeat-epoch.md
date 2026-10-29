---
id: dt-repeat-epoch
kind: concept
situation: 新 token 不足但训练预算还有余量。
task: 判断重复数据是否仍值得用。
approach: 先 deduplication，再用重复次数对照估边际收益。
result: 独立能力不再提高时停止继续重复。
---

## 可以这样回答

新 token 不足但训练预算还有余量。

可以，但先 deduplication，再有限地重复。Muennighoff 等的 datablations 发现，固定算力下重复到约 4 个 epoch，效果接近用新数据，再多收益就很小。near-duplicates 文档不能算新数据，也别为了凑 token 数放松必要的质量过滤。
