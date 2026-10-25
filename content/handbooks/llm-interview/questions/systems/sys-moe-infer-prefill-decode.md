---
id: sys-moe-infer-prefill-decode
section: systems
order: 38
level: A
title: MoE 推理时 prefill 和 decode 为什么不能共用训练那套 Grouped GEMM？
quick: "Prefill 的每专家 token 数 $n_i$ 较大，Grouped GEMM 能充分利用 GPU；decode 每轮每请求只有一个 token，$n_i$ 常是个位数，读权重和 kernel 启动就更贵。两者应按规模选择算子，decode 通常换 fused MoE kernel，并使用适合短消息的 dispatch。"
tags:
  - MoE
  - Inference
  - Prefill
  - Decode
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

Prefill 和 decode 的每专家输入规模不同，所以通常要换不同算子。Prefill 的 token 多，Grouped GEMM 能接近训练时的效率；decode 每轮每个请求只产生一个 token，读 $k$ 个专家权重的带宽和 kernel 启动开销就很突出。MoE 省下了激活计算量，并不能据此保证小 batch decode 比 Dense 更快。

## Prefill 先看每专家的 token 数

一段长 输入提示（prompt），$T$ 大。Router → dispatch → 本地专家 MLP → combine，和训练前向同一条数据路径。$n_i$ 上百时 grouped GEMM 吃得饱，见 `sys-moe-grouped-gemm`。EP 的 all-to-all 按 $2k\cdot T\cdot d$ 摊，消息够长。这时 MoE 相对同激活 Dense 的优势看得见：总参数更大，但激活 FFN 只有 $k$（加 shared）路。

batch 里各序列长度不同，再加上 **chunked 输入预填充（prefill，即处理输入并建立缓存）**：微批一切，专家直方图跟着变，capacity / drop 若和训练不一致，首字质量会漂，见 `sys-moe-train-infer-routing-mismatch`。Prefill 仍建议 dropless 或 CF 与训练同档，不要为了吞吐在 prompt 阶段丢 token。

## Decode 先看读权重与启动开销

一步 逐 token 生成（decode）：每个活着的请求一个 token。即使连续 batch 到 $B=64$，摊到 $N=64$ 个专家上期望 $n_i\approx kB/N$，常常是个位数。此时：

- Grouped GEMM 的 $m$ 太小，Tensor Core 空转；
- 每个专家一份 $W$ 要从 HBM 读进来，**激活省了，权重流量没省**。稀疏的是计算，不是参数搬运；
- Python 循环 $N$ 次或变长 all-to-all 的 handshake 比 GEMM 还贵；
- CUDA graph 讨厌每步变化的 $n_i$ 和目的 rank 集合。

工程默认改成 **fused MoE kernel**：一个 kernel 里做 router、按 expert 分拣、现场 GEMM、加权写回。EP 仍在，但要用推理专用 dispatch（短消息、预分配 buffer），而不是训练的 DeepEP 图。Shared expert 每 token 必算，decode 时它是固定的一块带宽，过大就把稀疏红利吃掉，见 `arch-shared-expert`。

小 batch、单卡、专家全驻留时，甚至可以「把命中的专家权重 gather 成一块再一次 GEMM」，避免 $N$ 次启动。专家不在本地时，decode 的 EP 延迟是 P99 来源：一个 token 等最慢的那台专家卡。Device-limited routing 在推理同样要开，见 `sys-moe-node-limited-routing`。

和 Dense 比较时，要把两种阶段分开计时。

同激活 FLOPs 的 MoE 在 **大 prefill、大 batch** 时更快或接近；在 **小 batch decode** 时经常更慢，因为多读了 $k$ 套专家权重和一次不规则通信。面试报「671B 激活 37B 所以 decode 像 37B」是算力账，不是延迟账。延迟看：权重字节 / HBM 带宽、EP hop、kernel 次数。

评测时分别报告 prefill tokens/s、decode tokens/s、TPOT P99 和每层专家命中直方图。平均 tokens/s 可能被一条超长 prefill 拉高，掩盖 decode 的延迟问题。

## 追问

**CUDA graph 怎么抓？**
把 decode 的 $B$ 分档（$1,2,4,\ldots$），每档一张图；路由集合仍动态时只能 fused kernel 内部分拣，不能每专家一个 graph 节点。
**量化？**
专家权重量化直接减 decode 带宽。Router 保持高精度，避免 Top-$k$ 翻转，见训推不一致卡。
**PD 分离？**
Prefill 机用训练像的 grouped GEMM；decode 机用 fused + 更激进量化。两台路由实现必须字节级对齐，否则 KV 能复用、专家却走错。
**$k=1$ 对 decode 更友好吗？**
少读一套权重、少一次 combine。更脆。Mixtral 用 $k=2$ 是质量折中，不是 decode 最优。
