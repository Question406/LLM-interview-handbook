---
id: anthropic-pref-bt
section: anthropic
order: 12
level: S
title: Anthropic：Bradley-Terry 偏好模型，平局和噪声标签怎么处理？
quick: >-
  PM 把对比变成分数差的 logistic：$P(y_w \succ y_l)=\sigma(r_w-r_l)$。平局不要硬掰成胜负：丢掉、标
  0.5，或用带平局参数的 Davidson。噪声按标注一致率建模，别把红队分歧当成黄金标签。
tags:
  - Anthropic
  - Preference model
  - Bradley-Terry
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
---

Anthropic 的 HH-RLHF 和 CAI 都把人类或 AI 的对比蒸馏进 preference model，再拿 $r_\phi$ 当 强化学习（RL） 奖励。面试会把 PM 从「一个打分器」问到损失、平局、噪声。我会从 Bradley-Terry 写起。

## 从对比到分数

一条样本是 输入提示（prompt） $x$ 和两条回答 $y_i,y_j$，标注 $y_i \succ y_j$。BT 假设每条回答有标量强度，人看到的是强度差上的 Bernoulli：

$$
P(y_i \succ y_j \mid x)=\sigma\bigl(r_\phi(x,y_i)-r_\phi(x,y_j)\bigr),
$$

其中 $\sigma(z)=(1+e^{-z})^{-1}$。训练损失是负对数似然：

$$
\mathcal{L}=-\log\sigma\bigl(r_\phi(x,y_w)-r_\phi(x,y_l)\bigr).
$$

$r_\phi$ 通常是从 监督微调（SFT） 初始化的 LM，在最后一个 token 上接线性头，或对 hidden 做池化。绝对分值没有校准意义，只有差进入概率。RL 时要对 $r$ 做 running mean/std 归一，否则 PPO 单步更新可能不稳定。

这和分类「这条好/坏」不同：没有绝对阈值，只有配对。单条 Elo 能排模型，不能当二元分类准确率报。

## 平局

标注员经常说「差不多」。三种处理，我会按数据量选：

1. 丢掉。最干净，浪费样本。对比很贵时不优先。
2. 软标签 0.5。损失变成 $0.5\,\mathrm{BCE}(p)+0.5\,\mathrm{BCE}(1-p)$，把差往 0 推。实现简单，等于教模型「这两条别分太开」。
3. Davidson / Rao-Kupper。显式平局概率，多一个 $\nu>0$：

$$
P(\mathrm{tie})=\frac{\nu\sqrt{\pi_i\pi_j}}{\pi_i+\pi_j+\nu\sqrt{\pi_i\pi_j}},\quad \pi_i=e^{r_i}.
$$

$\nu$ 大则更容易判平。HH 数据里 harmless 对更常平（两条都在拒），helpful 对更少。我会把 $\nu$ 当超参，或按任务分开。

不要把平局随机派成胜负。那是往梯度里加对称噪声，PM 在难分区域会抖。更糟的是产品经理说「必须选出一条」然后按展示顺序点左边，那是位置偏差，不是偏好。

CAI 的 AI 评委也要允许「无法决定」。逼评委二选一，条款没覆盖的样本会变成高置信噪声。

## 噪声标签

人标 harmless 的一致率明显低于摘要偏好。设真实偏好以 $\varepsilon$ 翻转：

$$
P_{\mathrm{obs}}(i\succ j)=(1-\varepsilon)P_{\mathrm{true}}(i\succ j)+\varepsilon P_{\mathrm{true}}(j\succ i).
$$

$\varepsilon$ 可用重复标注估计。损失可以写成噪声感知的 logistic，或用 Huber / 对高 loss 样本降权（类似 generalized BT）。实践里更有效的是：

- 重复标一小部分，报 agreement，当数据质量仪表盘；
- 丢掉「标得很快、永远点第一条」的标注员；
- 同一输入提示 多对对比，看循环竞赛（A>B>C>A），有环说明噪声或非传递，BT 假设破了。

非传递不一定是噪声：人可能用多轴（有用 vs 无害）在不同对上切。这正好接 `anthropic-hh-rlhf`：一个标量 $r$ 无法同时最大两轴。多目标或约束优于把打架的对硬塞进同一个 BT。

AI 反馈的噪声是另一种：评委对位置敏感、对长度敏感。扫 $y_1,y_2$ 左右对调，胜率不对称就要在输入里随机交换，损失按交换后的标签算。

## 追问

- **和 Elo / TrueSkill 什么关系？** BT 是 Elo 的静态版。Elo 有时间序和更新步；训练 PM 是批量 MLE。面试说「PM 分数当 Elo」可以，但别把在线 Elo 更新和梯度下降混成一个公式。
- **直接偏好优化（DPO） 还要不要 PM？** DPO 把 BT + 最优策略代进损失，跳过显式 $r_\phi$。平局和噪声问题还在，只是落到政策损失上。
- **长度偏差？** 人偏爱长回答，$r$ 会涨在长度上。控制：在 $r$ 里减长度惩罚，或配对时长度分层。RL 阶段长度膨胀往往是 PM 在刷这个捷径。
- **一对多对比怎么进 BT？** 选一个 winner 对其余所有 loser 建边，或 Plackett-Luce 对完整排序建模。数据少时 pairwise BT 更稳。

## 相关题

- [[anthropic-pref-collect]]：讲采集协议怎样产生平局和分歧；这张卡讲采回来之后 BT 模型怎么处理它们。
- [[anthropic-hh-rlhf]]：helpful 和 harmless 冲突时偏好怎么采、怎么混训，是 BT 打分之前的数据问题。
- [[xai-lmarena]]：Arena 现在也用 Bradley-Terry 全局 MLE 出分，是同一个模型用在在线评测上。
- [[align-arena]]：对齐岗问法的 Arena 题，讲 BT / ELO 估出来的分数受哪些选择偏差和文风影响。
