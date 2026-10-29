---
id: openai-lora-sft
section: openai
order: 23
level: A
title: OpenAI：对基座做 LoRA SFT，rank、目标模块和全参怎么取舍
quick: >-
  我会先按任务选择 LoRA 覆盖模块，再单独试 rank：风格格式可从 8 或 16 起，领域迁移再试
  32–64。新任务与旧能力一起评估，容量不够或域偏移大时比较全参；显存、服务方式和遗忘风险共同决定选择。
tags:
  - OpenAI
  - LoRA
  - SFT
  - Fine-tuning
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: LoRA — Low-Rank Adaptation of Large Language Models
    url: 'https://arxiv.org/abs/2106.09685'
    type: primary
  - title: QLoRA — Efficient Finetuning of Quantized LLMs
    url: 'https://arxiv.org/abs/2305.14314'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 可以这样回答

我会按域偏移、显存和部署需求选 LoRA 或全参，再用验证集决定 rank 与目标模块。比如同一基座要挂许多客户 adapter，LoRA 方便共享权重；若只服务一个模型、需要大幅改领域且能接受遗忘，全参值得比较。

InstructGPT 第一阶段用全参 SFT，OpenAI 微调 API 历史上也对部分模型全参更新。LoRA 来自 Hu et al.，QLoRA 则在量化基座上做低秩更新，这些是公开方法。

## 技术备查

我会按域偏移、显存和部署需求选 LoRA 或全参，再用验证集决定 rank 与目标模块。比如同一基座要挂许多客户 adapter，LoRA 方便共享权重；若只服务一个模型、需要大幅改领域且能接受遗忘，全参值得比较。

InstructGPT 第一阶段用全参 SFT，OpenAI 微调 API 历史上也对部分模型全参更新。LoRA 来自 Hu et al.，QLoRA 则在量化基座上做低秩更新，这些是公开方法。

## 公式、rank、改哪些层

冻结 $W\in\mathbb{R}^{d\times k}$，只训

$$
W' = W + \frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k}.
$$

$A$ 常高斯初始化，$B$ 置零，开始时 $\Delta W=0$，不会一上来把预训练冲掉。$\alpha/r$ 是步长标定：改 $r$ 时若想保持有效更新幅度，要一起看 $\alpha$。可训参数大约 $r(d+k)$，相对 $dk$ 是 $O(r/\min(d,k))$。

我会这么选 $r$：指令风格和格式，$8$ 或 $16$ 往往够；换领域（医学、私有代码、另一种语言）再试 $32$–$64$。$r$ 加到接近全秩就失去 LoRA 的意义，等于用更别扭的方式做全参。验证集不涨时，先加目标模块，再加 $r$，不要两个一起拧。

目标模块先覆盖 attention 的 $W_q,W_k,W_v,W_o$。只改 $q,v$ 能运行，但指令遵循、长依赖可能还不够。数学、代码 SFT 会再覆盖 MLP 的 gate / up / down，它们参数多、也影响拟合。Embedding、LayerNorm / RMSNorm 默认冻结，扩 vocabulary 时再单独考虑，相关见 `openai-tiktoken`。

学习率通常比全参高一档（常见 $10^{-4}$ 量级，而全参 SFT 更接近 $10^{-5}$），因为更新落在低秩残差上。仍要 warmup。Dropout 打在 adapter 上，不要再给冻结的 $W$ 加一份。

## 和全参怎么选

域偏移大、拥有 checkpoint、只部署一个模型且可接受灾难遗忘时，可以用全参，InstructGPT SFT 就属于这类设定。评测要同时看新任务和旧能力，训练集 loss 下降说明不了旧能力还在。

许多客制化共享基座、快速扫超参或显存只够冻骨干时，LoRA 更方便。单 adapter 可 merge 回 $W$，按普通模型跑，不增加额外延迟；多 adapter 才需要 `nvidia-lora-serve` 里的专门 kernel。

LoRA 更新容量小可能减少遗忘，也可能在域偏移大时拟合不上，不能据此保证更安全。用在 RLHF 的 reward model 或 PPO 策略时，仍需 `openai-instructgpt-kl` 的冻结 ref 作为 KL 锚，rank $r$ 不提供这种约束。

QLoRA：基座 4bit，adapter 16bit。面试分开报：量化省的是基座显存；低秩省的是可训参数。两者可叠，是两个旋钮。

```python
# 形状：x 是 [B, T, k]，W 是 [d, k]
delta = (alpha / r) * (x @ A.T @ B.T)  # [B, T, d]
y = F.linear(x, W) + delta
```

核对实现可以用 $r=0$ 或 $B=0$ 时输出应等于基座这个不变量，再分别验证模块覆盖、rank 和 merge。

## 追问

**$\alpha$ 和 $r$ 哪个当步长？**
有效缩放是 $\alpha/r$。只改 $r$ 不改 $\alpha$，更新幅度会变。报超参时两个一起报。
**LoRA 能代替 InstructGPT 的 SFT 吗？**
风格和格式可以。要大幅改知识或工具行为，全参或至少把 MLP 加进去更常见。
**多个 adapter 怎么部署？**
单客制 merge；多客制才分核。基座权重要共享，不要每个租户一份全参。
**和 DPO / PPO 怎么接？**
先 SFT（LoRA 或全参）再偏好优化。ref 策略必须冻，见 `openai-dpo-loss`。
