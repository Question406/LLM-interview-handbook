---
id: openai-instructgpt-kl
section: openai
order: 4
level: S
title: OpenAI / InstructGPT：RLHF 为什么要加相对 SFT 的 KL？方向是哪边？
quick: "奖励里减 $\\beta\\log(\\pi_\\theta/\\pi_{\\mathrm{ref}})$，即反向 KL $(\\pi_\\theta\\|\\pi_{\\mathrm{ref}})$，防止策略漂离 SFT 去刷 RM。它和 PPO clip 相对 $\\pi_{\\mathrm{old}}$ 的一步约束是两回事。"
tags:
  - OpenAI
  - RLHF
  - KL
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
---

OpenAI 系对齐岗不一定按国内口径问 GRPO，但 InstructGPT 这篇是默认背景。KL 说错方向，后面 PPO/GRPO 全套都会拧。系统拆分见 `pt-rlhf-why-reverse-kl` 和阿里卡 `ali-grpo-kl-vs-ppo`；本题按 OpenAI 论文原设定收。

## 两个锚，不要合成一个 $\beta$

InstructGPT 的 强化学习（RL） 阶段用 PPO，奖励大致是

$$
r(x,y)=r_{\phi}(x,y)-\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

$\pi_{\mathrm{ref}}$ 通常是冻结 监督微调（SFT）。这一项是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 的样本估计：当前策略相对 SFT 的反向 KL。它惩罚「SFT 几乎不写、RM 却很喜欢」的句子，用来压 钻奖励规则的空子 和语言崩坏。

PPO clip 相对的是 $\pi_{\mathrm{old}}$（本批 采样轨迹（rollout） 策略）：

$$
\rho=\frac{\pi_\theta}{\pi_{\mathrm{old}}},\qquad
\min(\rho A,\ \mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A).
$$

clip 管本步更新别太大；ref KL 管整段训练别离开可用语言。两个系数、两个参照，不要答成「KL 就是 PPO」。

## 白板怎么讲失败模式

- $\beta$ 太小：长度变长、套话、奖励模型（RM） 分数涨、人工一看在刷分。InstructGPT 自己也写了 基于人类反馈的强化学习（RLHF） 会引入 RM overoptimization。
- $\beta$ 太大：KL 预算几步就花完，奖励分数（reward） 不动，等于没做 RL。
- 只 clip 不设 ref：短训可以，长训容易漂。DAPO 一类去掉 KL、改靠 clip 和动态采样，那是另一条实现，答的时候要声明你讲的是 InstructGPT 原设定。

监控四条曲线：相对 old 的 KL、相对 ref 的 KL、reward、平均长度。长度和 reward 一起飙、ref KL 也飙，优先怀疑 hacking 而不是「学得很好」。

SFT 本身是前向 KL $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，覆盖示范模式。RLHF 的惩罚项是反向 KL，集中在当前 $\pi_\theta$ 会采样到的地方。把 SFT 说成反向 KL 是常见口误。

## 追问

- **为什么不是 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$？** 那个会强迫覆盖 ref 的全程质量，探索更死。RLHF 要的是「你现在会说的话别太离谱」，所以是 $\pi_\theta$ 在前。
- **直接偏好优化（DPO） 还要这个 KL 吗？** DPO 把 RM + KL 解析掉了，隐式先验仍是 $\pi_{\mathrm{ref}}$，但实现上不再单独减一项 token KL。
- **和 GRPO 论文的 $k_3$ KL？** DeepSeekMath 把 KL 加进 loss 而不是扣进 reward，锚仍是 ref。名字都叫 KL，代码位置不同。
