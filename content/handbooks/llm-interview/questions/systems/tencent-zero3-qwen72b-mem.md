---
id: tencent-zero3-qwen72b-mem
section: systems
order: 200
level: A
title: 腾讯混元：ZeRO-3 微调 Qwen2-72B 时如何估算单卡显存？
quick: >-
  先拆参数/梯度/优化器状态在 ZeRO-3 下按数据并行度分片，再加激活、临时缓冲与碎片。不能只背「72B×2
  字节」，要写出分片后每卡参数字节 + Adam 状态 + 激活重计算策略。
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

这块容易背「$72\mathrm{B}\times 2$ 字节 $=144\,\mathrm{GB}$」当单卡占用，或反过来以为 ZeRO-3 后每卡只剩 $144/D$、激活忽略。我会做**分项估算 + 假设**，不报虚假精确的 37.2GB。先声明：全参还是 LoRA、$D$ 卡、seq、micro-batch、是否 checkpoint。分片表见 `tencent-zero-123`，bytes/param 见 `sys-memory`。我会报完公式再代入，不先甩一个 GB。利用率口径见 `tencent-sft-parameter-gpu-utilization`，不要把占用率和 MFU 混在这道估算题里。

## 真题记录

- 公司：腾讯 · 混元
- 原始措辞：**“用 DeepSpeed ZeRO-3 来微调 Qwen2-72B，每一张卡占用的显存大概是多少，估算一下为什么”**

## 先写分片后的参数账

$72\times 10^9$ 参数。BF16 权重总量 $\approx 72\times 10^9\times 2=144\,\mathrm{GB}$。ZeRO-3 按数据并行度 $D$ 分片，每卡稳态约 $144/D\,\mathrm{GB}$，但前向 all-gather 一层时峰值会回到「一层完整参数」。全参微调时梯度同量级（BF16 约再 $144/D$）。Adam 若 FP32 $m$、$v$ 加 master，约 $12$ bytes/param，总量 $\approx 864\,\mathrm{GB}$，分片后每卡 $\approx 864/D\,\mathrm{GB}$。未分片时五份状态约 $16$ bytes/param；ZeRO-3 把这 $16N$ 除到 $D$ 张卡上。例：$D=64$ 时参数侧稳态大约 $16\times 72\times 10^9/64\approx 18\,\mathrm{GB}$/卡量级，这还没算激活，不要把 18GB 说成最终答案。$D=8$ 时同一项约 $144\,\mathrm{GB}$/卡，80GB 卡仍放不下，所以要么更大 $D$、要么叠 TP、要么改 LoRA。我会把 $D$、是否全参说在数字前面。和「什么时候升到 3」衔接：72B 全参几乎必然要 3 或把 $N$ 用 TP/PP 切开，见 `tencent-zero-123`。

## 激活往往是长序列主导项

Activation $\propto B\cdot T\cdot L\cdot d$，和 $D$ 无关（本地 micro-batch 全量在）。Qwen2-72B 层数多、hidden 大，2k 到 8k SFT 时激活可以反超分片后的参数状态。Gradient checkpointing 用重算换显存，是这里的第一杠杆。再加 logits（词表 $\times$ 序列）、通信 buffer、allocator 碎片，预留 10% 到 20%+。all-gather 工作区会让峰值高于稳态，`nvidia-smi` 对不上「$16N/D$」是正常的。LoRA 时强调：可训参数 $\ll 72\mathrm{B}$，优化器只挂 adapter；底座 BF16 仍按 $144/D$ 分（或冻结后 CPU offload）。给数量级，不给精确 GB：报你用过的 $D$、seq、checkpoint、全参/LoRA。激活侧手段是 checkpoint / SP / 减 $T$，不是再升一个 ZeRO stage。ZeRO 已经到 3 了，再升没有下一档。这正是「除了 DeepSpeed 还有什么」要分层的原因，见 `tencent-beyond-deepspeed`。

