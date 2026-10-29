---
id: openai-instructgpt-kl
section: openai
order: 4
level: S
title: OpenAI / InstructGPT：RLHF 为什么要加相对 SFT 的 KL？方向是哪边？
quick: >-
  InstructGPT 在奖励里减去当前策略相对冻结 SFT 的 KL，约束策略长期漂移、减少刷 reward model。PPO clip 的参照是本批
  rollout 的 old 策略，只管这批更新，两者要分别监控和调节。
tags:
  - OpenAI
  - RLHF
  - KL
  - InstructGPT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary
---

InstructGPT 用相对冻结 SFT 的 KL 惩罚限制长期漂移，PPO clip 则限制当前策略相对本批 sampling 策略的变化。比如一句话 SFT 几乎不会写，RM 却给很高分，ref KL 就会增加代价；即使每步都被 clip 约束，长期仍需要这个参照。这里按 InstructGPT 论文原设定解释。

## 奖励和更新分别参照谁

InstructGPT 的 RL 阶段用 PPO，奖励大致是

$$
r(x,y)=r_{\phi}(x,y)-\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

$\pi_{\mathrm{ref}}$ 通常是冻结 SFT。这一项是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 的样本估计：当前策略相对 SFT 的 reverse KL。它惩罚「SFT 几乎不写、RM 却很喜欢」的句子，用来压 钻奖励规则的空子 和语言崩坏。

PPO clip 相对的是 $\pi_{\mathrm{old}}$（本批 sampling 轨迹（rollout） 策略）：

$$
\rho=\frac{\pi_\theta}{\pi_{\mathrm{old}}},\qquad
\min(\rho A,\ \mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A).
$$

clip 管本步更新别太大；ref KL 管整段训练别离开可用语言。两个系数、两个参照，不要答成「KL 就是 PPO」。

实际调参时，$\beta$ 太小会出现回答更长、套话更多、RM 分上涨但人评发现刷分，InstructGPT 也讨论了 RM overoptimization。$\beta$ 太大又会过度约束，几步就用完 KL 预算，reward 几乎不动。

只做 clip 的短训练可能可用，长训练仍会漂。DAPO 一类移除 KL、依靠 clip 和动态 sampling，是另一套实现，不能与这里的 InstructGPT 设定混用。

监控四条曲线：相对 old 的 KL、相对 ref 的 KL、reward、平均长度。长度和 reward 一起飙、ref KL 也飙，优先怀疑 hacking 而不是「学得很好」。

SFT 本身是前向 KL $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，覆盖示范模式。RLHF 的惩罚项是 reverse KL，集中在当前 $\pi_\theta$ 会 sampling 到的地方。把 SFT 说成 reverse KL 是常见口误。

相关：`pt-rlhf-why-reverse-kl`、`ali-grpo-kl-vs-ppo`

## 追问

**为什么不是 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$？**
那个会强迫覆盖 ref 的全程质量，探索更死。RLHF 要的是「你现在会说的话别太离谱」，所以是 $\pi_\theta$ 在前。
**DPO 还要这个 KL 吗？**
DPO 把 RM + KL 解析掉了，隐式先验仍是 $\pi_{\mathrm{ref}}$，但实现上不再单独减一项 token KL。
**和 GRPO 论文的 $k_3$ KL？**
DeepSeekMath 把 KL 加进 loss 而不是扣进 reward，锚仍是 ref。名字都叫 KL，代码位置不同。
