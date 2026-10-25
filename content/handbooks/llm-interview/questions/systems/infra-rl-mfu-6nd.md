---
id: infra-rl-mfu-6nd
section: systems
order: 237
level: S
title: AI Infra 实习：RL 里 rollout 大概占多少时间？MFU 和 $6ND$ 怎么算？
quick: "长 CoT 的 GRPO 里，rollout 常占 60-80% 的耗时。训练 FLOPs 约为 $6ND$，MFU $= 6ND / (t\\cdot \\mathrm{peakFLOPs})$，这个口径只适用于 backward 那段，decode 不能套。"
tags:
  - RL Infra
  - MFU
  - VeRL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: AI infra实习面经（小厂）
    url: https://www.nowcoder.com/feed/main/detail/166e576d5afa4a298cf9492ed51bed04
    type: candidate-first-hand
  - title: Scaling Laws for Neural Language Models
    url: https://arxiv.org/abs/2001.08361
    type: primary
---

长 CoT 的 GRPO 里，rollout 常常占一步耗时的 60-80%；$6ND$ 估的是训练正反向的 FLOPs，所以 MFU 只能拿来描述 actor backward 那一段，生成不能套。我会先把一步拆开，generate、奖励分数（reward）、recompute logp、reshard、backward 各占多少，再报数。把预训练的 MFU 口径直接当成「RL 一步的利用率」，是这题最常见的错。

举个例子，如果把整段采样轨迹（rollout）的时间也塞进分母的 $t$，分子却还是训练的 $6ND$，算出来的 MFU 会被稀释到个位数。这个数字没有物理意义，它只说明账本没切开，backward kernel 本身未必那么差。

## $6ND$ 和 MFU 怎么算

这是 Kaplan 以来的工业约定：参数量 $N$、token 数 $D$，一次完整训练（前向加反向）的 FLOPs 约为 $6ND$。线性层 $y=xW$ 对每个 token、每个参数大约做 2 次浮点运算（一次乘加），所以前向 $\approx 2ND$；反向要对激活和权重各回传一次，大约再加 $4ND$。合起来：

$$
\mathrm{FLOPs}_{\mathrm{train}} \approx 6ND.
$$

Attention 的 $QK^\top$ 不算在 $N$ 里，这是数量级近似，面试报公式就够了。Attention 的额外 FLOPs、MoE 路由、序列并行里的通信，工业界也照样用 $6ND$ 当主项，除非对方让你拆线性层，否则别往每层精确计数推。MFU 是用这些有效 FLOPs 除以 GPU 标称峰值乘实际耗时：

$$
\mathrm{MFU} = \frac{6ND}{t\cdot \mathrm{peakFLOPs}}.
$$

$D$ 必须是实测的有效 token，扣掉 padding，扣掉没进损失（loss）的输入提示（prompt）。拿 `max_length × batch` 当 $D$，分子虚高，MFU 看着很好，实际在空转。长 CoT 下 $D$ 的方差很大，组内一条 8k、一条 200，padding 不扣的话，MFU 会被最长那条序列的无效计算拖低。动态 batch 按 token 预算切，就是为了让 $D$ 更接近真正在算的 token。另外，FSDP 的 all-gather、activation checkpoint 的重算都会进 $t$，却不一定进你报的 $D$，也会把数字压下来。

分子和分母要配对。分子用 actor 有效 token 的 $6ND$，分母就只能是 actor update 的实际耗时。如果把 ref 前向、logp 重算的 FLOPs 也算进分子，它们是 $2ND$ 量级的前向，没有反向那 $4ND$，那分母就要包含这些前向的时间。两种口径混着用，就成了数字游戏。peak FLOPs 用厂商给的该 dtype 稠密标称值，比如 H100 BF16，别拿稀疏或 INT8 的峰值当稠密训练的分母。

## RL 里为什么低、怎么报

监督微调（SFT）和预训练的一步几乎全是大 GEMM，算术强度高，MFU 40-60% 很常见。On-policy RL 的一步通常分三段，见 `sys-rl-infra`。第一段是 rollout，自回归 decode，每步只出 1 个 token，反复读权重和 KV，是 memory-bound 的（见 `sys-prefill-decode`），Tensor Core 喂不饱，耗时却最长；长思维链（CoT，即分步推理过程）或 `rollout.n` 很大时，生成占 60-80% 很正常。第二段是 reward、ref 和重算 logp，都是额外的前向，micro-batch 小、形状碎，算力密度低。第三段才是 actor backward，也就是 $6ND$ 对应的那段，它还常被 HybridEngine 的 reshard、切推理布局打断。

预训练那套 $6ND$ 默认了三件事：大 GEMM、高算术强度、通信气泡可以忽略。RL 的 decode 打破了前两条，HybridEngine 换布局打破了第三条。所以「RL 的 MFU 只有预训练一半」，常常是负载变了，实现未必写砸了。这时候会出现两种「低」，我会分开说：把整步时间当 $t$，MFU 被生成稀释到个位数，这是口径问题；单看 policy update，micro-batch 小、长短不一、还要换布局，10-30% 也很常见，大约不到预训练的一半。fused kernel 救不了被 rollout 占满的一步，要先把生成引擎和 continuous batching 做好，见 `sys-rl-why-vllm-rollout`。

报数时先声明口径：含不含 ref 和 reward、是不是异步、序列多长、MFU 指整步还是只指 actor update。7B 长推理的 GRPO，可以说 rollout 约 70%、actor MFU 10-30%，给区间，不装精确。生成侧要报 FLOPs 的话，decode 前向大约每 token $2N$，但受带宽限制，实际达到的 FLOPs 远低于峰值，不能反推成训练 MFU。和预训练同事对数字时，我会把一步拆成 generate / sync / recompute / backward 四段：只有 backward 适用 $6ND$ 的 MFU，generate 报有效 tokens/s 和 KV，不报 MFU。

被问「怎么提高 RL 的 MFU」，先反问提高哪一段，优化也按这四段走。generation-bound 就换引擎、上连续 batch、限制长度尾部；sync-bound 就改放置或者用 LoRA；recompute-bound 就减掉多余的 ref 前向；update 段可以加大 micro-batch、减 padding、让通信和计算重叠、少切一次布局，最后才轮到 fused kernel。规模也要带上：7B 更容易 generation-bound，到 70B，reshard 和 all-gather 又会变成训练侧的瓶颈。

## 追问

**生成能不能套 $6ND$？**
不能。$6ND$ 包含反向，$D$ 还默认了大 GEMM。decode 是每 token $2N$ 量级的瘦矩阵，瓶颈在 HBM，实际达到的 FLOPs 远低于峰值，见 `sys-prefill-decode`。同理，也不能拿 $6ND$ 直接除出 rollout 要几台机器，应该按有效 tokens/s 和 KV 容量估卡。

**为什么重算 logp 会拉低 MFU？**
它多了一次训练图的前向，时间进了 $t$。如果你的 $D$ 只算 actor update，分母变大、分子不变。所以口径里要说明这次 $2ND$ 前向有没有算进分子。

**异步 RL 会不会让 MFU 变好看？**
会。训推重叠后，actor 段的 $t$ 变短，数字上升，但这只说明训练卡不再空等，策略不一定更对。staleness 是另一笔账，见 `slime-async-train`。

**7B 和 70B 的「低 MFU」是一回事吗？**
不是一回事。小模型更容易 generation-bound，大模型的 reshard 和 all-gather 会重新变成训练侧的瓶颈。报区间时带上规模，别直接拿去和预训练的 50% 比。
