---
id: align-reward-model
section: alignment
order: 12
level: S
title: 对齐：奖励模型怎么训、校准、Bradley-Terry 噪声
quick: "RM 用同一道题的优劣回答对训练，Bradley-Terry 损失让优选回答的分数更高。这个分数主要表达同题内的相对排序，绝对值不能直接跨题比较；还要单独检查概率校准、RL 奖励尺度和标注噪声。"
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

奖励模型（RM）从同一道题的回答对里学人类偏好，再用 $r_\phi$ 为强化学习（RL）或答案筛选提供信号。比如同题两条回答，一条更准确、一条更冗长，如果标注员总选更长的，RM 就可能把长度当质量。InstructGPT 和 Anthropic HH 都采用了偏好建模；训练后还要分别检查排序、尺度和标签噪声。

## 怎么训练和检查分数

数据是 $(x,y_w,y_l)$，同一输入提示 下的对比。$r_\phi$ 通常从 监督微调（SFT） 初始化，对 response 做池化或在最后一个 token 的表示上接线性头。偏好概率是 $P(y_w\succ y_l)=\sigma(r_w-r_l)$，用 $r$ 的差表达哪条更好。损失是 BT 负对数似然

$$
\mathcal{L}=-\mathbb{E}\big[\log\sigma\big(r_\phi(x,y_w)-r_\phi(x,y_l)\big)\big].
$$

这个概率只由两条回答的分差决定。给同题所有回答同时加一个数，不会改变偏好概率，所以「这条 4.2 分」没有独立的绝对含义。这也关系到 DPO 的隐式奖励。Helpful 和 harmless 最好分开，避免拒答和套话靠一个混合标量获胜。

实现时只在 response 上取表示，两条回答共享输入提示（prompt）编码，避免读题差异影响比较；同时打乱 $y_w/y_l$ 左右顺序。验证除了 loss，还要报 pairwise accuracy，以及按分差分层的准确率。

```python
def bt_loss(r_w, r_l):
    return -torch.nn.functional.logsigmoid(r_w - r_l).mean()
```

Margin 很大的 pair 梯度已经饱和，信息在「难分」的近邻对。全是悬殊对比，RM 表面 acc 很高，RL 时遇到接近决策边界的回答就容易误判。

BT 给出对比概率，接入 RL 前还要分开检查三件事：

1. **排序。** 同一 $x$ 下 $r$ 的次序对不对。这是 RM 的本职。
2. **概率校准。** $\sigma(r_w-r_l)$ 是否接近人标频率。可以画 reliability；温度缩放只改差的尺度，不创造绝对零点。
3. **RL 尺度。** PPO 要的是稳定优势。即使排序很好，裸 $r$ 的均值和方差会漂。训练时对 batch 或 running 做标准化，是优化需要，不是「校准到人类」。

ECE 低也不能排除 hacking。Gao 的过优化现象关注 proxy 与 gold 是否分叉，概率校准良好时仍可能发生。BoN 用 RM 选答案，还会放大尺度和长度的影响。

绝对分拿去跨 prompt 比「哪句更好」是错的：不同 $x$ 的 $r$ 原点不同。跨模型比 RM 分更错，除非同一 RM、同一预处理。

## 标注噪声怎么进入训练

人类偏好会有以下几类噪声：

- **不一致。** 同一对再标会翻。噪声率 20% 时，BT 仍可学到方向，但间隔被压扁，RL 步长难调。
- **平局硬掰。** 把「差不多」随机指定胜负，等于注入对称噪声。丢掉、标 0.5、或 Davidson 带平局参数，见 `anthropic-pref-bt`。
- **长度和排版。** 更长、使用更多 Markdown 排版的回答更容易获得偏好，RM 把偏见写进 $r$，见 `align-length-bias`。
- **红队分歧。** 安全 pair 上专家不同意是信号，不是该平均掉的 label noise。分开切片训或分开头。

缓解：多标注聚合、按一致率加权、ensemble RM（换种子或换家族）、定期用 held-out 人和第二 RM 看分叉。发现训练 RM 升、gold 降，先冻结策略、查明原因，再重新标注难以区分的回答对，不要加大学习率。

同样的噪声偏好用于 DPO，也不会自动变干净，隐式奖励仍会继承数据中的偏差。

相关：`anthropic-pref-bt`、`align-dpo`、`align-over-refuse`、`align-reward-hack`、`align-best-of-n`。

## 追问

**为什么不用 MSE 回归五分制？**
五分制标注员尺度漂；BT 只要求配对次序，和 基于人类反馈的强化学习（RLHF） 目标一致。
**pairwise acc 90% 能发吗？**
悬殊对拉高数字。要看难对、切片（安全、长回答、多语言）和 gold 分叉。
**两个 RM 分歧听谁？**
当发现 hacking 的探测器，不要当新的训练损失平均掉。验收换家族。
**RM 要不要和策略同步更新？**
在线可以，但旧偏好对可能不再代表当前策略生成的回答分布。离线 RM 过时一样会 hack，见 `align-online-dpo`。

## 相关题

- [[align-overopt-rm]]：RM 训好之后被策略一路优化会发生什么，那张讲 proxy 和 gold 的分叉曲线。
- [[align-reward-hack]]：这里说长度偏好会写进 $r$，那张讲策略怎么利用它、训练中怎么发现。
- [[align-best-of-n]]：RM 在推理时的用法，用它从 $N$ 条里挑最高分，绝对分不可信的问题在那里同样存在。
- [[sys-left-pad]]：工程题，左填充时 RM 取「最后一个非 pad」可能打到 prompt 上，是 RM 打分位置的实现坑。
- [[openai-dpo-loss]]：DPO 同样基于 Bradley-Terry，但不训显式 RM，把奖励写成 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。
