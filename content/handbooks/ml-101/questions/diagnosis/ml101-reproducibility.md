---
id: "ml101-reproducibility"
section: "diagnosis"
order: 8
level: "A"
title: "随机种子为什么仍不能保证所有训练完全复现？"
quick: "随机种子只控制部分随机数来源，不能消除非确定算子、并行归约顺序及软硬件版本差异。要复现，需同时固定数据与划分、全部随机源、运行环境和算法配置，并记录性能代价及允许的数值误差。"
tags: ["ML101", "diagnosis"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "PyTorch: Reproducibility"
    url: https://docs.pytorch.org/docs/2.14/notes/randomness.html
    type: primary
---

固定 seed 是复现的一部分，无法保证跨设备、跨版本的训练逐位相同。PyTorch 明确说明，不同发布版本、平台以及 CPU/GPU 之间，即使 seed 相同也不保证完全复现。 [PyTorch: Reproducibility](https://docs.pytorch.org/docs/2.14/notes/randomness.html)

原因一类是随机源没统一，例如 Python、NumPy、框架和数据加载 worker 各有状态；另一类是并行计算本身的数值顺序。浮点加法不严格满足结合律，归约顺序改变就可能产生微小差异，训练还可能逐步放大它。

例如同一个 batch 用不同数量设备做求和，顺序变化后末位不同。为了定位代码回归，我会先固定单一环境、数据版本与样本顺序，设置各随机源，启用确定性算法并处理不支持的算子；要评估模型方法，则还会比较多个 seed 的均值和波动。

## 追问

**确定性算法一定更快吗？**
不一定。限制算子实现可能牺牲 throughput，也可能在没有确定实现时直接报错。

**只保存模型权重能继续复现训练吗？**
通常还需优化器、调度器、混合精度状态、随机数状态，以及数据进度。

**逐位一致和结论可复现是一回事吗？**
不同。前者要求数值完全相同，后者关注独立运行后方法优劣和指标范围是否稳定，要提前明确目标。
