---
id: openai-ppo-clip
section: openai
order: 9
level: S
title: OpenAI：PPO clip 在 InstructGPT/RLHF 里在干什么，ratio 爆了怎么收
quick: >-
  clip 限制的是相对 $\pi_{\mathrm{old}}$ 的一步更新，不是相对 SFT 的语言锚。$\rho=\pi_\theta/\pi_{\mathrm{old}}$
  爆掉时，先靠 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$，再 KL 早停、advantage 归一、少 inner epoch。
  序列级 $\rho$ 随长度指数炸，token 级 clip 更稳。
tags:
  - OpenAI
  - PPO
  - RLHF
  - InstructGPT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

InstructGPT 是 OpenAI 对齐岗的默认背景。KL 方向见 `openai-instructgpt-kl`。这题专门收 PPO clip：很多人把 clip 和 ref KL 答成同一个 $\beta$。先拆两个锚，再讲 ratio 爆炸。

## 两个锚，clip 只管其中一个

InstructGPT 的 RL 阶段用 PPO。奖励里已经减了相对冻结 SFT 的 token KL。那是整段训练别离开可用语言。

clip 相对的是本批 rollout 的 $\pi_{\mathrm{old}}$：

$$
\rho_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)},\qquad
L=\mathbb{E}\big[\min\big(\rho_t A_t,\ \mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)A_t\big)\big].
$$

$\varepsilon$ 常见 $0.1$–$0.2$。$\min$ 取悲观端：$A>0$ 时不让 $\rho$ 无地上涨；$A<0$ 时不让 $\rho$ 无地下降。它不替代 ref KL。只 clip 不设 ref，短训能走，长训仍会漂到 RM 喜欢的套话，这是 InstructGPT 自己写过的 overoptimization。

SFT 是前向 KL，RL 惩罚项是反向 KL，clip 是信任域。三个东西三个参照。

## ratio 爆了，我会按层收

语言模型的 $\rho$ 很容易炸。序列级

$$
\rho_{\mathrm{seq}}=\exp\sum_t\big(\log\pi_\theta-\log\pi_{\mathrm{old}}\big)
$$

随 $T$ 指数放大。一个 token 上 $0.1$ nat 的差，$T=200$ 就是 $e^{20}$。这时：

1. 先承认 clip 已经在挡 surrogate。 未 clip 的 $\rho A$ 再大，进入 $L$ 的是 $1\pm\varepsilon$。但梯度仍可能从没被 clip 到的 token 进来，inner epoch 一多，$\pi_\theta$ 会一步步走出 $\pi_{\mathrm{old}}$ 的 $\varepsilon$ 球。
2. 对 ref 的 KL 早停 / 自适应 $\beta$。 OpenAI 原版 PPO 就有 target-KL；InstructGPT 把 KL 放进 reward。监控两条 KL：对 old、对 ref。old KL 飙了减 lr 或停这批，ref KL 飙了加 $\beta$ 或查 reward hacking。
3. advantage 归一、value clip。 GAE 的尺度一漂，$\rho$ 再稳 $A$ 也会把更新拉飞。
4. 少 PPO epoch、小 batch 多次同步。 LLM-RL 里 2–4 个 epoch 已经偏多。
5. token 级 ratio + 双 clip。 负优势且 $\rho\gg 1$ 时，坏 token 被放大的概率会给巨大负项；对负 $A$ 再加一道上限是后来 LLM PPO 的补丁，要声明不是 InstructGPT 原文。

ratio 直方图是我一定会提的仪表：大量 $\rho$ 贴在 $1\pm\varepsilon$ 墙外，说明这批已经不可信，该丢而不是硬训。

和 DPO 对比见 `openai-dpo-loss`：DPO 没有这套 on-policy $\rho$，爆炸模式换成 log-prob 差和长度偏差。

## 追问

- **clip 能防 reward hacking 吗？** 不能。hacking 是 RM 的错，要用 ref KL、长度惩罚和人工抽查。clip 只防一步走太远。
- **为什么不直接 TRPO？** TRPO 要二阶约束，PPO 用 clip 近似信任域，好实现、好和大模型反传叠。
- **$\rho$ 用 log 空间怎么写？** `log_ratio = new_logp - old_logp`，`rho = exp(log_ratio)`，先 clamp `log_ratio` 再 exp，避免 overflow。
- **和 GRPO？** 组内相对优势，没有 critic；clip 往往还在。锚仍要说清是 old 还是 ref。
