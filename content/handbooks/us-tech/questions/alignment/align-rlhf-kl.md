---
id: align-rlhf-kl
section: alignment
order: 1
level: S
title: 对齐：RLHF 为什么加 reverse KL 到 SFT 模型，正向 KL 会怎样
quick: "RLHF 常用反向 KL 约束当前策略：模型现在生成的回答若在 SFT 中概率很低，就会受罚；SFT 里的有害模式则允许不再覆盖。正向 KL 更强调覆盖参考分布，会惩罚丢掉这些模式，因此两者对对齐的作用不同。"
tags:
  - OpenAI
  - RLHF
  - KL
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Aligning language models to follow instructions
    url: https://openai.com/index/instruction-following/
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

RLHF 用反向 KL，是为了限制当前策略生成参考模型很少说的回答，同时允许它丢掉参考模型中的有害模式。可以想成 SFT 既会给有用回答，也残留一些有害回答；对齐时希望保住前者、压低后者。反向和正向 KL 对「漏掉参考模式」的惩罚不同。

## 反向 KL 怎么约束当前策略

InstructGPT 的 强化学习（RL） 目标可以写成

$$
\max_\theta\ \mathbb{E}_{x,\,y\sim\pi_\theta}\big[r_\phi(x,y)\big]-\beta\,D_{\mathrm{KL}}\big(\pi_\theta(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

展开就是奖励里减 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。期望在 **当前策略** 上取：$\pi_\theta$ 跑到 $\pi_{\mathrm{ref}}\approx 0$ 的地方，$\log$ 比爆炸。这个惩罚可以限制模型生成胡话或钻奖励规则的空子。$\pi_{\mathrm{ref}}$ 有、$\pi_\theta$ 不去的峰几乎不进期望，所以 **允许遗忘**。监督微调（SFT）里残留的毒性、套话、过度承诺，可以对齐掉。这是 mode-seeking，不是实现 bug。

$\pi_{\mathrm{ref}}$ 通常用冻结的 SFT 模型。用 base 当锚，可能连 SFT 学会的指令格式也当成偏离来罚；用约束很强、已经对齐过的模型，又可能把探索空间压得太小。

PPO clip 相对本批 $\pi_{\mathrm{old}}$，限制单步更新；ref KL 相对 $\pi_{\mathrm{ref}}$，限制整段训练的漂移。两者参照和系数不同，监控时也要分开。

## 换成正向 KL 会怎样

若改成 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$，期望改到 $\pi_{\mathrm{ref}}$ 上。参考在某处概率为正，策略在该处接近 0 就会被重罚。于是 $\pi_\theta$ **必须继续覆盖 SFT 的每一个高概率模式**，包括我们想丢掉的有害峰。对齐要的是收窄：抬有用、无害的峰，丢掉毒性、拍马、拒答失败。正向 KL 会惩罚模型降低这些模式的概率。

采样也对不上。PPO 从 $\pi_\theta$ 采样训练轨迹（rollout），估计反向 KL 可以直接复用这些样本，不需要额外采样。正向要从 $\pi_{\mathrm{ref}}$ 再抽一条，管道多一路参考生成，和 on-policy 循环不合。硬换成交叉熵更糟：$H(\pi_{\mathrm{ref}},\pi_\theta)=H(\pi_{\mathrm{ref}})+D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$，那是正向 KL 加一项与 $\pi_\theta$ 无关的熵。

在前面的双峰例子里，反向 KL 允许策略不再覆盖有害峰；正向 KL 会惩罚遗漏参考分布有质量的区域，因而更难压低这个峰。

SFT 阶段的方向又有所不同。

SFT / MLE 最小化 $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，mode-covering：示范里出现过的写法都得给质量。基于人类反馈的强化学习（RLHF） 的惩罚项是反向的。两阶段方向不同，不能说「对齐都在做 KL」。可以理解为先通过 covering 学会示范中的技能，再通过 seeking 按奖励调整输出。

训练时我会一起监控四条：相对 old 的 KL、相对 ref 的 KL、奖励分数（reward）、平均长度。长度和 reward 一起飙、ref KL 也飙，优先怀疑 hacking，见 `align-reward-hack`。KL 大不一定是坏事：参考很少拒答、对齐成功学会拒答，KL 也会升，要对着安全评测一起读。

DPO 从带这个反向 KL 的目标出发，最优策略 $\pi_\theta\propto\pi_{\mathrm{ref}}\exp(r/\beta)$。方向写反，隐式奖励换元对不上，见 `align-dpo`。

Token 级实现只在 response mask 上平均 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$。把输入提示（prompt）算进 KL，会把「读懂问题」当偏离来罚。

相关：`openai-instructgpt-kl`。

## 追问

**为什么不是 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$？**
那个强迫覆盖 ref 全程质量，有害峰丢不掉，探索更死。RLHF 要的是「你现在会说的话别太离谱」，所以 $\pi_\theta$ 在前。
**$\beta$ 太小 / 太大？**
太小：长度膨胀、套话、奖励模型（RM） 分涨、人工一看在刷分。太大：KL 预算几步花完，reward 不动，等于没做 RL。
**和 PPO clip 重复吗？**
不重复。Clip 限单步；ref KL 限长期漂。只 clip 不设 ref，短训可以，长训容易离开可用语言。
**Reference 用 SFT 还是 base？**
常用 SFT。用 base 会把格式当偏离罚掉。
