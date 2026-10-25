---
id: apple-ane
section: apple
order: 7
level: S
title: Apple：Neural Engine 约束（静态 shape、算子白名单）对 Transformer 设计的影响？
quick: "我会按 ANE 能编译的静态图来设计 Transformer：固定 shape 和 KV 槽位，采用合适的布局、算子与 dtype，再验证整网是否驻留。某层回退到 CPU/GPU 会增加拷贝和耗电，量化之前先把这类问题定位清楚。"
tags:
  - Apple
  - Neural Engine
  - Transformer
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Deploying Transformers on the Apple Neural Engine
    url: https://machinelearning.apple.com/research/neural-engine-transformers
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: On-Device Llama 3.1 with Core ML
    url: https://machinelearning.apple.com/research/core-ml-on-device-llama
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Transformer 上 ANE，要先围绕静态 shape、算子和布局改计算图，再检查整网是否驻留。比如 decode 每步把 KV `torch.cat` 长一格，在 GPU 上很自然，在静态图里就需要预分配槽位或另设更新路径；回退到 CPU/GPU 还会引入拷贝，影响原本约 30 token/s 的目标。

Apple 2022 的指南讲了 Transformer 的 ANE 部署，2024 AFM 也明确端侧运行于 Neural Engine，并提到高效 KV 更新。设计时我会先问上下文上限、当前讨论 prefill 还是 decode，再画训练 GPU 图、导出前 ANE 图和运行时 cache 状态。

## 先把图改成硬件能执行的形状

静态路径里输入、输出、中间张量的 shape 要固定，上限记作 $S_{\max}$。KV 可预分配为 $[B,H_{\mathrm{kv}},S_{\max},d_h]$，按 position 写入槽位；也可以只读 cache、外置拼接，模型只返回本步新 $k,v$。Core ML stateful 模型把 KV 注册为跨 `predict` 保留的 state，编译产物往往按 `(context_len, extend_len)` 提供多个入口。

ANE 偏好卷积，`Linear` 的 $[B,S,D]$ 常改写成 $1\times 1$ Conv2d，激活排成 $[B,D,1,S]$，也就是 BC1S，接近 $[B,C,1,S]$。最后一维按 64 字节对齐，设成 1 可能引起大量 padding；Rank 超过 5 会被拒。主要 dtype 是 fp16/int8，一个 fp32 字面量也可能生成无法放在 ANE 的缓冲，把整段切到 GPU。

不支持的 gather、动态分支或 softmax 轴会让编译器切图，小模型上拷贝可能比计算更贵。公开实现按 head 拆 softmax 来保住 L2，mask 用有限大负数，避免 $-\infty$ 带来的问题。有的 score 写成 $KQ$，mask 也得跟着转置；照搬 $QK^\top$ 的 GPU 布局可能悄悄算错。

## 再确定模型和运行策略

AFM on-device 用 GQA、共享输入输出 embedding 和 49k 词表，以减少 KV 带宽和驻留压力。prefill 可固定为每次 64 或 128 个新 token，变长 prompt pad 到下一档并用 mask 遮住；档位太稀浪费算力，太密又增大二进制。

decode 尽量去掉数据依赖控制流，固定 $k$ 的 top-k 比可变 nucleus 好处理。MoE 或条件 adapter 要静态限定 max expert，或在 CPU 换 weight 后再跑静态段。AFM 的基础模型保持固定，热插拔的是几十 MB 的 LoRA。KV 更新同样要用支持的 slice，随机 scatter 可能回退。

2025 的 KV sharing 把模型分两块，第二块复用第一块末层 KV，cache 降约 37.5%，prefill 还能跳过第二块。视觉侧 HyperDETR 也通过解耦 decoder 与 Transformer 路径，用 $1\times 1$ 动态卷积出 mask，让整网留在 ANE。这些例子说明模块边界本身也可以为硬件调整。

验收时用 Talaria 看每层时延和能量、指导 palettization，再用 Instruments / Core ML 检查 compute unit。greedy 输出要与 CPU 参考逐 token 对齐。手写 LayerNorm 掉 CPU、$-\infty$ mask 出 NaN、nucleus 回 CPU 花几毫秒，都应具体定位到 shape、dtype 和算子支持。

## 追问

**为什么不一直用 GPU？**
后台常驻的 Siri、输入法重视功耗和带宽，ANE 提供能效路径。Core ML 的 Llama 3.1 文在 Mac 走 GPU，属于另一条产品线，不能套到 iPhone AFM。

**动态 shape 将来更灵活，还要固定档位吗？**
这道设计题仍按静态档位展开，即使运行时弹性增加，产品也需要可预测的时延。

**能直接上 FlashAttention 吗？**
不能直接搬 CUDA tiling。这里要找编译器支持的切头 softmax 和驻留方式。

**算子不支持怎么办？**
改成 Conv、高阶 LayerNorm 或静态 slice；必须在 CPU 做的部分移出热路径。先查 compute unit，采样优先比较固定 top-k 与可变 nucleus，再决定改图。

相关：`apple-ondevice-quant`、`apple-topk-sample`、`google-gqa-mqa`、`apple-personalize`、`apple-siri-latency`