白板我建议写三行再求和，不要口算一个总数：第一行参数状态 $16N/D$；第二行激活，给 $B,T$ 和是否 checkpoint 的倍数（常见是不开 checkpoint 时激活可以大过第一行）；第三行 15% 碎片和通信缓冲。三行都依赖你声明的假设，换 $D$ 或改 LoRA 只动第一行，换序列长度只动第二行。假设改了，我要能当场改对应那一行，而不是把整个 GB 数重编。全参 $D=8$ 第一行已经约 144GB，结论是「这张卡放不下，要更大 $D$、TP 或 LoRA」。

全参和 LoRA 必须准备两套数。全参：$16N/D$ 加激活。LoRA：adapter 的 Adam 按可训参数计，底座权重按 $2N/D$ 或 offload 掉，激活仍按全图前向计。LoRA 省的是优化器，不一定省激活，长序列照样要 checkpoint。有人把 LoRA 说成「72B 变几百万参数所以显存忽略」，漏了底座前向和激活，这是最常见的低估。报数时把「优化器项」和「底座前向项」分成两行。Qwen2-72B 的词表和层数都会把 logits 与激活抬上去，不要用通用 7B 的直觉硬套。给数量级、给假设、拒绝假精确。

## 追问

- **$D=8$ 全参大概怎样？** 参数状态约 $16\times 72\mathrm{B}/8\approx 144\,\mathrm{GB}$/卡，80GB 卡仍放不下，还要更大 $D$、TP 或 LoRA。先说假设再报数。
- **为什么不能报一个固定 GB？** $D$、seq、checkpoint、LoRA 差一档，数字差一倍。先写公式再代入。
- **ZeRO-3 峰值为什么高于稳态？** 按层 all-gather 参数，用完才丢掉；还有通信 buffer。看峰值不要看平均值。
- **激活为什么不分片？** ZeRO 不分 activation。要 checkpoint、序列并行或减 micro-batch。升 3 解决不了长序列。
- **LoRA 还按 72B Adam 算吗？** 不要。$m/v$ 只在 adapter 上；底座至多一份分片权重。这会把每卡从一百多 GB 量级打到十几 GB 量级。
- **和利用率那题怎么分开？** 本卡估占用；MFU / tokens/s 是另一口径，见 `tencent-sft-parameter-gpu-utilization`。占用高可以很慢。
- **白板三行是什么？** $16N/D$、激活、$15\%$ 碎片。改 $D$ 动第一行，改 seq 动第二行，不要把整个数字重编。
- **把 $D$ 从 64 改成 8 怎么办？** 第一行乘 8，得出单卡已经超过 80GB，结论改成必须再切或改 LoRA，不要硬圆原来的 18GB。
- **LoRA 为什么不一定省激活？** 底座仍要全图前向，激活仍按 $B,T,L,d$ 走。省的是 Adam 那一行。长序列照样 checkpoint，不要说「72B 变几百万参数所以显存忽略」。
- **词表为什么会抬显存？** logits 是词表 $\times$ 序列，Qwen2-72B 词表大，这一项不能用 7B 直觉硬套。三行之外如果还 OOM，先看 logits 和工作区。
- **假精确的 GB 有什么害处？** 改 $D$ 或改 LoRA 就圆不回去。给数量级、给假设、改哪一行就动哪一行。
- **三行求和时哪一行最容易漏？** 激活。$D$ 很大时第一行已经不大，8k SFT 第二行会反超。漏了激活就会报一个漂亮的 $16N/D$，上机立刻 OOM。
- **offload 底座之后还要不要报 $144/D$？** 权重不在 GPU 上就不要再按分片 BF16 计，但前向仍可能把一层 gather 回来，峰值还在。报稳态和峰值两句话。
- **上机立刻 OOM 而白板对得上，通常漏了什么？** 激活或 all-gather 峰值。$D$ 很大时第一行好看，8k 第二行和峰值才是凶手。看 `nvidia-smi` 对峰值，不要对平均值。
