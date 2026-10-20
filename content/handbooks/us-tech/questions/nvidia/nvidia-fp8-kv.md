---
id: nvidia-fp8-kv
section: nvidia
order: 17
level: A
title: NVIDIA：FP8 KV cache 和权重量化不是一回事
quick: "权重量化减的是每步读 $W$ 的字节；FP8 KV 减的是常驻 cache 和 decode 时读历史 K/V 的字节。两者 scale、kernel、误差都不同，TensorRT-LLM 里也是两个开关。"
tags:
  - NVIDIA
  - FP8
  - KV Cache
  - TensorRT-LLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Quantization in TensorRT-LLM
    url: https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/blogs/quantization-in-TRT-LLM.md
    type: primary
  - title: FP8 Quantization — TensorRT-LLM Performance Tuning
    url: https://nvidia.github.io/TensorRT-LLM/performance/performance-tuning-guide/fp8-quantization.html
    type: primary
  - title: Quantization — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/features/quantization.html
    type: primary
  - title: NVIDIA TensorRT-LLM Supercharges Large Language Model Inference on NVIDIA H100 GPUs
    url: https://developer.nvidia.com/blog/nvidia-tensorrt-llm-supercharges-large-language-model-inference-on-nvidia-h100-gpus/
    type: secondary
---

## 题怎么来的

刚答完 `nvidia-fp8` 或 `nvidia-int8-quant`，评委常补一句「那 KV 呢」。权重已经 FP8 / INT4，长上下文 逐 token 生成（decode） 仍可能被 cache 打满。TensorRT-LLM 文档把 KV 量化写成独立开关，甚至允许 checkpoint 没开 FP8 KV、runtime 再打开。我会先写两笔显存账，再谈 scale 和误差落在哪。

## 两笔账、两堵墙

Decode 每步都要：(1) 读一层权重做 GEMM；(2) 读历史 KV 做 attention。字节：

$$
\mathrm{KV}\approx 2\cdot L\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot b,\qquad
W\approx \sum |W|\cdot b_W.
$$

$T$ 短、$B$ 小：读 $W$ 往往是主项，权重量化（W8A16、FP8 权重、INT4 AWQ）对症。$T$ 长或并发高：KV 线性涨，权重每步不变，墙转到 cache。$b$ 从 2（fp16）收到 1（FP8），同样 HBM 能塞大约 2 倍 token 或更大 batch；读 KV 的带宽也减半。官方量化博客写过：GPT-J 一类从 fp16 KV 换 FP8 KV，H100 上 batch 可以到 2-3 倍，吞吐再跟一截。这和「权重 FP8 让 Tensor Core 更快」不是同一条 roofline。

所以可以出现四种组合，面试要能分开：

- 权重 fp16、KV FP8：纯为了长上下文容量。
- 权重 FP8、KV fp16：小 batch、短上下文，先加速 GEMM。
- 两者都 FP8：Hopper serving 常见。
- 权重 INT4、KV FP8：容量和读 $W$ 都狠，激活 / attention 仍可能较高精度。

训练时的 FP8（Transformer Engine、延迟缩放、E4M3 / E5M2 分工）对的是正向 / 反向 GEMM，见 `nvidia-fp8`。KV cache 根本不参与反传。不要说「我们训了 FP8，所以 serving 的 cache 自动是 FP8」。

## Scale 和误差不在同一个张量上

权重量化：离线 PTQ，per-tensor 或 per-channel $s_W$，GEMM 里 $x_{\mathrm{fp8}} W_{\mathrm{fp8}}$，累加器 fp32 再 rescale。Outlier 在通道上，SmoothQuant / AWQ 那套故事，见 `nvidia-int8-quant`。

KV 量化：K、V 是运行时写进去的激活，每步多一行。Scale 常常 per-tensor 粗、或沿 token / 通道更细。Attention 是 $QK^{\top}$，K 的误差直接进 logits；softmax 对少数过大的 logit 很敏感。V 的误差进加权和，相对钝一点。乱套「和权重同一个 per-tensor INT8」容易把长上下文注意力打崩。TRT-LLM 建议 Hopper / Ada 上 KV 用 FP8 而不是 INT8：E4M3 的动态范围对 cache 更友好，实测精度打击通常小于 INT8 KV。Ampere 没有原生 FP8 MMA，仍可能 FP8 存、算前转回。那是带宽收益，不是 Tensor Core 收益。

写 cache：attention plugin 可以在核内把新 K/V cast 成 FP8 再落到 paged block。读 cache：dequant 后和 $Q$ 做点积，或走 FP8 attention。Paged 布局见 `nvidia-paged-kv`。Scale 要跟块一起存，否则 gather 回来无法还原。

## 什么时候不要开

质量回归：长上下文检索、agent 多跳、logits 对小数敏感的评测，先 A/B，不要只看 GSM8K。Decode 已经不是 KV 带宽墙（极小 $T$、权重还是 fp16 大模型），KV FP8 对 TPOT 几乎没感觉，只省容量。Blackwell 上还有 NVFP4 KV 等更窄格式，和权重 FP4 仍是两套开关。引擎怎么挂这些开关见 `nvidia-trt-llm`。

## 追问

- **打开权重量化就等于 KV 也 FP8 吗？** 不等于。要另设 `kv_cache_quant_algo` 或 runtime 的 KV dtype。
- **GQA 还要量化 KV 吗？** $H_{\mathrm{kv}}$ 已经小了，容量压力轻一档，但 $T$ 到 128k 仍值得。GQA 减头数，FP8 减字节，正交，见 `google-gqa-mqa`。
- **和 INT4 权重叠会不会崩？** 两套误差相乘。先单独开、再组合评测。崩了先看 K 的 scale 是不是太粗。
- **训练 FP8 的 amax 能不能当 KV scale？** 不能。训练 amax 是层激活历史；KV 是每条请求自己的 K/V 分布，还随 $T$ 长。

## 相关题

- [[sys-kv-quant]]：同一主题的系统版，更细讲 K 按 channel、V 按 token 定 scale 的原因，以及 INT8 和 FP8 怎么选。
- [[nvidia-w4a8]]：把权重、激活、KV 三把量化开关放在一张表里，和本题的「两笔账」是同一个思路的扩展。
- [[nvidia-kv-offload]]：KV 容量不够时的另一条路，算 PCIe 带宽为什么让热 KV 只能留在 HBM、先上 FP8。
- [[nvidia-fp8]]：本题开头要区分的 FP8 训练配方，延迟缩放和 amax 历史都在那边。
- [[sys-fp8-gemm]]：FP8 用在权重 GEMM 上的 scale 粒度和核，对应本题说的「权重量化」那笔账。
- [[nvidia-int8-quant]]：常作为本题前一问的权重 INT8 量化，对称/非对称和校准都针对 GEMM 的权重和激活。
