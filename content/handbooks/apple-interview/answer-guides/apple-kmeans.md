---
id: apple-kmeans
kind: coding
situation: 聚类迭代要处理 empty cluster 和停止后的标签。
task: 完成向 quantization 分配及中心更新。
approach: 明确距离、empty cluster 策略和最终重分配。
result: 对照小数据聚类，说明时间与中间内存。
---

## 可以这样回答

聚类迭代要处理 empty cluster 和停止后的标签。

我会用向 quantization 距离计算实现 Lloyd 迭代：每个点分到最近中心，再把中心更新为均值，empty cluster 按约定处理，结束后重新分配标签。时间是 $O(n k d I)$，距离可写成 $[n,k]$；广播实现还要检查中间 tensor 内存，再讨论 k-means++ 和 16 个中心 $\approx$ 4-bit 的码本。

测试时，我会对照小数据聚类，说明时间与中间内存。
