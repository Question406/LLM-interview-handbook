---
id: tencent-zero3-qwen72b-mem
section: systems
order: 200
level: A
title: 腾讯混元：ZeRO-3 微调 Qwen2-72B 时如何估算单卡显存？
quick: "先问全参还是 LoRA、数据并行度 D、序列长度和 micro-batch，再逐项估显存。全参 ZeRO-3 的参数状态约为 16N/D，还要加本地激活、按层 all-gather 峰值、logits 和缓冲；LoRA 的优化器只按 adapter 参数计算。"
tags:
  - Tencent
  - Hunyuan
  - ZeRO
  - Memory
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯-混元大模型面经
    url: https://www.nowcoder.com/feed/main/detail/19561cb3bcbf4a519766f61d6414a44c
    type: candidate-first-hand
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

ZeRO-3 微调 Qwen2-72B 的单卡显存，要按参数状态、激活和临时缓冲分别估。先给出全参还是 LoRA、$D$ 卡、seq、micro-batch 和是否 checkpoint，再代入公式。例如全参 $D=64$ 时，参数状态稳态约 18GB/卡，$D=8$ 时却约 144GB/卡，后者连 80GB 卡都放不下，还未计算激活。

模型有 $72\times 10^9$ 参数，BF16 权重总量 $\approx 72\times 10^9\times 2=144\,\mathrm{GB}$，也就是 $72\mathrm{B}\times 2$ 字节 $=144\,\mathrm{GB}$。ZeRO-3 按数据并行度 $D$ 分片，权重稳态约 $144/D\,\mathrm{GB}$，前向 all-gather 一层时会临时装入这一层完整参数。全参的 BF16 梯度约再加 $144/D$。Adam 的 FP32 $m$、$v$ 和 master 合计约 $12$ bytes/param，总量 $\approx 864\,\mathrm{GB}$，每卡 $\approx 864/D\,\mathrm{GB}$。

Adam 的 $m/v$ 已计入这些状态，未分片总量约 $16N$。这些状态合计约 $16$ bytes/param，第一行写作 $16N/D$。代入 $D=64$，得到 $16\times 72\times 10^9/64\approx 18\,\mathrm{GB}$/卡；代入 $D=8$，得到约 $144\,\mathrm{GB}$/卡，也就是 $16\times 72\mathrm{B}/8\approx 144\,\mathrm{GB}$/卡。把 $D$ 从 64 改成 8，第一行就乘 8，需要增大 $D$、叠 TP 或改 LoRA。72B 全参通常需要 ZeRO-3，或先通过 TP/PP 切开 $N$。

第二行算 activation，规模 $\propto B\cdot T\cdot L\cdot d$。它取决于本地 micro-batch，并不会因 ZeRO 的 $D$ 增大而自动分片。Qwen2-72B 层数多、hidden 大，2k 到 8k 监督微调（SFT）时，激活可能超过分片后的参数状态。Gradient checkpointing 用重算换显存，还可考虑 SP 或减 $T$；估算时要声明 $B,T$ 和是否 checkpoint。不开 checkpoint 时，激活可能比第一行还大。

第三行加 logits、通信 buffer、all-gather 工作区和 allocator 碎片，通常预留 10% 到 20%+；白板可以用 15%，即 $15\%$ 作示意。Logits 的规模是词表 $\times$ 序列，Qwen2-72B 的词表和层数都会抬高这部分与激活，不能照搬通用 7B 的直觉。上机仍 OOM 时，应检查峰值，而非拿 `nvidia-smi` 平均值去对 $16N/D$。

LoRA 要另算一套：可训参数 $\ll 72\mathrm{B}$，Adam 只挂 adapter，底座 BF16 权重约 $2N/D$，也就是 $144/D$，或冻结后放到 CPU offload。底座不在 GPU 的稳态就不重复计入，但前向载入 / gather 一层仍有峰值。LoRA 可把每卡从一百多 GB 量级降到十几 GB 量级，但底座仍需全图前向，激活仍随 $B,T,L,d$ 变化，长序列照样可能需要 checkpoint。

最后报告数量级和假设，避免给一个看似精确的 37.2GB。改 $D$ 或换 LoRA 时调整第一行，改序列长度时调整激活项，缓冲与碎片另留余量。显存占用与 MFU / tokens/s 也要分别回答，占用高仍可能算得慢。

相关：`tencent-zero-123`、`sys-memory`、`tencent-sft-parameter-gpu-utilization`、`tencent-beyond-deepspeed`


## 真题记录

- 公司：腾讯 · 混元
- 原始措辞：**“用 DeepSpeed ZeRO-3 来微调 Qwen2-72B，每一张卡占用的显存大概是多少，估算一下为什么”**
