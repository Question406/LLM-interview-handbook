---
id: coding-layernorm
kind: coding
situation: 每个 token 需要独立的特征 normalization。
task: 沿最后一维计算均值方差与仿射变换。
approach: 使用总体方差和 eps，保留 gamma/beta 可学习。
result: 对照参考实现，测试常数输入和 gradient。
---

## 可以这样回答

每个 token 需要独立的特征 normalization。

对 $[B,T,D]$ 的每个 token，沿 $D$ 减均值、除以 $\sqrt{\sigma^2+\varepsilon}$，再乘 $\gamma$ 加 $\beta$。统计量只来自这个 token 的特征，方差除以 $D$，训练和推理都不依赖 batch 统计。

测试时，我会对照参考实现，测试常数输入和 gradient。
