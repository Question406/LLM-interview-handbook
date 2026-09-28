---
id: sys-fp8-gemm
section: systems
order: 28
level: S
title: 系统：FP8 GEMM，scaling 与 DeepGEMM 一类公开思路
quick: >-
  Hopper Tensor Core 吃 E4M3/E5M2，但 scale 粒度决定准不准、核好不好写。Per-tensor 快、怕
  outlier；DeepSeek-V3 公开的是激活 $1\times 128$ tile、权重 $128\times 128$ block。DeepGEMM
  是开源 JIT 核，不是把内部配方当自己的。
tags:
  - NVIDIA
  - DeepSeek
  - Quantization
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
  - title: deepseek-ai/DeepGEMM
    url: https://github.com/deepseek-ai/DeepGEMM
    type: primary
  - title: NVIDIA Transformer Engine
    url: https://github.com/NVIDIA/TransformerEngine
    type: primary
  - title: DeepSeek-V3 README_WEIGHTS（FP8 block scale）
    url: https://github.com/deepseek-ai/DeepSeek-V3/blob/main/README_WEIGHTS.md
    type: secondary
---

## 题怎么来的

NVIDIA H100 / Blackwell 推理岗几乎必问 FP8 GEMM。训练混合精度（延迟缩放、E5M2 梯度）见 `nvidia-fp8`；KV 的 FP8 见 `sys-kv-quant`、`nvidia-fp8-kv`。本题只谈权重点积：怎么 scale、核为什么不能当成「cast 成 fp8 再调 cublas 就结束」。DeepSeek-V3 报告和开源 DeepGEMM 是可以写在白板上的公开材料，不要编集群内部的 kernel 名或未发表配方。

## Scale 是一等公民

FP8 动态范围窄。E4M3 尾数多、范围更窄，推理权重大多用它；E5M2 指数多，训练梯度常用。没有 INT8 那个零点。一块张量要先乘 scale 再量化：

$$
x_{\mathrm{fp8}}=\mathrm{cast}(x / s),\qquad
s \approx \max(|x_{\mathrm{group}}|) / \mathrm{fp8\_max}.
$$

GEMM 在 Tensor Core 上做 $D \approx (X_{\mathrm{fp8}} s_x)\,(W_{\mathrm{fp8}} s_w)$，累加通常要回到更高精度再乘回 scale。group 有多大，决定 outlier 会不会把整块的有效比特吃光：

- **Per-tensor：** 一个 $s$。Launch 简单，cuBLAS / Transformer Engine 的入门路径。激活有通道 outlier 时，多数值被压成几个 bin，质量先坏。
- **Per-token / per-channel：** 激活按 token，权重按输出通道。比 per-tensor 稳，scale 元数据仍小。
- **DeepSeek-V3 公开的细粒度：** 激活按 $1\times 128$ tile（每个 token、每 128 通道一个 scale），权重按 $128\times 128$ block。报告写明这是为了在 FP8 窄范围里扛 outlier；权重文件里 `weight_block_size: [128, 128]`、`fmt: e4m3` 也是公开的。当时 Hopper Tensor Core 不能在 MMA 内部吃分组 scale，部分累加要出 Tensor Core 到 CUDA core 做反量化再进 FP32 累加，这就是「细粒度准、但有来回税」的来源。报告甚至建议未来硬件把 group scale 做进 MMA。

把 FP8 说成「INT8 去掉零点」不够。scale 轴必须对准 outlier 轴，和 KV 量化同一句口诀，只是这里的张量是 GEMM 的 $X$ 和 $W$，不是 cache。

Transformer Engine 训练侧常用 delayed scaling：用历史 amax，避免每步为当前 tensor 做一次同步。推理侧权重 scale 冻结，激活往往动态 per-token 或 per-tile，和训练 delayed 不是同一套统计。不要把 TE 训练故事原样搬到 serving GEMM。

## 核：形状一变就要再选路

Dense 层 $M=T_{\mathrm{tokens}}$（prefill 大、decode 的 $M=B$ 很小）、$N=K=d$ 或 $d_{\mathrm{ff}}$。Decode 的 $M$ 经常是几十到几百，FP8 Tensor Core 有最小 tile，太瘦会退回带宽墙，FP8 的 TFLOPS 广告打不出来。Prefill 和宽 MoE expert 才容易吃满。Decode 侧更该凑 batch，见 `sys-decode-batch`。

MoE 更烦：每个 expert 一块不同的 $M_i$，要 grouped GEMM 一次 launch 吃一组不规则 $M$，见 `nvidia-moe-gemm`。DeepGEMM 公开仓库写：JIT、少依赖、dense 和两种 MoE 布局、`fp8_gemm_nt` 以及 masked grouped 接口（对接 DeepEP 的低延迟输出）。这是「形状变化大、手写模板跟不上就 JIT」的公开思路，不是把某家内部调度器讲成自己的。

还要注意：

- **Layout。** Hopper 上常见 NT（$A$ row-major，$B$ 视为转置）。Layout 错了不是慢一点，是核直接不接。
- **Grouped scale 和 MMA。** Per-tensor 可以整核走 Tensor Core；tile scale 要在累加路径上插 CUDA core。Nsight 上看得到 MMA 和 FP32 管道的缝。
- **和通信叠。** MoE 的 dispatch 出 FP8 token，GEMM 直接吃，少一次 cast，见 `sys-ep-dispatch`。
- **不是 KV FP8。** 权重 GEMM 的 scale 救不了 K 的 channel outlier。两套量化、两套核。

错误说法：开了 FP8 一定 2 倍墙钟（decode 太瘦时几乎不涨）；DeepSeek 的 128 是魔法，随便改 group 不改核；用训练 delayed amax 当推理动态激活 scale。Group 大小要和核 tile 对齐，乱改会对不齐或回退到慢路径。

质量：不要只看 PPL。看长上下文、工具 JSON、数学。Scale 过粗，先坏的是尾部通道上的细信号。校准和在线 amax 要分开说：推理激活常用在线 max，权重用离线 block scale。

## 追问

- **E4M3 还是 E5M2？** 推理权重 / 激活优先 E4M3。E5M2 给更需要范围的梯度。Serving GEMM 很少把两者混在同一张 $W$ 上。
- **为什么不一直 per-tensor？** 快、实现简单，outlier 一来有效比特不够。细粒度是质量开关，代价是核更难、scale 流量更大。
- **DeepGEMM 和 cuBLAS 怎么讲？** 规则 dense 大 GEMM，厂商库往往够。不规则 MoE $M_i$、细粒度 scale，开源 JIT 核是公开选项。不要声称某内部融合没论文。
- **Decode 为什么 FP8 加速不明显？** $M$ 太小，吃不满 Tensor Core，墙在读 $W$。这时更该凑 batch，见 `sys-decode-batch`。
- **和 Transformer Engine 训练 FP8 是一回事吗？** 都是 E4M3/E5M2 + scale。训练有延迟 amax 和反传；推理权重冻结、激活动态。核和统计都不同。
- **Block 128 能改成 32 吗？** 能更准、scale 更多，但必须有对应核。没有核就先 dequant 成 BF16 再 GEMM，带宽账是假的。
