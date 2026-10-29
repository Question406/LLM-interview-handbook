---
id: openai-ppo-clip
section: openai
order: 9
level: S
title: OpenAI：PPO clip 在 InstructGPT/RLHF 里在干什么，ratio 爆了怎么收
quick: >-
  假设旧策略选择某个动作的概率是 0.2，新策略变成 0.3，ratio 就是 1.5。若这个动作的 advantage 为正，PPO
  不希望仅凭这一批经验就一直把它推高。
tags:
  - OpenAI
  - PPO
  - RLHF
  - InstructGPT
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 回答思路

> **问题与场景：** 假设旧策略选择某个动作的概率是 0.2，新策略变成 0.3，ratio 就是 1.5。
>
> **做法与原因：** Clipped objective 在有利方向超过范围后削平进一步收益。
>
> **检查与取舍：** 我会用正负两个 advantage 分别代入公式，再看实际 KL、ratio 分布和重复训练次数。

## 可以这样回答

假设旧策略选择某个动作的概率是 0.2，新策略变成 0.3，ratio 就是 1.5。若这个动作的 advantage 为正，PPO 不希望仅凭这一批经验就一直把它推高。

Clipped objective 在有利方向超过范围后削平进一步收益。Advantage 为负时，要按相反方向分析；它不是把所有 ratios 截到范围里，也不是严格保证每步 KL 都很小。

我会用正负两个 advantage 分别代入公式，再看实际 KL、ratio 分布和重复训练次数。这样比只说“防止更新太大”更准确。

## 技术备查

PPO clip 约束相对本批 sampling 策略的更新收益，ref KL 则限制整个训练期间偏离 SFT 的程度。比如每轮都只走一小步，很多轮后仍可能走得很远，这就是两个参照都需要说明的原因。下面按 InstructGPT 和 PPO 公开设定讨论，KL 方向可对照 `openai-instructgpt-kl`。

## 两个锚，clip 只管其中一个

InstructGPT 的 RL 阶段用 PPO。奖励里已经减了相对冻结的 SFT 模型的 token 级 KL，用来约束整个训练过程中策略偏离 reference model 的程度。

clip 相对的是本批 sampling 轨迹（rollout）的 $\pi_{\mathrm{old}}$：

$$
\rho_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)},\qquad
L=\mathbb{E}\big[\min\big(\rho_t A_t,\ \mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)A_t\big)\big].
$$

$\varepsilon$ 常见 $0.1$ 到 $0.2$。$\min$ 取悲观端：$A>0$ 时不让 $\rho$ 无限上涨；$A<0$ 时不让 $\rho$ 无限下降。它不替代 ref KL。只 clip 不设 ref，短训能走，长训仍会漂到 reward model（RM） 喜欢的套话，这是 InstructGPT 自己写过的 overoptimization。

SFT 是前向 KL，RL 惩罚项是 reverse KL，clip 是信任域。三个东西三个参照。

## ratio 变大以后怎么排查

语言模型的 $\rho$ 很容易炸。序列级

$$
\rho_{\mathrm{seq}}=\exp\sum_t\big(\log\pi_\theta-\log\pi_{\mathrm{old}}\big)
$$

随 $T$ 指数放大。一个 token 上 $0.1$ nat 的差，$T=200$ 就是 $e^{20}$。这时：

先检查目标 $L$ 中 clip 进入哪一侧的 surrogate。对被削平的有利分支，$\rho A$ 再大也只取 $1\pm\varepsilon$ 对应项；其他未 clip 的 token 仍能提供梯度，inner epoch 太多，$\pi_\theta$ 会持续离开 $\pi_{\mathrm{old}}$。

再同时监控相对 old 和 ref 的 KL。OpenAI 原版 PPO 有 target-KL，InstructGPT 把 KL 放进 reward；old KL 飙升时减 lr 或停止这批，ref KL 飙升时调高 $\beta$ 并检查刷 RM。GAE 尺度漂移也会让 $A$ 放大更新，所以要检查 advantage 归一和 value clip。

减少 PPO epoch，用小 batch 多次同步，LLM-RL 中 2 到 4 个 epoch 已经偏多。token 级 ratio 配双 clip 是后来的一种补丁：负优势且 $\rho\gg 1$ 时会出现巨大的负项，对负 $A$ 另加上限以限制它；这不属于 InstructGPT 原文。

最后看 ratio 直方图。大量 $\rho$ 超出 $1\pm\varepsilon$ 时，这批数据对当前策略已偏得太远，应考虑丢掉并重新 sampling。

和 DPO 对比见 `openai-dpo-loss`：DPO 没有这套 on-policy $\rho$，爆炸模式换成 log-prob 差和 length bias。

## 追问

**clip 能防止模型钻奖励规则的空子吗？**
不能。hacking 是 RM 的错，要用 ref KL、长度惩罚和人工抽查。clip 只防一步走太远。
**为什么不直接 TRPO？**
TRPO 要二阶约束，PPO 用 clip 近似信任域，好实现、好和大模型 backpropagation 叠。
**$\rho$ 用 log 空间怎么写？**
`log_ratio = new_logp - old_logp`，`rho = exp(log_ratio)`，先 clamp `log_ratio` 再 exp，避免 overflow。
**和 GRPO？**
组内相对优势，没有 价值评估模型（critic）；clip 往往还在。锚仍要说清是 old 还是 ref。

## 相关题

- [[sys-kl-place]]：这里的「两个锚」里 ref KL 那一个怎么接，写进奖励还是写进 loss，梯度走法不同。
- [[fireworks-grpo-sft-loss]]：把 clipped 目标写成 detach 权重乘 logprob 的代码题，clip mask 在那里是单侧的。
- [[coding-cispo]]：PPO clip 让出界 token 的梯度变 0，CISPO 改成截断权重、保留梯度，两者并排对照。
- [[anthropic-grpo-debug]]：调试题修完后会追问 ratio 为什么不是 1、第一步 clip 有没有用，正好接这张。
- [[coding-gae]]：PPO 里 advantage 的来源，手写 GAE 递推和 value clip。
- [[align-reward-hack]]：追问里说 clip 防不了 hacking，那张讲 hacking 的具体样子和怎么发现。
