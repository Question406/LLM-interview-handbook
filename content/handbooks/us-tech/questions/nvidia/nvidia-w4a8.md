---
id: nvidia-w4a8
section: nvidia
order: 23
level: A
title: NVIDIA：W4A8 和 KV 量化、激活量化不是一把开关
quick: >-
  W4 砍的是每步读权重；A8 砍的是 GEMM 里的激活带宽和 Tensor Core 格式；KV 量化砍的是 cache 容量和
  attention 读历史。TensorRT-LLM 的 `w4a8_awq` 和 `kv_cache_quant_algo` 分开配。W4A8 的
  A 通常是 FP8 不是 INT8。三套 scale、三种误差，别说「都量化了」。
tags:
  - NVIDIA
  - W4A8
  - Quantization
  - TensorRT-LLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Optimizing LLMs for Performance and Accuracy with Post-Training Quantization
    url: https://developer.nvidia.com/blog/optimizing-llms-for-performance-and-accuracy-with-post-training-quantization/
    type: secondary
  - title: Quantization — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/features/quantization.html
    type: primary
  - title: AWQ — Activation-aware Weight Quantization
    url: https://arxiv.org/abs/2306.00978
    type: primary
  - title: SmoothQuant — Accurate and Efficient Post-Training Quantization
    url: https://arxiv.org/abs/2211.10438
    type: primary
---

## 题怎么来的

刚讲完 `nvidia-int8-quant` 或 `nvidia-fp8`，评委常抛配方名：W4A8、W4A16、FP8 KV。NVIDIA 博客和 TensorRT-LLM 量化表把它们列成不同列：W4A8 AWQ / GPTQ、W4A16、FP8 权激、FP8 KV、NVFP4 KV。我会先画三笔字节账，再讲 scale 落在哪个张量上。ModelOpt 出 checkpoint，引擎只是吃核，见 `nvidia-trt-llm`。

## 三笔账

Decode 一步，每层大致要搬：

$$
W:\ |W|\cdot b_W,\qquad
x:\ N\cdot D\cdot b_A,\qquad
\mathrm{KV}:\ 2\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot b_{\mathrm{KV}}.
$$

$N$ 是这一步的 token 数（纯 decode 接近瞬时 $B$）。三套比特互相独立：

- **权重 $b_W$。** 小 batch decode 是内存墙，读 $W$ 往往最大。INT4 相对 fp16 是 $1/4$ 的权重流量。W4A16（AWQ / GPTQ）只做这件事，激活仍 fp16/bf16，GEMM 是 mixed-dtype。
- **激活 $b_A$。** Prefill 或大 $N$ 时 GEMM 变算力墙，激活也量化才能喂 INT8 / FP8 Tensor Core。W4A8 在 NVIDIA 栈里通常是 **INT4 权重 + FP8 激活**（`w4a8_awq`），不是 INT4 乘 INT8。W8A8 才是 SmoothQuant 那条 INT8 权激。
- **KV $b_{\mathrm{KV}}$。** 跟线性层激活不是同一个张量。长 $T$ 时 attention 读历史压过读 $W$。FP8 KV 把 cache 和这段带宽减半，开关叫 `kv_cache_quant_algo`，见 `nvidia-fp8-kv`。

所以「开了 W4A8」只保证线性层的 $W$ 和 $x$；KV 可能仍是 fp16。反过来，只开 FP8 KV、权重仍 fp16，短上下文小 batch 对 TPOT 几乎没感觉。

| 配方 | 读 $W$ | GEMM 格式 | KV | 典型墙 |
|---|---|---|---|---|
| W4A16 | $\times 1/4$ | mixed，激活 16 | 另设 | 小 $B$ decode |
| W4A8 | $\times 1/4$ | W4$\times$FP8 | 另设 | decode + 要吃 Tensor Core |
| FP8 W8A8 | $\times 1/2$ | Hopper FP8 MMA | 另设 | 大 $N$ / Hopper |
| INT8 SQ | $\times 1/2$ | INT8 MMA | 另设 | Ampere 权激 |
| FP8 KV | 不变 | 不变 | $\times 1/2$ | 长 $T$ 容量 |

## Scale 不在同一个轴上

**W4：** 离线 PTQ。AWQ 按激活幅度保护显著通道，group size 常见 128，每组一个 $s_W$。GPTQ 是逐列残差量化。反量化在 GEMM 里和 $x$ 乘，累加器仍高精度。

**A8：** 运行时对当前 token（或 per-tensor）量化激活。W4A8 路径里常有 `pre_quant_scale`（AWQ 的平滑）再 cast 成 E4M3，再和 INT4 权重做 mixed GEMM，输出再乘 $\alpha$。激活 outlier 仍在：只压权重不够时，要么 SmoothQuant 把幅度迁到 $W$，要么别走太窄的 $A$。

**KV：** K/V 是注意力写出的，每步多一行。Scale 跟 paged block 走。K 的误差进 $QK^{\top}$，对 softmax 更狠；V 钝一些。和 $W$ 的 group scale **不能共用**，校准数据也不是同一批张量。训练 FP8 的 amax 更不能拿来当 KV scale，见 `nvidia-fp8`。

错法：把 W4A8 说成「KV 也是 4 bit」。那是 NVFP4 KV 之类的第三条配方，质量口子要单独评。

## 什么时候选哪条

小 $B$、短 $T$、70B 级：先 W4A16 或 W4A8，墙在读 $W$。Hopper 上 W4A8 比 W4A16 多一次激活量化，Nsight 看 SOL：若已经是内存墙，A8 的收益可能被 quant kernel 吃掉，要以实测为准。

长上下文、并发高：先 FP8 KV（或 GQA），否则 W4 再省也塞不下 cache。显存仍不够，才轮到卸载，见 `nvidia-kv-offload`。卸载的带宽比量化差一个数量级，能用 $b_{\mathrm{KV}}$ 解决就不要把热 KV 赶到 PCIe 上。

质量：W4 伤 MLP 的通道；KV 伤长距离注意力。分开 A/B，再组合。TRT-LLM 表上 Hopper 支持 W4A8 AWQ，Ampere 往往只有 W4A16——没有原生 FP8 MMA 时 A8 不一定划算。

## 追问

- **A8 是 INT8 还是 FP8？** 在 NVIDIA PTQ 博客和 TRT-LLM 里，W4A8 默认按 INT4 权重 + FP8 激活讲。INT8 权激是另一列 SmoothQuant。
- **和权重 FP8 怎么比？** FP8 W8A8 权重只减半，但 MMA 整齐；W4 权重更瘦、核更不规则。容量优先 W4，Hopper Tensor Core 优先 FP8，也可以权重 W4、KV FP8 混搭。
- **激活量化会改采样吗？** 线性层误差会进 logits。先看 greedy / 短任务，再看长上下文检索。KV 量化更常在长上下文上爆。
- **group size 写成 1？** 最细、scale 开销变大、核变慢，质量不一定正比提升。128 是 AWQ 常见折中。
