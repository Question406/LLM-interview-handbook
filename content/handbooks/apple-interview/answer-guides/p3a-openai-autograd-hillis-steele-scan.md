---
id: p3a-openai-autograd-hillis-steele-scan
kind: coding
situation: matrix prefix product 要保留非交换的乘法顺序。
task: 实现扫描及其 backpropagation。
approach: 结合律只允许重分组，不允许交换左右因子。
result: 用自动求导对照，检查非交换 matrix 与容差。
---

## 可以这样回答

matrix prefix product 要保留非交换的乘法顺序。

我会保存 forward prefix product，backward 从后往前累积每个输出传回的 gradient，再按 matrix 乘法的左右顺序求导。Hillis–Steele 每层读上一层副本，用结合律并行合并；比如左块与右块交换会算错，浮点结果则用容差比较。

测试时，我会用自动求导对照，检查非交换 matrix 与容差。
