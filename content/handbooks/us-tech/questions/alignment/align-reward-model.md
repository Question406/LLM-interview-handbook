---
id: align-reward-model
section: alignment
order: 12
level: S
title: 对齐：奖励模型怎么训、校准、Bradley-Terry 噪声
quick: "RM 用成对偏好训 Bradley-Terry：$P(y_w\\succ y_l)=\\sigma(r_w-r_l)$，只有分差有意义，绝对分不可信。标签噪声、平局和长度偏好都会写进 $r$，被策略利用。"
tags:
  - Anthropic
  - OpenAI
  - Reward Model
  - Bradley-Terry
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
---

InstructGPT 和 Anthropic HH 都把人偏好蒸馏进奖励模型，再拿 $r_\phi$ 做 强化学习（RL）。对齐岗问 RM，不是「接个回归头」。要能写出 Bradley-Terry、说清绝对分不可信、以及噪声标签怎么把后续 PPO / 直接偏好优化（DPO） / BoN 一起带偏。公司章的平局处理见 `anthropic-pref-bt`；本题收训练、校准、噪声这三块。

## 怎么训：数据、结构、损失

数据是 $(x,y_w,y_l)$，同一输入提示 下的对比。$r_\phi$ 通常从 监督微调（SFT） 初始化，对 response 做池化或在最后一个 token 的表示上接线性头。损失是 BT 负对数似然

$$
\mathcal{L}=-\mathbb{E}\big[\log\sigma\big(r_\phi(x,y_w)-r_\phi(x,y_l)\big)\big].
$$

只有差进入概率。把 RM 当点式回归（「这条 4.2 分」）会引入一个 BT 里消掉的任意加性函数，和后面 DPO 的 隐式奖励 对不上，见 `align-dpo`。Helpful 和 harmless 不要塞进同一个标量，否则拒答和套话会赢，见 `align-over-refuse`。

实现要点：只在 response 上算表示；对比的两条必须共享 输入提示（prompt） 编码，否则模型用「读题质量」作弊；打乱 $y_w/y_l$ 左右顺序，防止模型依赖展示位置判断好坏。验证报 pairwise accuracy 和按间隔分层的准确率，不要只报 loss。

```python
def bt_loss(r_w, r_l):
    return -torch.nn.functional.logsigmoid(r_w - r_l).mean()
```

Margin 很大的 pair 梯度已经饱和，信息在「难分」的近邻对。全是悬殊对比，RM 表面 acc 很高，RL 时遇到接近决策边界的回答就容易误判。

## 校准：排序对了不等于能当奖励

BT 给出的是对比概率，不是校准过的绝对质量。三件事常被混：

1. **排序。** 同一 $x$ 下 $r$ 的次序对不对。这是 RM 的本职。
2. **概率校准。** $\sigma(r_w-r_l)$ 是否接近人标频率。可以画 reliability；温度缩放只改差的尺度，不创造绝对零点。
3. **RL 尺度。** PPO 要的是稳定优势。即使排序很好，裸 $r$ 的均值和方差会漂。训练时对 batch 或 running 做标准化，是优化需要，不是「校准到人类」。

面试别说「我们 ECE 很低所以不会 hack」。Gao 的 overoptimization 是 proxy 和 gold 分叉，校准指标可以一直很好，见 `align-reward-hack`。BoN 把 RM 当选模器时，尺度和长度会一起被放大，见 `align-best-of-n`。

绝对分拿去跨 prompt 比「哪句更好」是错的：不同 $x$ 的 $r$ 原点不同。跨模型比 RM 分更错，除非同一 RM、同一预处理。

## Bradley-Terry 噪声

人标不是干净的 Bernoulli。来源：

- **不一致。** 同一对再标会翻。噪声率 20% 时，BT 仍可学到方向，但间隔被压扁，RL 步长难调。
- **平局硬掰。** 把「差不多」随机指定胜负，等于注入对称噪声。丢掉、标 0.5、或 Davidson 带平局参数，见 `anthropic-pref-bt`。
- **长度和排版。** 更长、使用更多 Markdown 排版的回答更容易获得偏好，RM 把偏见写进 $r$，见 `align-length-bias`。
- **红队分歧。** 安全 pair 上专家不同意是信号，不是该平均掉的 label noise。分开切片训或分开头。

缓解：多标注聚合、按一致率加权、ensemble RM（换种子或换家族）、定期用 held-out 人和第二 RM 看分叉。发现训练 RM 升、gold 降，先冻结策略、查明原因，再重新标注难以区分的回答对，不要加大学习率。

噪声 RM 进 DPO 不会自动变干净：DPO 只是把这张 RM 解析进策略。数据脏，隐式奖励也脏。

## 追问

- **为什么不用 MSE 回归五分制？** 五分制标注员尺度漂；BT 只要求配对次序，和 基于人类反馈的强化学习（RLHF） 目标一致。
- **pairwise acc 90% 能发吗？** 悬殊对拉高数字。要看难对、切片（安全、长回答、多语言）和 gold 分叉。
- **两个 RM 分歧听谁？** 当发现 hacking 的探测器，不要当新的训练损失平均掉。验收换家族。
- **RM 要不要和策略同步更新？** 在线可以，但旧偏好对可能不再代表当前策略生成的回答分布。离线 RM 过时一样会 hack，见 `align-online-dpo`。

## 相关题

- [[align-overopt-rm]]：RM 训好之后被策略一路优化会发生什么，那张讲 proxy 和 gold 的分叉曲线。
- [[align-reward-hack]]：这里说长度偏好会写进 $r$，那张讲策略怎么利用它、训练中怎么发现。
- [[align-best-of-n]]：RM 在推理时的用法，用它从 $N$ 条里挑最高分，绝对分不可信的问题在那里同样存在。
- [[sys-left-pad]]：工程题，左填充时 RM 取「最后一个非 pad」可能打到 prompt 上，是 RM 打分位置的实现坑。
- [[openai-dpo-loss]]：DPO 同样基于 Bradley-Terry，但不训显式 RM，把奖励写成 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。
