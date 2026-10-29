---
id: coding-gumbel-max
kind: coding
situation: 硬 sampling 与连续松弛中的温度含义不同。
task: 分别实现指定分布与 differentiable 近似。
approach: 明确噪声加在缩放前还是缩放后。
result: 检查频率分布及固定噪声下 argmax 行为。
---

## 可以这样回答

硬 sampling 与连续松弛中的温度含义不同。

硬 sampling 先缩放 logits，再用 argmax(z/τ+g)，得到 temperature sampling。Gumbel-softmax 松弛用 softmax((z+g)/τ)，它的 τ 只改变连续输出和 gradient，在固定噪声下不改变选中的类别。

测试时，我会检查频率分布及固定噪声下 argmax 行为。


本题已经沿最后一维支持 `[B,V]` 等 batch 单步选择，但没有多步生成。使用同一 Gumbel 方法的完整 batch loop 见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-generation)。
