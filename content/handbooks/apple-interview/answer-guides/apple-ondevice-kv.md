---
id: apple-ondevice-kv
kind: design
situation: long contextKV 占用内存并受带宽限制。
task: 计算 cache 预算并比较压缩方案。
approach: 从层数、KV heads、长度和精度逐项估算。
result: 理论字节与实际 profiling 一致，质量回归可接受。
---

## 可以这样回答

long contextKV 占用内存并受带宽限制。

on-device decode 每步读取历史 KV，显存和带宽可先按 $2 L H_{\mathrm{kv}} d_h S b$ 估算。GQA 减少 KV head，8-bit cache 减少每元素字节，2025 公开的跨块 KV 共享再减少有效存储深度；long context 要重点检查手机 DRAM / ANE SRAM 的预算。
