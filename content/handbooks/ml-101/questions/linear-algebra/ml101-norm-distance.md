---
id: ml101-norm-distance
section: linear-algebra
order: 2
level: A
title: "L1、L2 范数和距离度量怎么选择？"
quick: "L1 把各维绝对差相加，L2 把平方差相加再开方，距离可写成两向量之差的范数。选择前先确认特征尺度和差异的业务意义；需要对旋转保持不变时 L2 更合适，沿坐标逐项累计差异时可以比较 L1，并用任务效果验证。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "NumPy: numpy.linalg.norm"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html
    type: primary
---

我会先看差异该怎样累计，再选 L1 或 L2，并先处理各维单位不一致的问题。比如差向量是 $(3,4)$，L1 距离是 7，L2 距离是 5；两者衡量的是同一组差异，只是累计方式不同。

对实向量 $x\in\mathbb R^d$，两种范数是

$$
\|x\|_1=\sum_{i=1}^{d}|x_i|,
\qquad
\|x\|_2=\sqrt{\sum_{i=1}^{d}x_i^2}.
$$

$x_i$ 是第 $i$ 维坐标，范数衡量一个向量的大小。要衡量 $u$ 与 $v$ 的差，就计算 $d_p(u,v)=\|u-v\|_p$，其中 $p=1$ 或 $2$。这两种距离都满足非负、相等时为零、对称和三角不等式。向量范数与矩阵范数的接口区别见 [NumPy norm 文档](https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html)。

L1 沿坐标轴累计绝对差，L2 对应几何上的直线距离，并且正交旋转坐标后不变。一次大的单维误差和许多小误差，在两种度量下的相对排序可能不同。例如 $(5,0)$ 与 $(3,3)$ 的 L1 分别为 5、6，L2 却分别为 5、$\sqrt{18}$。因此要按问题比较，不能只凭名字选。

我会先确认尺度：一维是金额、一维是次数时，原始数值大的维度容易主导距离。可以根据任务设权重，或在训练集拟合缩放规则，再应用到验证和测试数据；缩放本身也是在定义「哪些差异更重要」。最终用检索、聚类或预测的实际目标验证选择。

## 追问

**L2 范数的平方也算距离度量吗？**
严格说不算。平方欧氏距离不满足三角不等式：实数 0、1、2 上，$|0-2|^2=4$，却大于 $|0-1|^2+|1-2|^2=2$。它仍可用于损失函数，但不能直接套用依赖度量性质的证明。

**对矩阵调用 norm，默认也是谱范数吗？**
不是。NumPy 对二维矩阵默认返回 Frobenius 范数，即所有元素平方和再开方；`ord=2` 才返回最大奇异值，也就是矩阵谱范数。要明确当前算的是向量长度、矩阵元素总体大小，还是线性变换的最大放大率。
