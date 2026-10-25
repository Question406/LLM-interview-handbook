---
id: msft-orpo
section: microsoft
order: 4
level: A
title: Microsoft：ORPO 相对 DPO/PPO，少了参考模型意味着什么
quick: "ORPO 在单模型、单阶段中结合 chosen 的 SFT NLL 与 odds ratio 偏好损失，不加载冻结参考模型，也不另训奖励模型。节省权重与前向的同时，失去了显式 KL 锚，需要监控 chosen / rejected 概率、长度、熵和语言回归。"
tags:
  - Microsoft
  - ORPO
  - DPO
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ORPO — Monolithic Preference Optimization without Reference Model
    url: https://arxiv.org/abs/2403.07691
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

ORPO 把 SFT 和偏好学习合在一次更新里，省去冻结参考模型与独立奖励模型，但也不再有参考策略的显式 KL 锚。比如 7B bf16 的参考权重约多占 14GB，显存紧的小模型训练省下一份很有价值，语言行为是否漂移则要靠回归评测检查。

论文来自 KAIST 的 Hong 等，实验包含 Phi-2，不能称作微软论文。它可作为 Azure / 开源小模型的一阶段基线，与 `msft-phi-slm` 的部署约束相关。PPO + KL 背景见 `openai-instructgpt-kl`。

## 对照三种损失与模型数量

PPO 式 RLHF 通常有策略、冻结参考、奖励模型和 critic，除了这些前向还要采样 rollout。其奖励可写为：

$$
r(x,y)=r_{\phi}(x,y)-\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

KL 用于限制策略偏离参考语言行为，也降低钻 RM 空子的程度，代价是显存、吞吐和 RM 偏差。

DPO 消去显式 RM，损失依赖 $(\pi_\theta,\pi_{\mathrm{ref}})$：

$$
\mathcal{L}_{\mathrm{DPO}}=-\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big).
$$

它仍需冻结 $\pi_{\mathrm{ref}}$，通常是 SFT checkpoint。ZeRO 能分片状态，但额外参考前向仍存在。

ORPO 直接用 $(x,y_w,y_l)$ 数据进行单阶段、单模型优化：

$$
\mathcal{L}=\mathbb{E}\big[\mathcal{L}_{\mathrm{SFT}}(x,y_w)+\lambda\mathcal{L}_{\mathrm{OR}}\big],
$$

$$
\mathrm{odds}_\theta(y\mid x)=\frac{P_\theta(y\mid x)}{1-P_\theta(y\mid x)},\qquad
\mathcal{L}_{\mathrm{OR}}=-\log\sigma\Big(\log\frac{\mathrm{odds}_\theta(y_w\mid x)}{\mathrm{odds}_\theta(y_l\mid x)}\Big).
$$

$\mathcal{L}_{\mathrm{SFT}}$ 提高 chosen 似然，odds ratio 拉开 chosen 与 rejected。没有 $\pi_{\mathrm{ref}}$，也没有另一个 RM。

## 省下参考后，怎样保持稳定

Phi-2 的 $2.7\mathrm{B}$ 单机偏好训练可少存一份权重、少一次前向，也减少 tokenizer/checkpoint 对齐的工程负担。论文称 monolithic，表示 SFT 和偏好不必拆成两个 job。

DPO 的 $\beta$ 来自参考 KL 下的隐式奖励推导，ORPO 则依赖 NLL 对 $y_w$ 的正向约束，对 $y_l$ 的惩罚来自 odds ratio。$\lambda$ 太小会接近 SFT，偏好信号不足；太大可能过分压低 $P(y_l)$，导致乱码、拒答和长度塌缩。不能把它简单当成参考为均匀分布的 DPO，也不能只改 $\beta$ 套推导。

训练中看 chosen / rejected 平均 logprob、差距、熵、长度，以及 SFT 风格的指令遵循回归集。数据仍需 $(y_w,y_l)$，减少的是模型开销，并未消除成对偏好标注。

已有高质量 SFT、需要稳定 KL 锚或偏好较噪时可选 DPO；要在线探索、奖励来自环境或分类器时仍考虑 PPO / REINFORCE。ORPO 适合已有偏好对、希望小模型一次训完且显存受限的任务。语言明显退化时，可以退回 DPO 并检查小 $\beta$ 等设置，而非盲目增大 $\lambda$。

## 追问

**ORPO 的 SFT 项也是参考 KL 吗？**
不是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，它只直接监督 chosen 的似然。

**能先 SFT 再 ORPO 吗？**
能。论文强调不必 warm-up；已有 SFT 时也可直接用现成参考做 DPO。

**不使用 RM 就不会 reward hacking 吗？**
仍可能学成对标注里的长度、客气等捷径，PPO 则可能利用 RM 偏差，都要对抗评测。

**$P_\theta(y\mid x)$ 如何计算？**
从序列 token logprob 之和再做归一，长度差大时使用 length-normalize，避免 odds 被长度主导。

相关：[[align-dpo]]、[[openai-dpo-loss]]、[[align-ipo]]、[[align-kto]]、[[align-length-bias]]
