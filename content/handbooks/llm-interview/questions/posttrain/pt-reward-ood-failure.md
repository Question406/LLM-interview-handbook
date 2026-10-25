---
id: pt-reward-ood-failure
section: posttrain
order: 40
level: S
title: Reward 在 OOD 上如何失效，训练时怎么发现并兜底？
quick: "RM 和规则奖励只在训练分布附近可靠，策略一旦把输出推到标注没覆盖的地方，打分会错排甚至反向，还会奖励看起来像好答案的幻觉。训练时盯 proxy 与 gold 的相关性、分布漂移和高分样本审计，发现后对可疑轨迹降权或拒训、换更严的可执行奖励；加大 KL 只能推迟。"
tags:
  - Reward Model
  - OOD
  - Overoptimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
---

Reward 在 OOD 上失效，指策略生成的 $(x,y)$ 已经跑出偏好数据或规则覆盖的范围，比如新题型、更长的分步推理（CoT）、新的工具轨迹或对抗风格，这时 $\hat{r}(x,y)$ 的排序和人类或可执行 oracle 脱钩，甚至会奖励「看起来像好答案」的幻觉。策略在优化过程中自己就在把分布往外推，所以这是一种持续发生的 OOD。

为什么会这样。奖励模型（RM）拟合的是标注支撑上的代理效用。Gao et al. 的 overoptimization 曲线显示，对 proxy RM 优化越狠，gold RM 或人类分先升后降，OOD 就是这条曲线背后的机制：标注范围之外，代理评分未必反映真实质量。规则奖励在代码、数学上更稳，但 checker 也有覆盖不到的地方，格式对语义错、终局对步骤假都可能拿高分；学出来的 RM 更怕风格漂移，回答更长、更客套、项目符号更多都可能骗到它。

举个例子，数学强化学习（RL）里模型写「伪步骤加正确最终答案」，松校验和 RM 都给高分，换成逐步 verifier 或者竞赛新题，分数就崩了。这就是 OOD 下的表面成功。

怎么发现，我会看三样东西。一是 proxy 和 gold 的相关性：在 held-out 域切片上算 Spearman 或准确率，按长度、工具调用次数、题型切开看，相关性掉下来比「训练 reward 还在涨」更早报警。二是漂移仪表盘：embedding 距离、长度、n-gram 新颖性、expert / tool 直方图。输出突然变长而 gold 不动，先怀疑 hacking，别当成能力提升。三是高分审计：每个 bucket 抽高 $\hat{r}$ 的样本给人或更严格的验证器看，OOD 失效很多时候就表现为高分幻觉。

兜底的做法是对高不确定或被标成 OOD 的轨迹 clip 优势、拒训、回放到 SFT 数据分布，或者换更严的可执行奖励。发现失效后先归因，看是数据、奖励定义还是 KL 太松，再决定回滚、加金标还是改奖励。KL 预算只是推迟崩点，它既检测不了失效，也治不了错分。

## 追问

**这和模型钻奖励规则的空子有什么区别？**
hacking 是策略找到了 proxy 的捷径，OOD 失效是 proxy 在支撑外不再校准。两者常常一起出现。

**规则奖励就免疫吗？**
只对标注风格漂移免疫，checker 的盲区照样会被利用。

**gold 从哪来？**
小而稳的人类标注，或者更强的独立 verifier。别用正在被优化的同一个 RM。
