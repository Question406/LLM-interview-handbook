---
id: nvidia-w4a8
section: nvidia
order: 23
level: A
title: NVIDIA：W4A8 和 KV 量化、激活量化不是一把开关
quick: >-
  W4 量化权重，A8 量化线性层激活，KV 量化处理历史 KV cache，三者省的空间和带宽不同。TensorRT-LLM 的 `w4a8_awq`
  通常使用 INT4 权重和 FP8 激活，KV 由 `kv_cache_quant_algo` 单独配置；选方案时要分别检查 scale、误差和当前瓶颈。
tags:
  - NVIDIA
  - W4A8
  - Quantization
  - TensorRT-LLM
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Optimizing LLMs for Performance and Accuracy with Post-Training
      Quantization
    url: >-
      https://developer.nvidia.com/blog/optimizing-llms-for-performance-and-accuracy-with-post-training-quantization/
    type: secondary
  - title: Quantization — TensorRT-LLM
    url: 'https://nvidia.github.io/TensorRT-LLM/features/quantization.html'
    type: primary
  - title: AWQ — Activation-aware Weight Quantization
    url: 'https://arxiv.org/abs/2306.00978'
    type: primary
  - title: SmoothQuant — Accurate and Efficient Post-Training Quantization
    url: 'https://arxiv.org/abs/2211.10438'
    type: primary
---

## 可以这样回答

W4、A8 和 KV 量化对应三个不同的张量：模型权重、线性层激活、attention 的历史 KV cache。比如权重已经用 W4 压缩，长上下文的 KV 仍然是 fp16，就可能继续因为缓存放不下而 OOM。判断量化有没有用，要先看当前主要在读哪份数据、哪份数据占显存。

权重位宽记作 $b_W$。小 batch decode 常受内存限制，读取 $W$ 占大头，INT4 相对 fp16 只需 $1/4$ 权重流量。W4A16（AWQ / GPTQ）压缩权重，激活仍为 fp16/bf16，由 mixed-dtype GEMM 计算。
激活位宽记作 $b_A$。prefill 或大 $N$ 时，GEMM 更可能受算力限制，要使用 INT8 / FP8 Tensor Core，激活也要配合量化。W4A8 在 NVIDIA 栈里通常是 INT4 权重 + FP8 激活（`w4a8_awq`），不是 INT4 乘 INT8。W8A8 才是 SmoothQuant 那条 INT8 权激。
历史缓存的位宽记作 $b_{\mathrm{KV}}$，它与线性层激活分别配置。长 $T$ 时，attention 读历史 KV 的成本可能超过读 $W$。FP8 KV 把 cache 和这段带宽减半，开关叫 `kv_cache_quant_algo`，见 `nvidia-fp8-kv`。

## 技术备查

W4、A8 和 KV 量化对应三个不同的张量：模型权重、线性层激活、attention 的历史 KV cache。比如权重已经用 W4 压缩，长上下文的 KV 仍然是 fp16，就可能继续因为缓存放不下而 OOM。判断量化有没有用，要先看当前主要在读哪份数据、哪份数据占显存。

NVIDIA 博客和 TensorRT-LLM 的量化表会分别列出 W4A8 AWQ / GPTQ、W4A16、FP8 权激、FP8 KV 和 NVFP4 KV。ModelOpt 生成 checkpoint，引擎使用对应的 kernel，见 `nvidia-trt-llm`。下面把数据量、scale 和质量影响分别说明。

## 先算各张量的流量

Decode 一步，每层大致要搬：

$$
W:\ |W|\cdot b_W,\qquad
x:\ N\cdot D\cdot b_A,\qquad
\mathrm{KV}:\ 2\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot b_{\mathrm{KV}}.
$$

$N$ 是这一步的 token 数（逐 token 生成的 decode 阶段接近当前 $B$）。三套比特互相独立：

权重位宽记作 $b_W$。小 batch decode 常受内存限制，读取 $W$ 占大头，INT4 相对 fp16 只需 $1/4$ 权重流量。W4A16（AWQ / GPTQ）压缩权重，激活仍为 fp16/bf16，由 mixed-dtype GEMM 计算。
激活位宽记作 $b_A$。prefill 或大 $N$ 时，GEMM 更可能受算力限制，要使用 INT8 / FP8 Tensor Core，激活也要配合量化。W4A8 在 NVIDIA 栈里通常是 INT4 权重 + FP8 激活（`w4a8_awq`），不是 INT4 乘 INT8。W8A8 才是 SmoothQuant 那条 INT8 权激。
历史缓存的位宽记作 $b_{\mathrm{KV}}$，它与线性层激活分别配置。长 $T$ 时，attention 读历史 KV 的成本可能超过读 $W$。FP8 KV 把 cache 和这段带宽减半，开关叫 `kv_cache_quant_algo`，见 `nvidia-fp8-kv`。

