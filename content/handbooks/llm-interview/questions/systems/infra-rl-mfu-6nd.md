---
id: infra-rl-mfu-6nd
section: systems
order: 237
level: S
title: AI Infra 实习：RL 里 rollout 大概占多少时间？MFU 和 $6ND$ 怎么算？
quick: >-
  长 CoT / GRPO 里 rollout 常占墙钟 60-80%，policy backward 的 MFU 往往只有预训练的一半不到。训练
  FLOPs 近似 $6ND$（$N$ 参数、$D$ token）；MFU $= 6ND / (t\cdot
  \mathrm{peakFLOPs})$。生成是 decode，别用同一套 $6ND$ 估 rollout。
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

错法：把预训练 MFU 直接报成「RL 一步的利用率」。$6ND$ 估的是 训练正反向里的有效 token；GRPO 一步墙钟大头在 decode 生成。生成不要套同一套 $6ND$，否则分子是训练 FLOPs、分母却含整段 rollout，数字没有物理意义。报数前我先画一步墙钟：generate、reward、recompute logp、reshard、backward 各占多少。MFU 只描述 backward 能不能把 Tensor Core 喂饱；把 rollout 时间塞进同一个 $t$，是这道题最常见的口径错误。

## $6ND$ 在算什么

Kaplan 以来的工业约定：参数量 $N$、token 数 $D$，一次完整训练（前向 + 反向）的 FLOPs 近似 $6ND$。线性层 $y=xW$ 对每个 token、每个参数大约 2 次浮点（乘加）做前向，所以前向 $\approx 2ND$。反向要对激活和权重各回传一次，大约再 $4ND$。合计：

$$
\mathrm{FLOPs}_{\mathrm{train}} \approx 6ND.
$$

Attention 的 $QK^\top$ 不进 $N$，这是数量级近似，面试报公式即可。MFU 把这些有效 FLOPs 除以 GPU 标称峰值乘墙钟：

$$
\mathrm{MFU} = \frac{6ND}{t\cdot \mathrm{peakFLOPs}}.
$$

$D$ 必须是 实测有效 token：扣 padding、扣没进 loss 的 prompt。用 `max_length × batch` 当 $D$，分子虚高，MFU 看起来很好、实际在空转。FSDP all-gather、activation checkpoint 重算会进 $t$，不一定进你报的 $D$，也会把数字打下来。同一套公式，分子分母要配对：分子用 actor 有效 token 的 $6ND$，分母就只能用 actor update 的墙钟；若把 ref 前向、logp 重算的 FLOPs 也算进分子（它们是 $2ND$ 量级的前向，没有反向那 $4ND$），分母就要含这些前向的时间。混用是数字游戏。Attention 的额外 FLOPs、MoE 路由、序列并行里的通信，工业界仍用 $6ND$ 当主项，面试不要把公式推到每层精确计数，除非对方要你拆线性层。

## 为什么 RL 的 MFU 更低

SFT / 预训练一步几乎全是大 GEMM，算术强度高，MFU 40-60% 常见。On-policy RL 一步通常拆成三段，见 `sys-rl-infra`：

1. Rollout。 自回归 decode，每步 1 个 token，反复读权重和 KV，memory-bound，见 `sys-prefill-decode`。峰值 Tensor Core 喂不饱，墙钟却最长。长 CoT / 大 `rollout.n` 时，生成占 60-80% 很正常。
2. Reward / ref / 重算 logp。 额外前向，micro-batch 小、形状碎，算力密度低。
3. Actor backward。 这才是 $6ND$ 那段，还常被 HybridEngine reshard、切推理布局打断。

