---
id: dt-weighted-batcher
kind: coding
situation: 只恢复 random seed 会重新消费数据。
task: 按权重组 batch 并准确断点续跑。
approach: 同时保存各源 offset、随机状态和耗尽状态。
result: 恢复后样本序列一致，缺源不偷偷改 data mix。
---

## 可以这样回答

只恢复 random seed 会重新消费数据。

按 token 预算组 batch，checkpoint 保存每个数据源的读取 offset 和随机数状态，恢复时从原位置继续读；只恢复 random seed 的话，每个源会从头再读一遍。数据源耗尽时把它的概率设为零并报告，不悄悄改变 data mix。权重本身由上层决定，调 data mix 就是改 `weights`。

测试还要满足这个条件：恢复后样本序列一致，缺源不偷偷改 data mix。
