---
id: openai-lora-sft
section: openai
order: 23
level: A
title: OpenAI：对基座做 LoRA SFT，rank、目标模块和全参怎么取舍
quick: >-
  LoRA 把 $\Delta W=(\alpha/r)BA$ 加在冻结的 $W$ 上，$B$ 是 $[d,r]$、$A$ 是 $[r,k]$，$r$ 远小于宽。SFT 风格迁移
  常用 $r=8$–$16$，域偏移大再加到 64+，目标至少覆盖注意力的 $q,k,v,o$，难任务再加 MLP。全参拟合更强也更易忘；LoRA
  主要赢在多租户和实验速度。
tags:
  - OpenAI
  - LoRA
  - SFT
  - Fine-tuning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: LoRA — Low-Rank Adaptation of Large Language Models
    url: https://arxiv.org/abs/2106.09685
    type: primary
  - title: QLoRA — Efficient Finetuning of Quantized LLMs
    url: https://arxiv.org/abs/2305.14314
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

InstructGPT 的第一段是全参 SFT；OpenAI 微调 API 历史上也对部分模型做全参更新。研究岗仍会问 LoRA，因为内部实验、客制化、多租户服务都要在「不动基座」和「真改行为」之间取舍。论文是 Hu et al.；QLoRA 是量化基座上的同一低秩更新。LoRA 不是 OpenAI 发明的。对齐主线见 `openai-instructgpt-kl`，部署侧见 `nvidia-lora-serve`。

## 公式、rank、改哪些层

冻结 $W\in\mathbb{R}^{d\times k}$，只训

$$
W' = W + \frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k}.
$$

$A$ 常高斯初始化，$B$ 置零，开始时 $\Delta W=0$，不会一上来把预训练冲掉。$\alpha/r$ 是步长标定：改 $r$ 时若想保持有效更新幅度，要一起看 $\alpha$。可训参数大约 $r(d+k)$，相对 $dk$ 是 $O(r/\min(d,k))$。

我会这么选 $r$：指令风格和格式，$8$ 或 $16$ 往往够；换领域（医学、私有代码、另一种语言）再试 $32$–$64$。$r$ 加到接近全秩就失去 LoRA 的意义，等于用更别扭的方式做全参。验证集不涨时，先加目标模块，再加 $r$，不要两个一起拧。

目标模块：最低限度是注意力的 $W_q,W_k,W_v,W_o$。只改 $q,v$ 能跑，但指令遵循和长依赖常不够。MLP 的 gate / up / down 参数量大、贡献也大，数学和代码 SFT 我会默认加上。Embedding 和 LayerNorm / RMSNorm 默认不动，除非在扩词表；扩表本身见 `openai-tiktoken`。

学习率通常比全参高一档（常见 $10^{-4}$ 量级，而全参 SFT 更接近 $10^{-5}$），因为更新落在低秩残差上。仍要 warmup。Dropout 打在 adapter 上，不要再给冻结的 $W$ 加一份。

## 和全参怎么选

全参：域偏移大、你拥有 checkpoint、可以接受灾难遗忘、服务时只跑一个模型。InstructGPT 的 SFT 是这个设定。评测要同时看新任务和旧能力，不要只报 SFT 集的 loss。

LoRA：同一基座上挂很多客制化、要快速扫超参、或显存只够冻骨干。服务时若只有一个 adapter，merge 回 $W$ 再当普通模型跑，没有额外延迟。多 adapter 才需要单独的 LoRA kernel，那是 `nvidia-lora-serve` 的题。

错法：把 LoRA 说成「一定比全参更不容易忘」。忘得少是因为容量小、更新小；域偏移大时它只是拟合不上，不是更安全的对齐。另一错法：在 RLHF 的 reward model 或 PPO 策略上随手 LoRA 却不谈 KL 锚，锚仍要靠 `openai-instructgpt-kl` 那套 ref，不是靠 $r$。

QLoRA：基座 4bit，adapter 16bit。面试分开报：量化省的是基座显存；低秩省的是可训参数。两者可叠，是两个旋钮。

```python
# 形状：x 是 [B, T, k]，W 是 [d, k]
delta = (alpha / r) * (x @ A.T @ B.T)   # [B, T, d]
y = F.linear(x, W) + delta
```

先说不变量（$r=0$ 或 $B=0$ 时输出等于基座），再谈 $r$、模块、merge。不要一上来背「只改 q,v」。

## 追问

- **$\alpha$ 和 $r$ 哪个当步长？** 有效缩放是 $\alpha/r$。只改 $r$ 不改 $\alpha$，更新幅度会变。报超参时两个一起报。
- **LoRA 能代替 InstructGPT 的 SFT 吗？** 风格和格式可以。要大幅改知识或工具行为，全参或至少把 MLP 加进去更常见。
- **多个 adapter 怎么服？** 单客制 merge；多客制才分核。基座权重要共享，不要每个租户一份全参。
- **和 DPO / PPO 怎么接？** 先 SFT（LoRA 或全参）再偏好优化。ref 策略必须冻，见 `openai-dpo-loss`。
