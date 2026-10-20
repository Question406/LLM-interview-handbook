---
id: openai-ppo-clip
section: openai
order: 9
level: S
title: OpenAI：PPO clip 在 InstructGPT/RLHF 里在干什么，ratio 爆了怎么收
quick: "clip 只限制相对 $\\pi_{\\mathrm{old}}$ 的一步更新，不管离 SFT 多远。$\\rho$ 爆掉时先靠 clip，再加 KL 早停、advantage 归一和更少的 inner epoch。"
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

InstructGPT 的强化学习（RL）阶段用 PPO。奖励里已经减了相对冻结的监督微调（SFT）模型的 token 级 KL，用来约束整个训练过程中策略偏离参考模型的程度。

clip 相对的是本批采样轨迹（rollout）的 $\pi_{\mathrm{old}}$：

$$
\rho_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)},\qquad
L=\mathbb{E}\big[\min\big(\rho_t A_t,\ \mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)A_t\big)\big].
$$

$\varepsilon$ 常见 $0.1$ 到 $0.2$。$\min$ 取悲观端：$A>0$ 时不让 $\rho$ 无限上涨；$A<0$ 时不让 $\rho$ 无限下降。它不替代 ref KL。只 clip 不设 ref，短训能走，长训仍会漂到 奖励模型（RM） 喜欢的套话，这是 InstructGPT 自己写过的 overoptimization。

SFT 是前向 KL，RL 惩罚项是反向 KL，clip 是信任域。三个东西三个参照。

## ratio 爆了，我会按层收

语言模型的 $\rho$ 很容易炸。序列级

$$
\rho_{\mathrm{seq}}=\exp\sum_t\big(\log\pi_\theta-\log\pi_{\mathrm{old}}\big)
$$

随 $T$ 指数放大。一个 token 上 $0.1$ nat 的差，$T=200$ 就是 $e^{20}$。这时：

1. 先承认 clip 已经在挡 surrogate。 未 clip 的 $\rho A$ 再大，进入 $L$ 的是 $1\pm\varepsilon$。但梯度仍可能从没被 clip 到的 token 进来，inner epoch 一多，$\pi_\theta$ 会一步步走出 $\pi_{\mathrm{old}}$ 的 $\varepsilon$ 球。
2. 对 ref 的 KL 早停 / 自适应 $\beta$。 OpenAI 原版 PPO 就有 target-KL；InstructGPT 把 KL 放进 奖励分数（reward）。监控两条 KL：对 old、对 ref。old KL 飙了减 lr 或停这批，ref KL 飙了加 $\beta$ 或查 钻奖励规则的空子。
3. advantage 归一、value clip。 GAE 的尺度一漂，$\rho$ 再稳 $A$ 也会导致更新幅度过大。
4. 少 PPO epoch、小 batch 多次同步。 LLM-RL 里 2 到 4 个 epoch 已经偏多。
5. token 级 ratio + 双 clip。 负优势且 $\rho\gg 1$ 时，坏 token 被放大的概率会给巨大负项；对负 $A$ 再加一道上限是后来 LLM PPO 的补丁，要声明不是 InstructGPT 原文。

ratio 直方图是我一定会提的仪表：大量 $\rho$ 贴在 $1\pm\varepsilon$ 墙外，说明这批已经不可信，该丢而不是硬训。

和 直接偏好优化（DPO） 对比见 `openai-dpo-loss`：DPO 没有这套 on-policy $\rho$，爆炸模式换成 log-prob 差和长度偏差。

## 追问

- **clip 能防止模型钻奖励规则的空子吗？** 不能。hacking 是 RM 的错，要用 ref KL、长度惩罚和人工抽查。clip 只防一步走太远。
- **为什么不直接 TRPO？** TRPO 要二阶约束，PPO 用 clip 近似信任域，好实现、好和大模型反传叠。
- **$\rho$ 用 log 空间怎么写？** `log_ratio = new_logp - old_logp`，`rho = exp(log_ratio)`，先 clamp `log_ratio` 再 exp，避免 overflow。
- **和 GRPO？** 组内相对优势，没有 价值评估模型（critic）；clip 往往还在。锚仍要说清是 old 还是 ref。

## 相关题

- [[sys-kl-place]]：这里的「两个锚」里 ref KL 那一个怎么接，写进奖励还是写进 loss，梯度走法不同。
- [[fireworks-grpo-sft-loss]]：把 clipped 目标写成 detach 权重乘 logprob 的代码题，clip mask 在那里是单侧的。
- [[coding-cispo]]：PPO clip 让出界 token 的梯度变 0，CISPO 改成截断权重、保留梯度，两者并排对照。
- [[anthropic-grpo-debug]]：调试题修完后会追问 ratio 为什么不是 1、第一步 clip 有没有用，正好接这张。
- [[coding-gae]]：PPO 里 advantage 的来源，手写 GAE 递推和 value clip。
- [[align-reward-hack]]：追问里说 clip 防不了 hacking，那张讲 hacking 的具体样子和怎么发现。