所以「开了 W4A8」只保证线性层的 $W$ 和 $x$；KV 可能仍是 fp16。反过来，只开 FP8 KV、权重仍 fp16，短上下文小 batch 下，TPOT 改善可能不明显。

| 配方 | 读 $W$ | GEMM 格式 | KV | 典型墙 |
|---|---|---|---|---|
| W4A16 | $\times 1/4$ | mixed，激活 16 | 另设 | 小 $B$ decode |
| W4A8 | $\times 1/4$ | W4$\times$FP8 | 另设 | decode + 要吃 Tensor Core |
| FP8 W8A8 | $\times 1/2$ | Hopper FP8 MMA | 另设 | 大 $N$ / Hopper |
| INT8 SQ | $\times 1/2$ | INT8 MMA | 另设 | Ampere 权激 |
| FP8 KV | 不变 | 不变 | $\times 1/2$ | 长 $T$ 容量 |

## Scale 不在同一个轴上

权重的 W4 通常在离线训练后量化（PTQ）阶段完成。AWQ 按激活幅度保护显著通道，group size 常见 128，每组一个 $s_W$。GPTQ 是逐列残差量化。反量化在 GEMM 里和 $x$ 乘，累加器仍高精度。

激活的 A8 在运行时对当前 token 或整个 tensor 做量化。W4A8 路径里常有 `pre_quant_scale`（AWQ 的平滑）再 cast 成 E4M3，再和 INT4 权重做 mixed GEMM，输出再乘 $\alpha$。激活 outlier 仍在：只压权重不够时，要么 SmoothQuant 把幅度迁到 $W$，要么别走太窄的 $A$。

KV 缓存由 attention 计算写出，每个生成步骤都会多一行。Scale 跟 paged block 走。K 的误差进 $QK^{\top}$，对 softmax 的影响更大；V 的误差影响相对小一些。和 $W$ 的 group scale 不能共用，calibration 数据也不是同一批张量。训练 FP8 的 amax 更不能拿来当 KV scale，见 `nvidia-fp8`。

如果还要把 KV 设成 4 bit，就需要 NVFP4 KV 等另一条配方，单独评估质量；W4A8 本身没有设置这个缓存位宽。

对于小 $B$、短 $T$ 的 70B 级模型，瓶颈主要是读 $W$，可以先比较 W4A16 和 W4A8。Hopper 上 W4A8 比 W4A16 多一次激活量化，Nsight 看 SOL：若已经是内存墙，A8 的收益可能被 quant kernel 吃掉，要以实测为准。

长上下文、并发高时，先比较 FP8 KV 或 GQA；仅压缩 W4 可能仍装不下 cache。显存仍不够，才轮到卸载，见 `nvidia-kv-offload`。卸载的带宽比量化差一个数量级，能用 $b_{\mathrm{KV}}$ 解决就不要把热 KV 赶到 PCIe 上。

质量测试也分别做：W4 检查 MLP 通道误差，KV 检查长距离 attention，先各自 A/B，再组合。TRT-LLM 表上 Hopper 支持 W4A8 AWQ，Ampere 往往只有 W4A16：没有原生 FP8 MMA 时 A8 不一定划算。

## 追问

**A8 是 INT8 还是 FP8？**
在 NVIDIA PTQ 博客和 TRT-LLM 里，W4A8 默认按 INT4 权重 + FP8 激活讲。INT8 权激是另一列 SmoothQuant。
**和权重 FP8 怎么比？**
FP8 W8A8 权重只减半，但 MMA 整齐；W4 权重更瘦、核更不规则。容量优先 W4，Hopper Tensor Core 优先 FP8，也可以权重 W4、KV FP8 混搭。
**激活量化会改 sampling 吗？**
线性层误差会进 logits。先看 greedy / 短任务，再看长上下文检索。KV 量化更常在长上下文上暴露问题。
**group size 写成 1？**
group size 为 1 时粒度最细，但 scale 开销会增大、kernel 变慢，质量也未必同比提高。128 是 AWQ 常见的折中。

相关量化基础也可看 `nvidia-int8-quant`。

## 相关题

- [[nvidia-fp8-kv]]：只拆本题三笔账里的 KV 那笔，讲 FP8 KV 和权重量化为什么是两个开关。
- [[sys-kv-quant]]：KV 量化的 outlier 和 scale 轴（K per-channel、V per-token），是本题 KV 部分的细节。
- [[sys-fp8-gemm]]：纯 FP8 W8A8 的 GEMM 和 scale 粒度，回答「和权重 FP8 怎么比」时要用。
- [[nvidia-int8-quant]]：INT8 对称/非对称和 calibration 的基础，本题的 INT4 权重和 SmoothQuant 对比都建立在它上面。
- [[coding-int8-symm]]：把对称量化和 dequant GEMM 真正写成代码的白板题，适合练手。
- [[nvidia-trt-llm]]：本题提到的 `w4a8_awq` 和 KV 开关所在的引擎，那题讲 plugin、inflight 和量化各管哪层。
