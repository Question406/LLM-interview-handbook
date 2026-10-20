---
id: sys-rl-memory
section: systems
order: 19
level: S
title: 7B 模型做 GRPO，显存主要花在哪里？怎么优化？
quick: "去掉 Critic 后，训练侧仍有 Actor 的 Adam 状态（约 16 bytes/param）、ref 和激活，rollout 侧还有 $G$ 条长序列的 KV。先分清 OOM 在训练还是生成，再对症优化。"
tags:
  - GRPO
  - Memory
  - 真实面经
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: 2025 美团大模型面经
    url: 'https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0'
    type: legacy-reference
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
---

这块容易听到「GRPO 去掉 Critic」就报一个固定 GB 数，或把训练显存和 serving KV 混成一笔。峰值取决于精度、optimizer、ZeRO stage、序列长、group size $G$、并行，以及训练与 采样轨迹（rollout） 是否占用同一张卡。先拆三类峰值，再谈优化。

## 1. 训练侧：policy 仍是一份 Adam 账

Actor 要前向、反向、更新。和 监督微调（SFT） 一样，经典 mixed-precision Adam 大约 $16$ bytes/param（BF16 $W$ / 梯度、FP32 master、$m$、$v$）。未分片时 $7\mathrm{B}$ 量级仍是约 $112\,\mathrm{GB}$ 的状态，外加 activation。GRPO 省掉的是 **Critic 那一整份同规模状态**，不是把 Actor 变成「只有 14GB」。

Reference $\pi_{\mathrm{ref}}$ 通常冻结：无梯度、无 Adam，BF16 约 $2$ bytes/param（$\approx 14\,\mathrm{GB}$），但仍要做 KL / log-prob 前向。即使权重与 Actor 同构，也常是第二份驻留，或与 Actor 分时加载。别从账单里默默删掉。

Activation 按 `micro-batch` $\times$ 回复长度走。GRPO 一次对 $G$ 条 completion 计算 loss，有效 token 数是 $B\cdot G\cdot T_{\mathrm{resp}}$，比同 batch 的 SFT 更容易把激活打满。Checkpointing、序列切分、对 pad 做 `response_mask` 都是在削这本账。

## 2. Rollout 侧：KV 乘的是 $G$，不是 $1$

每个 输入提示（prompt） 采 $G$ 条长回复。vLLM / SGLang 上每条都有一份 KV。$G=8$、$T=8\mathrm{k}$ 时，KV 足迹按「单条 decode KV $\times 8$」涨；长 思维链（CoT，即分步推理过程） 的尾部序列会把并发度顶死。GRPO 的组采样是算法需要，不是可忽略的实现细节。

采样还要 logits、draft 缓冲、tokenizer 工作区。若和训练 **colocate**，同一 GPU 上可能同时（或分时切换）挂着训练状态与推理引擎。峰值是两本账的叠加或切换毛刺，不是 $\max$ 的理论下界。

## 3. 通信与优化顺序

集体通信的 gather / reduce-scatter 缓冲、异步权重同步的 staging，会在 step 边界再抬一截。优化不要一上来换框架：

1. **先砍乘数：** 截断无意义长尾、控制 $G$ 与并发、prompt 去重。组全对 / 全错时 advantage 本就是 $0$，白占 KV。
2. **再砍训练状态：** activation checkpoint、ZeRO/FSDP、合适的 TP/PP；reference 用 LoRA / 更低精度前向或 CPU offload（若延迟可接受）。
3. **最后改拓扑：** colocate 省权重拷贝，但显存毛刺大；disaggregate 让 rollout 与 trainer 独立扩容，代价是参数同步与 staleness。

把「训练 backward OOM」和「engine KV OOM」分开：前者动 checkpoint / ZeRO，后者动 paging、并发、$G$ 和长度。

## 追问

- **去掉 Critic 能省多少？** 大约省掉一份与 Actor 同阶的 $V_\psi$ 状态（参数+Adam+其激活）。7B 上很可观，但仍可能小于「$G$ 条长 KV + Actor Adam」。
- **Reference 能否和 Actor 共享权重？** 共享则 KL 恒为 $0$。必须是冻结快照；能共享的是**存储格式与并行切分**，不是同一份可训练张量。
- **为什么有时 80GB 卡仍 OOM？** 未分片 Adam、过长 $T$、过大 $G$、colocate 双引擎，任一峰值都够把 80GB 打穿。先问 OOM 发生在 train 还是 generate。
