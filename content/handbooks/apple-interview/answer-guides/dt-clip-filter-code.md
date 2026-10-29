---
id: dt-clip-filter-code
kind: coding
situation: 相似度高不保证 caption 事实全对。
task: 按来源过滤 image-text pairs 且控制 false rejection。
approach: 真实和合成 caption 分别对 threshold 做 calibration。
result: 抽查错配、难图与保留覆盖，不只看均分。
---

## 可以这样回答

相似度高不保证 caption 事实全对。

图像和文本各自编码成向量，用余弦相似度当图文匹配分，再按语言和来源分桶，每桶取分位数当阈值。合成 caption 的 CLIP 分会向 teacher model 的分布靠拢而虚高，所以要和网页 alt-text 分开设阈值。重复和安全 CLIP 分管不到，要用各自的 checker，误删靠下游对照来验证。

测试还要满足这个条件：抽查错配、难图与保留覆盖，不只看均分。
