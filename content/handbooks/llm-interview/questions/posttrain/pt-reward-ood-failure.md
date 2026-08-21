---
id: pt-reward-ood-failure
section: posttrain
order: 40
level: S
title: Reward 在 OOD 上如何失效，训练时怎么发现并兜底？
quick: >-
  RM/规则奖励只在训练分布附近可靠；策略一离开标注支撑，分数会错排甚至反向。
  要用分布漂移监控、OOD 探测与保守更新，避免把错误高分当成功信号。
tags:
  - Reward Model
  - OOD
  - Overoptimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
---

奖励失效的典型形态：策略生成的 $(x,y)$ 相对偏好 / 规则训练集是 OOD——新题型、更长 CoT、新工具轨迹、对抗风格——此时 $\hat{r}(x,y)$ 的排序与人类或可执行 oracle 脱钩，甚至奖励「看起来像好答案」的幻觉。Policy 自己把分布推开，就是一种持续的 OOD。

## 为什么会失效

RM 拟合的是标注支撑上的代理效用。Gao et al. 的 overoptimization 曲线：对 proxy RM 优化越狠，gold RM / 人类分先升后降。OOD 是这条曲线的机制版：proxy 在支撑外没有因果意义，KL 预算只是推迟崩点，不是检测手段。

规则奖励在代码 / 数学更稳，但仍有 checker 覆盖不到的盲区（格式对、语义错；终局对、步骤假）。学得的 RM 更怕风格漂移：更长、更客套、更多项目符号。

## 怎么发现

- **Proxy–gold 相关**：held-out 域切片上 Spearman / 准确率，按长度、工具调用次数、题型切。相关掉了比「训练 reward 还在涨」更早。
- **漂移仪表盘**：embedding 距离、长度、n-gram 新颖性、expert/tool 直方图。突然变长且 gold 不动，优先怀疑 hacking 而不是能力。
- **高分审计**：每个 bucket 抽高 $\hat{r}$ 样本给人 / 更严 verifier。OOD 失效经常表现为「高分幻觉」。

## 兜底

高不确定或 OOD 标记的轨迹：clip 优势、拒训、回放到 SFT 分布、或换更严的可执行奖励。发现失效后先归因（数据、奖励定义、KL 过松），再决定回滚 / 加金标 / 改奖励。不要只加大 KL 硬冲。

## 例子

数学 RL 里模型写「伪步骤 + 正确最终答案」，松校验和 RM 都给高分；换逐步 verifier 或竞赛新题后分数崩。这是 OOD 下的表面成功。

## 追问

- **和 reward hacking 的差别？** Hacking 是策略找到 proxy 的捷径；OOD 失效是 proxy 在支撑外不再校准。二者常一起出现。
- **规则奖励就免疫吗？** 只免疫标注风格漂移，不免疫 checker 盲区。
- **Gold 从哪来？** 小而稳的人类 / 更强独立 verifier，不要用正在被优化的同一 RM。
