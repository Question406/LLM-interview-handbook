---
id: p3a-apple-cvml-circular-padding
kind: coding
situation: image boundaries 需要环绕而非补零。
task: 实现可求导的二维周期填充。
approach: 用模索引处理大 padding 与任意空间维。
result: 手算边角，检查超宽 padding 和 gradient 累加。
---

## 可以这样回答

image boundaries 需要环绕而非补零。

把输出行列映射到原图的模索引，再用 index_select 取值。这样能处理非对称及超过图像尺寸的补边，并保留 gradient；环形补边会改变 boundary conditions，不能不加分析地替换普通图像的零补边。

测试时，我会手算边角，检查超宽 padding 和 gradient 累加。
