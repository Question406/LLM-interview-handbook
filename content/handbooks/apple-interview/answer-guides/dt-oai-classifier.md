---
id: dt-oai-classifier
kind: concept
situation: 现场 fit 模型无法替代数据与标签检查。
task: 完成可信分类 baseline 和误差分析。
approach: 先查字段与 cluster 级划分，再按来源 对 threshold 做 calibration。
result: 独立 evaluation slices 及 false rejection 检查支持过滤用途。
---

## 可以这样回答

现场 fit 模型无法替代数据与标签检查。

先看清字段、标签来源和缺失，再按文档或 near-duplicates cluster 划分训练、开发和固定 evaluation set，然后建简单 baseline，按语言、长度、来源分析误差并对 threshold 做 calibration。这题考的是数据和标签靠不靠得住：只调用 fit、报一个总体 AUC，说明不了分类器能拿去过滤数据。
