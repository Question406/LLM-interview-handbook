---
id: msft-orpo
section: microsoft
order: 4
level: A
title: Microsoft：ORPO 相对 DPO/PPO，少了参考模型意味着什么
quick: "ORPO 把 监督微调（SFT） 的 NLL 和一项 odds ratio 偏好损失写进同一次更新，不加载冻结的 $\\pi_{\\mathrm{ref}}$，也不另训 奖励模型（RM）。省的是显存和一个独立训练阶段；丢掉的是 KL 锚。小模型（Phi 级）很划算，长训要盯 rejected 概率和语言崩坏。"
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

对齐岗对照 PPO / 直接偏好优化（DPO） 时，ORPO 是「能不能少加载一个模型」的标准追问。论文是 KAIST 的 Hong 等人，不是微软发的；但实验里用了 Phi-2，Azure / 开源栈也把它当一阶段对齐基线。微软面试里它常和 `msft-phi-slm` 绑在一起：小模型显存紧，参考模型的一份 bf16 副本很贵。InstructGPT 式 PPO+KL 见 `openai-instructgpt-kl`。

## 三套配方，先数模型数

PPO 式 基于人类反馈的强化学习（RLHF）：策略、冻结参考、奖励模型，常常再加 价值评估模型（critic）。四份前向，采样轨迹（rollout） 还要采样。奖励是

$$
r(x,y)=r_{\phi}(x,y)-\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

参考模型的 KL 约束帮助保留语言行为，并限制钻奖励规则空子的程度。代价是显存、吞吐、以及 RM 自己的偏差。

DPO 把 RM+KL 解析掉，loss 只在 $(\pi_\theta,\pi_{\mathrm{ref}})$ 上：

$$
\mathcal{L}_{\mathrm{DPO}}=-\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big).
$$

仍要一份冻结 $\pi_{\mathrm{ref}}$，通常是 监督微调（SFT） 权重。7B bf16 就是多 14GB，ZeRO 分片也消不掉「多一份前向」。

ORPO 的设定是 **单阶段、单模型**。数据是 $(x,y_w,y_l)$，不必先单独 SFT 再开第二阶段。损失是

$$
\mathcal{L}=\mathbb{E}\big[\mathcal{L}_{\mathrm{SFT}}(x,y_w)+\lambda\mathcal{L}_{\mathrm{OR}}\big],
$$

$$
\mathrm{odds}_\theta(y\mid x)=\frac{P_\theta(y\mid x)}{1-P_\theta(y\mid x)},\qquad
\mathcal{L}_{\mathrm{OR}}=-\log\sigma\Big(\log\frac{\mathrm{odds}_\theta(y_w\mid x)}{\mathrm{odds}_\theta(y_l\mid x)}\Big).
$$

$\mathcal{L}_{\mathrm{SFT}}$ 把 chosen 的似然拉上去，odds ratio 让 chosen 相对 rejected 的胜率变大。没有 $\pi_{\mathrm{ref}}$，也没有单独的 RM。

## 「少了参考模型」到底少了什么

显存和工程：少一次前向、少一份权重、少一套和策略对不齐的 tokenizer/checkpoint。Phi-2 这种 $2.7\mathrm{B}$ 在单机上可以对偏好数据直接训，不必为了 DPO 再塞一个同尺寸冻结模型。论文把这叫做 monolithic：SFT 和偏好不是两段 job。

理论：DPO 的 $\beta$ 来自「奖励 = 隐式 log 比 + 参考策略的 KL」。ORPO 没有这条 KL。约束 chosen 不飞出预训练语言的，是 NLL 本身：它只在 $y_w$ 上提供正信号，对 $y_l$ 的惩罚来自 odds ratio，而不是「相对 SFT 的 token KL」。所以：

- $\lambda$ 太小：几乎就是 SFT，偏好学不够，rejected 风格还在。
- $\lambda$ 太大：模型为了压 $P(y_l)$ 把大量 token 的概率压低，出现乱码、拒答、长度塌缩。没有 $\pi_{\mathrm{ref}}$ 给你一条 KL 曲线当刹车。

我会监控：chosen / rejected 的平均 logprob、两者差距、熵、长度、以及一块 SFT 风格的回归集（指令遵循有没有掉）。DPO 至少还能看相对 ref 的 KL；ORPO 要把回归集当成替代锚。

常见误区是：把 ORPO 说成「DPO 把 ref 设成均匀分布」。odds 和 DPO 的 log 比不是同一个推导，别在白板上直接改动 $\beta$ 来套用推导。另一常见误区是：说 ORPO 完全不需要偏好数据。它仍要 $(y_w,y_l)$，只是不需要第三份模型。

## 什么时候仍选 DPO / PPO

要强 KL 锚、要和已有 SFT checkpoint 对齐、或者偏好数据很噪：DPO 更稳，ref 就是那份 SFT。要在线探索、奖励是环境或分类器而不是成对文本：仍是 PPO / REINFORCE 一类。ORPO 适合「已经有成对数据、想在小模型上一次训完、显存是硬约束」。Azure 上对 Phi 做领域对齐，我会先 ORPO 打底，再抽查；若语言生成能力明显下降，退回 DPO 加小 $\beta$，而不是把 $\lambda$ 盲目加大。

## 追问

- **没有 ref，还算 KL 正则吗？** 不算 DPO 那种 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$。SFT 项是对 chosen 的前向似然，不是对整份参考策略的反向 KL。
- **能先 SFT 再 ORPO 吗？** 能，但论文卖点是不必 warm-up。已有高质量 SFT 时，直接 DPO 往往更省事，因为 ref 现成。
- **和 PPO 比谁更不容易 hacking？** PPO 有 RM，hacking 的是 RM；ORPO hacking 的是成对标注里的捷径（更长、更客气）。都要离线对抗集，不是换个字母就免疫。
- **实现上 $P_\theta(y\mid x)$ 怎么估？** 序列级用 token logprob 之和再归一；长度差大时要 length-normalize，否则 odds 被长回答主导。

## 相关题

- [[align-dpo]]：标准 DPO 的隐式奖励和 $\beta$，ORPO 拿掉的 KL 锚就在这里。
- [[openai-dpo-loss]]：DPO 相对 PPO 少了什么；和这张卡连起来，能把 PPO、DPO、ORPO 三套配方的模型数量讲清楚。
- [[align-ipo]]：IPO 仍保留参考模型，只改损失形状，和 ORPO 去掉参考模型是两条不同的改法。
- [[align-kto]]：KTO 省掉的是成对标注，ORPO 省掉的是参考模型。
- [[align-length-bias]]：ORPO 的序列概率要做长度归一，那张卡讲长度偏见在整条偏好管道里从哪进来。
