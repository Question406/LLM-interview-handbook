---
id: apple-ondevice-kv
section: apple
order: 12
level: S
title: Apple：端侧 KV 的显存和带宽怎么估，GQA 加量化 cache 各省哪一刀？
quick: "端侧 decode 每步读取历史 KV，显存和带宽可先按 $2 L H_{\\mathrm{kv}} d_h S b$ 估算。GQA 减少 KV head，8-bit cache 减少每元素字节，2025 公开的跨块 KV 共享再减少有效存储深度；长上下文要重点检查手机 DRAM / ANE SRAM 的预算。"
tags:
  - Apple
  - KV Cache
  - GQA
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

端侧 KV 优化先算驻留字节和每步读取量，再分别看 GQA、8-bit cache 和跨块共享能省多少。decode 每步都要读历史，手机上的约束是 DRAM 带宽、ANE SRAM 和预分配静态 shape，相关导出约束见 `apple-ane`。

Apple 2024 报告已使用 GQA 和 Neural Engine KV 更新；2025 进一步公开 8-bit cache，并让第二段复用第一段末层 KV，cache 约再降 37.5%。权重压缩之后，长上下文的 KV 可能成为主要带宽开销。权重量化和 mask 的 $-\infty$ 问题见 `apple-ondevice-quant`，云端同类估算见 `sys-kv-quant`、`google-gqa-mqa`。

## 先写字节，再谈技巧

一份 KV 的驻留大约：

$$
\mathrm{Bytes} \approx 2 \cdot L \cdot H_{\mathrm{kv}} \cdot d_h \cdot S \cdot b
$$

$2$ 是 K 和 V，$L$ 层数，$S$ 是已写入的上下文，$b$ 是每元素字节。Query head 数 $H_q$ 不进 cache。GQA 把 $H_{\mathrm{kv}}$ 收到 $H_q/g$；MQA 收到 1。形状是 $[B,H_{\mathrm{kv}},S_{\max},d_h]$，算注意力时再 broadcast 到 $H_q$，不要把 cache 存成 $H_q$ 份，否则 GQA 白做。手写 attention 见 `apple-mha-code`。

端上 decode 每步 $T_q=1$，算术强度接近 1：FLOPs 和从 DRAM 搬来的 KV 字节同一量级。权已经 palettize 到约 3.7 或 2 bpw 之后，读权变便宜，长 $S$ 时 KV 成为主带宽。因此可以按 GQA $\to$ 量化 cache $\to$ 少算一些层的 KV 的顺序评估，先找出长上下文主要花在哪里。

这几种做法分别改变公式里的不同因素：

- GQA。线性降 $H_{\mathrm{kv}}$。质量敏感时不要直接 MQA；AFM 公开走 grouped-query。
- 8-bit KV。$b: 2\to 1$（相对 fp16）。Scale 按 head 或按 token 保存。Score 仍建议在 fp16 累加；mask 加在反量化之后，见 `apple-ondevice-quant`。K 的 outlier 常沿通道，乱 per-tensor 会把注意力打歪，云端同构讨论见 `sys-kv-quant`。
- KV sharing（2025）。模型按约 5:3 深度切成两块，block 2 的 KV 直接用 block 1 末层的 cache，公开写降约 37.5%，还能让 输入预填充（prefill，即处理输入并建立缓存） 跳过第二块的 KV 生成。这是改深度结构，不是 PTQ。

ANE 还要求预分配 $S_{\max}$，不能 `torch.cat` 沿时间维涨。Stateful 模型把 KV 登记成跨 `predict` 的 state；写入是定点 slice。随机 scatter 容易掉出 ANE。档位太稀浪费 SRAM，太密二进制膨胀，见 `apple-ane`。

## 用一个配置估算带宽

假设端侧 $L=28$，$d_h=128$，$H_{\mathrm{kv}}=8$（GQA），$S=4096$，fp16：

$$
2\cdot 28\cdot 8\cdot 128\cdot 4096\cdot 2 \approx 470\ \mathrm{MB}
$$

每步 decode 都要扫这一份（加上当前层的计算）。改 8-bit 大约减半；若 $H_{\mathrm{kv}}$ 从 32 收到 8，再除以 4；KV sharing 再乘约 0.625。三刀叠完，同一 4k 窗口才谈得上和系统、激活抢内存。视觉前缀也占这条 cache，见 `apple-multimodal`：减不掉已经写进去的图像 token。

不要承诺「8-bit KV 无损」。短上下文 greedy 要和 fp16 cache 对得上；长上下文看的是摘要是否由证据支持，以及是否遵循指令，不是再刷一遍 MMLU。RoPE 必须在量化前转到 $K$，否则 cache 里是未旋转向量，decode 错位。



先问上下文上限和 batch（端上常常 $B=1$，但预分配仍按 $S_{\max}$）。再写公式，标出 $H_{\mathrm{kv}}$、$b$、$L_{\mathrm{effective}}$ 三处旋钮。主动说失败模式：cache 存成 $H_q$；INT8 分数上加 mask；动态 `cat` 掉出 ANE；投机拒绝后不回滚 KV，见 `apple-spec-edge`、`openai-speculative-decoding`。

评测：同一前缀 greedy 对齐；Instruments 上看 decode 是否被内存墙拖住；热和功耗跟 $S$ 走，连续对话会降频，见 `apple-afm-eval`。采样仍在 CPU 的小 $k$ 上可以，见 `apple-topk-sample`，那不改变 KV 带宽。

## 追问

**GQA 和 8-bit 谁先做？**
训练时就 GQA，几乎零推理税。8-bit 是推理压缩，要校准和可能的 recovery adapter。长窗口两者都要。
**Paged KV 端上有吗？**
云端分页是为了并发和碎片。端上 $B\approx 1$、静态 $S_{\max}$，预分配更符合 ANE。不要把 vLLM 故事原样搬到 iPhone。
**为什么不把 KV 也 2-bit？**
权可以 QAT 到 2-bit；KV 每 token 写入、对 softmax 敏感。公开停在 8-bit 是质量和带宽的折中。
**第二段复用第一段 KV，注意力还对吗？**
设计假设后段可以从前段末层的压缩状态继续。这是架构选择，要在长上下文任务上验，不能口头保证等于满 KV。

## 相关题

- [[google-gqa-mqa]]：MHA、MQA、GQA 三档怎么选、KV 显存差多少，是这里「GQA 砍 $H_{\mathrm{kv}}$」那一刀的展开，场景在云端。
- [[apple-ondevice-quant]]：同一套 Apple 端侧模型的另一半，讲权重 palettization 和 ANE 上 mask 的数值问题，本题只管 KV。
- [[sys-kv-quant]]：云端 KV 量化的通用版，细讲 K/V 的 outlier 轴和 scale 怎么分。
- [[nvidia-kv-offload]]：GPU 上 KV 放不下时卸到 CPU/NVMe 的带宽账，端侧没有这条退路，可以对照看。
- [[google-tpu-decode]]：同样是 decode 每步读 KV 撞带宽墙，换到 TPU 上大并发 serving，靠连续批和投机解码把 batch 做大。
- [[meta-llama-gqa]]：用 Llama 2 70B 的 32/8 配置算 GQA 省下的 KV，和这里同一个公式，但墙是 HBM 不是手机 DRAM。
