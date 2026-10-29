---
id: dt-p3a-paper-gated-layer
kind: coding
situation: 论文公式尚未转为明确 tensor 运算。
task: 写出可训练的 gated residual layer。
approach: 先核对 matrix 方向和广播，再注册参数。
result: 手算初值，检查参数更新与自动求导。
---

## 可以这样回答

论文公式尚未转为明确 tensor 运算。

先澄清 tensor 形状、matrix 乘法方向、广播与 parameter sharing，再从公式写 forward。用可手算的初始状态检查输出，用 gradient 和参数注册检查能否真正训练；本题公式自拟，原帖未公开论文或层名。

测试时，我会手算初值，检查参数更新与自动求导。
