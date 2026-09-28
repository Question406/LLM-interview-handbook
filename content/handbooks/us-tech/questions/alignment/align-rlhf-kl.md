---
id: align-rlhf-kl
section: alignment
order: 1
level: S
title: 对齐：RLHF 为什么加 reverse KL 到 SFT 模型，正向 KL 会怎样
quick: >-
  PPO 式 RLHF 减的是 $\beta D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，期望在当前策略上取。它罚的是
  「SFT 几乎不说、RM 却给高分」的句子，并允许忘掉 SFT 里的有害峰。换成正向
  $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$ 会逼模型继续覆盖 SFT 的每个峰，对齐要的收窄被抵消。
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

OpenAI / Anthropic 对齐岗把 InstructGPT 当默认背景，不一定点名「reverse KL」。我会先说惩罚落在哪一种偏离，再写公式左右哪边是 $\pi_\theta$。方向写反，后面 DPO 换元和 PPO 监控全拧。工程拆分（ref KL 对 $\pi_{\mathrm{ref}}$，clip 对 $\pi_{\mathrm{old}}$）见 `openai-instructgpt-kl`。本题把正向 / 反向说清楚。

## 反向 KL：罚的是你现在会说的话

InstructGPT 的 RL 目标可以写成

$$
\max_\theta\ \mathbb{E}_{x,\,y\sim\pi_\theta}\big[r_\phi(x,y)\big]-\beta\,D_{\mathrm{KL}}\big(\pi_\theta(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

展开就是奖励里减 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。期望在 **当前策略** 上取：$\pi_\theta$ 跑到 $\pi_{\mathrm{ref}}\approx 0$ 的地方，$\log$ 比爆炸。这正是防胡话和 reward hacking 的护栏。$\pi_{\mathrm{ref}}$ 有、$\pi_\theta$ 不去的峰几乎不进期望，所以 **允许遗忘**。SFT 里残留的毒性、套话、过度承诺，可以对齐掉。这是 mode-seeking，不是实现 bug。

$\pi_{\mathrm{ref}}$ 通常冻 SFT，不要冻 base：用 base 当锚会把指令格式本身当偏离来罚，SFT 白做。锚太强（已经对齐过的模型）会把探索空间压没。

PPO clip 相对的是本批 $\pi_{\mathrm{old}}$，管单步别跳太猛。ref KL 管整段训练别离开可用语言。两个系数、两个参照。把 ref KL 和 PPO clip 说成一回事会掉分。

## 正向 KL 会怎样

若改成 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$，期望改到 $\pi_{\mathrm{ref}}$ 上。参考在某处概率为正，策略在该处接近 0 就会被重罚。于是 $\pi_\theta$ **必须继续覆盖 SFT 的每一个高概率模式**，包括我们想丢掉的有害峰。对齐要的是收窄：抬有用、无害的峰，丢掉毒性、拍马、拒答失败。正向 KL 把「丢掉」变成违法。

采样也对不上。PPO 从 $\pi_\theta$ 做 rollout，反向 KL 的蒙特卡洛是零额外采样。正向要从 $\pi_{\mathrm{ref}}$ 再抽一条，管道多一路参考生成，和 on-policy 循环不合。硬换成交叉熵更糟：$H(\pi_{\mathrm{ref}},\pi_\theta)=H(\pi_{\mathrm{ref}})+D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$，那是正向 KL 加一项与 $\pi_\theta$ 无关的熵。

白板用两个峰：参考在「有用回答」和「SFT 里见过的有害回答」都有质量。对齐希望只留有用峰。反向 KL 允许不覆盖有害峰；正向 KL 会因为漏掉有害峰被罚，策略只好继续生成它们。

## SFT 本身是正向的，别混

SFT / MLE 最小化 $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，mode-covering：示范里出现过的写法都得给质量。RLHF 的惩罚项是反向的。两阶段方向不同，不能说「对齐都在做 KL」。先 covering 铺技能，再 seeking 按奖励收窄。

监控四条：相对 old 的 KL、相对 ref 的 KL、reward、平均长度。长度和 reward 一起飙、ref KL 也飙，优先怀疑 hacking，见 `align-reward-hack`。KL 大不一定是坏事：参考很少拒答、对齐成功学会拒答，KL 也会升，要对着安全评测一起读。

DPO 从带这个反向 KL 的目标出发，最优策略 $\pi_\theta\propto\pi_{\mathrm{ref}}\exp(r/\beta)$。方向写反，隐式奖励换元对不上，见 `align-dpo`。

Token 级实现只在 response mask 上平均 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$。把 prompt 算进 KL，会把「读懂问题」当偏离来罚。

## 追问

- **为什么不是 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$？** 那个强迫覆盖 ref 全程质量，有害峰丢不掉，探索更死。RLHF 要的是「你现在会说的话别太离谱」，所以 $\pi_\theta$ 在前。
- **$\beta$ 太小 / 太大？** 太小：长度膨胀、套话、RM 分涨、人工一看在刷分。太大：KL 预算几步花完，reward 不动，等于没做 RL。
- **和 PPO clip 重复吗？** 不重复。Clip 限单步；ref KL 限长期漂。只 clip 不设 ref，短训可以，长训容易离开可用语言。
- **Reference 用 SFT 还是 base？** 常用 SFT。用 base 会把格式当偏离罚掉。
