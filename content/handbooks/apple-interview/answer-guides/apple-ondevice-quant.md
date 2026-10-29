---
id: apple-ondevice-quant
kind: design
situation: 低比特可能破坏数值和关键算子行为。
task: 估算收益并定位 quantization 误差。
approach: 权重/KV 分别做 calibration，检查 mask 与设备支持。
result: 同设备质量、内存和延迟支持方案。
---

## 可以这样回答

低比特可能破坏数值和关键算子行为。

权重 palettization、激活和 KV quantization 要分别看：2024 公开方案混合 2/4-bit 权重、约 3.7 bpw，KV 用 8-bit，再用 LoRA 恢复质量。ANE 上 mask 应在反 quantization 后加 fp16 有限大负数，检查非法位置的 softmax 是否为零，避免 $-\infty$ 和 int8 截断导致错误。