于是出现两个「低」，我会拆开说：若把整步时间当 $t$，MFU 会被生成稀释到个位数，那是账本没切，不是 backward kernel 真那么差；单看 policy update，micro-batch 小、长短不一、还要换布局，10-30% 也常见，大约预训练的一半不到。优化 fused kernel 救不了 rollout 占满的一步，要把生成引擎和 continuous batching 做好，见 `sys-rl-why-vllm-rollout`。预训练那套 $6ND$ 还默认大 GEMM、高算术强度、通信气泡可忽略；RL 的 decode 打破前两条，HybridEngine 换布局打破第三条，所以「RL MFU 只有预训练一半」常常是负载变了，不是实现写砸了。长 CoT 下 $D$ 的方差很大：组内一条 8k、一条 200，padding 若不扣，MFU 会被最长序列的空计算拉穿。动态 batch 按 token 预算切，就是为了让 $D$ 更接近「真的在算的 token」。被问「如何提高 RL MFU」时，先问提高的是哪一段。Rollout 段：换引擎、连续 batch、限制长度尾部。Update 段：加大 micro-batch、减 padding、通信与计算重叠、少切一次布局。7B 更容易 generation-bound，70B 的 reshard 和 all-gather 会重新变成训练侧瓶颈，报区间时带上模型规模。

## 面试怎么报数

先声明口径：是否含 ref / reward、是否异步、序列长度、MFU 是「整步」还是「仅 actor update」。7B 长推理 GRPO，rollout ~70%、actor MFU 10-30%，给区间不装精确。生成侧若要报 FLOPs，decode 前向大约 $2N$ 每 token，但受带宽限制，实际达到的 FLOPs 远低于峰值，不能反推成训练 MFU。异步 RL 让 generate 与 train 重叠后，actor 段的 $t$ 变短、MFU 数字会好看一些，但那只说明训练卡不再空等，不说明策略更对，stale 是另一笔账。peak FLOPs 用厂商标称（如 H100 BF16），不要用稀疏或 INT8 峰值去当稠密训练的分母。

和预训练同事对数字时，把一步拆成 generate / sync / recompute / backward 四段。只有 backward 适用 $6ND$ 的 MFU；generate 报有效 tokens/s 和 KV，不要报 MFU。优化也按这四段走：generation-bound 换引擎，sync-bound 改放置或 LoRA，recompute-bound 减多余 ref 前向，最后才轮到 fused kernel。被追问「RL MFU 为什么低」时，先说负载从大 GEMM 变成了 decode，不要先认实现没写好。

## 追问

- **生成能不能套 $6ND$？** 不能。$6ND$ 含反向；$D$ 还假设大 GEMM。Decode 是 $2N$/token 量级的瘦矩阵，瓶颈在 HBM，实际达到的 FLOPs 远低于峰值，见 `sys-prefill-decode`。
- **padding 怎么进公式？** 名义 token 进了 $D$ 却没做有效 matmul，MFU 被低估。要用 response mask 后的有效 token。动态 batch 按 token 预算切，就是为了让 $D$ 更接近真在算的量。
- **为什么重算 logp 会打 MFU？** 多一次训练图前向加进 $t$，若你的 $D$ 只计 actor update，分母变大、分子不变。口径要声明是否把这次 $2ND$ 前向算进分子。
- **异步 RL 会不会让 MFU 好看？** 训推重叠后 actor 段 $t$ 变短、数字上升，只说明训练卡不再空等，不说明策略更对。stale 见 `slime-async-train`。
- **$6ND$ 能不能用来估 rollout 机器数？** 不能直接除。Decode 达不到峰值算力，应按有效 tokens/s 和 KV 容量估卡，而不是按训练 FLOPs 反推。
- **7B 和 70B 的「低 MFU」是一回事吗？** 不是。小模型更容易 generation-bound；大模型 reshard 和 all-gather 会重新变成训练侧瓶颈。报区间时带上规模，避免和预训练 50% 直接比。
- **peak FLOPs 用哪个？** 用该 dtype 的稠密标称（如 H100 BF16），不用稀疏或 INT8 峰值当训练分母。口径比数字本身更容易错。
- **$6ND$ 的 $D$ 能不能用配的 max length？** 不能。必须用实测有效 token，扣 padding 和没进 loss 的 prompt。否则分子虚高。生成段不要套这套公式，那是 decode、generation-bound。RL 的 MFU 更低，首先因为墙钟被 rollout 占满，其次才是 actor 段 micro-batch 小、还要换布局。
