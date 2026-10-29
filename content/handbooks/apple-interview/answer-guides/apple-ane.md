---
id: apple-ane
kind: design
situation: on-device 硬件限制形状与算子。
task: 把模型设计落到可运行图。
approach: 先核对算子支持和静态预算，再选近似。
result: 实际设备 profiling，而非仅凭理论 FLOPs。
---

## 可以这样回答

on-device 硬件限制形状与算子。

我会按 ANE 能编译的静态图来设计 Transformer：固定 shape 和 KV 槽位，采用合适的布局、算子与 dtype，再验证整网是否驻留。某层回退到 CPU/GPU 会增加拷贝和耗电，quantization 之前先把这类问题定位清楚。
