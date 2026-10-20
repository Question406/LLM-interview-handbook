---
id: sys-kv-quant
section: systems
order: 9
level: A
title: 系统：KV cache 量化（INT8/FP8），outlier 和注意力质量
quick: "Decode 的 HBM 大头常是 KV，不是权重。INT8 / FP8 把每个 token 的 K/V 压窄，容量和带宽一起省。K 的 outlier 沿通道、V 沿 token，所以 K 常 per-channel、V 常 per-token。Softmax 对 K 的误差更敏感。"
tags:
  - NVIDIA
  - Quantization
  - KV Cache
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache"
    url: https://arxiv.org/abs/2402.02750
    type: primary
  - title: "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization"
    url: https://arxiv.org/abs/2401.18079
    type: primary
  - title: SmoothQuant — Accurate and Efficient Post-Training Quantization for Large Language Models
    url: https://arxiv.org/abs/2211.10438
    type: primary
  - title: Quantization — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/features/quant.html
    type: secondary
---

## 题怎么来的

NVIDIA TensorRT-LLM、vLLM、长上下文 serving 都会问：权重已经 FP8/INT4 了，为什么还要动 KV。权重量化见 `nvidia-int8-quant`，FP8 配方见 `nvidia-fp8`；本题只谈 cache。OpenAI 式追问是 outlier 在哪一维、为什么乱 per-tensor INT8 会把注意力打崩。

## 为什么 KV 值得单独量化

Decode 每步都要把历史 K/V 从 HBM 读进 SM。序列变长，KV 流量线性涨，权重流量不变，所以长上下文逐 token 生成（decode）更受内存带宽限制。一份 KV 的字节大约 $2\cdot L\cdot n_{\mathrm{kv}}\cdot d_h\cdot T\cdot b$。把 $b$ 从 2（FP16）收到 1（FP8/INT8）或 0.5（INT4），同样显存能塞更长 $T$ 或更大 batch，带宽也减半。这和权重量化正交：GPTQ/AWQ 减的是读权重；KV 量化减的是读 cache。

FP8（E4M3 / E5M2）动态范围比 INT8 友好，Hopper / Blackwell Tensor Core 原生吃 FP8，TensorRT-LLM 线上很常见。INT8 更通用，scale 要自己管。再低到 2/4 bit 是 KIVI、KVQuant 那条研究线，serving 上要有对应 kernel 才有实际耗时，不是 bit 降了一定更快。

## Outlier 不对称，所以 K 和 V 不能同一套 scale

激活 outlier 是 SmoothQuant 的故事：少数通道幅度极大，per-tensor 量化把有效比特浪费在那几个峰值上。KV 里更具体：

- **K 的 outlier 多沿 channel。** 某些 hidden 维长期很大。Per-token 一个 scale 救不了这些通道；应对 channel 维（或很小的 group）做 scale。KIVI 把 K 做成 per-channel 低比特，就是这个观察。
- **V 的 outlier 多沿 token。** 某个 token 的 value 整体偏大。V 更适合 per-token scale。

注意力里 $QK^{\top}$ 的误差会进 softmax，再去加权 $V$。K 量化噪声会被 softmax 放大成错误的权重分布；V 量化噪声更像加权和上的加性误差。同样 bit 下，K 通常比 V 对误差更敏感。实务常见：K 用更高精度或更细的 scale，V 可以压到更低比特；或两边都 FP8，但 K 用 per-channel amax。

Per-tensor INT8 是面试里的错误答案：一条序列一个 scale，outlier 通道把格子撑满，其余通道只能映射到少数几个量化值，长上下文的针点检索先坏。校准不要只看 PPL：要看长上下文检索、复制、多轮是否还对。PPL 对局部量化噪声不敏感。

KIVI 一类还会把**最近若干 token 留在高精度**（sliding window），只把更早的 KV 打到 2/4 bit。Decode 对最近 token 最敏感，这个不对称往往比「全序列同一 bit」更稳。没有对应 dequant kernel，低比特只是占着窄存储，算的时候仍要还原成 FP16，预期的带宽收益就可能无法实现。

服务上还要看 kernel 是否 fused：先 dequant 再走 FP16 attention，等于多读一遍；真正吃到 INT8/FP8 带宽，必须是 paged attention 直接吃量化页。NVIDIA 岗会追 Nsight 里是 dequant 带宽还是 Tensor Core。

和 FlashAttention / paging 叠：量化发生在写入 KV 页时，kernel 按 block table 读回低比特再 dequant 进点积。页可以是 FP8，寻址仍是 `sys-paged-attn` 那套。PD 分离时，量化后再搬 KV，网络体积一起降，见 `sys-prefill-decode-disagg`。

## 追问

- **INT8 和 FP8 怎么选？** 硬件有 FP8 Tensor Core 就优先 FP8，动态范围更好、kernel 现成。只有 INT8 通路、或要和 CPU offload 互通时用 INT8 加细粒度 scale。
- **为什么不直接用 SmoothQuant 的 W8A8 顶替 KV 量化？** W8A8 管的是 GEMM 的权重和激活。KV 是跨 step 存下来的缓存，生命周期和 scale 统计都不同。
- **2bit KV 能上线吗？** KIVI 一类显示很多模型仍能保持可用质量，但要 grouped scale、残差处理，且必须有 kernel。没有 kernel 就 dequant 回 FP16，带宽没省到。
- **质量先坏在哪？** 长上下文找针、依赖精确匹配的复制。先看任务，不要只看 PPL。
- **Group size 怎么选？** 越小越准、元数据越多。Channel group 32/64 常见。Window 太大，最近 token 的高精度优势被稀释；太小，kernel 切换碎。
- **和权重量化一起开注意什么？** Scale 不要共用。权重 per-channel 的 amax 救不了 K 的 channel outlier；KV 要单独校准。
- **记不住 per-token / per-channel？** K 的 outlier 沿 channel，V 沿 token。scale 轴跟 outlier 轴走，这一句够画图。
- **Decode 变长时 scale 要不要重算？** 历史页的 scale 冻结；只给新 token 算新 scale。回过头重量化整段 KV 太贵。

## 相关题

- [[nvidia-fp8-kv]]：同一题的 NVIDIA 问法，重点是 KV 量化和权重量化是两笔显存账、TRT-LLM 里两个开关；本题更细讲 K/V 的 outlier 轴。
- [[apple-ondevice-kv]]：端侧版本，墙从 HBM 换成手机 DRAM，先估 KV 字节再看 GQA 和 8-bit 各省多少。
- [[nvidia-kv-offload]]：KV 放不下时另一条路是卸到 CPU/NVMe，那题算的是什么时候带宽还不如量化。
- [[nvidia-w4a8]]：把 W4、A8、KV 三种量化放在一起对账，适合答完本题后被问「和权重量化一起开」。
- [[apple-ondevice-quant]]：端侧权重 palettization 加 8-bit KV 的整套配方，外加 ANE 上 mask 的数值坑。
- [[sys-kv-offload]]：KV 容量的另一条路，把冷前缀分层放到 CPU 和盘，前提是在飞的 decode 页留在 HBM。
