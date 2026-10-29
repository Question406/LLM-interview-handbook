---
id: dt-stale-rollout-incident
section: panel
order: 42
level: A
title: Panel 情景：异步 rollout throughput 翻倍，为什么训练奖励上涨但任务成功下降？
quick: >-
  假设生成服务还在用版本 10，而训练已经到了版本 15。这些回答来自旧策略，不能因为刚刚送到 trainer 就称它们是当前策略的 on-policy
  数据。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 情景练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

## 题目描述

原创情景，建议 35 分钟。你将 sampling 与训练拆成异步服务，rollout throughput 翻倍。训练奖励持续上升，冻结任务成功率却下降。部分 trajectories 来自 20 个版本前的策略，reward model 和工具 schema 最近也更新过。

请设计调查与恢复方案，写出每条 trajectories 必须带哪些元信息，解释何时应丢弃旧数据、重算奖励或限制消费速度。

## 回答思路

> **问题与场景：** 假设生成服务还在用版本 10，而训练已经到了版本 15。
>
> **做法与原因：** 我会给每条 rollout 记录生成权重版本、时间和行为 log-probability，并限制训练可接受的滞后。
>
> **检查与取舍：** throughput 之外，还要看滞后分布、ratio、有效样本和独立成功率。

## 可以这样回答

假设生成服务还在用版本 10，而训练已经到了版本 15。这些回答来自旧策略，不能因为刚刚送到 trainer 就称它们是当前策略的 on-policy 数据。

我会给每条 rollout 记录生成权重版本、时间和行为 log-probability，并限制训练可接受的滞后。Importance correction 可以处理某些分布差异，但策略相差太大时会很不稳定。

throughput 之外，还要看滞后分布、ratio、有效样本和独立成功率。若奖励涨而任务变差，需要检查陈旧数据与评分偏差，而不是只继续加生成并发。

## 技术备查

## 解题思路与参考答案

不要把所有变化归结为 off-policy。先核对当前展示的奖励是否混合不同版本的打分尺度；同一输出经两版奖励重评，能发现测量变化。工具 schema 或环境状态不一致也可能让旧 trajectories 不再有效，须在可重置环境复现。

### trajectories 至少记录什么

保存任务与环境快照版本、prompt 与工具 schema、行为策略 checkpoint、sampling 配置、动作 token 的行为 log probability、reward function/模型版本、生成和消费时间、终止原因。策略年龄既可按版本差，也可按实际分布差衡量；版本编号相近不保证行为接近。

### 有区分力的排查

先用同一冻结评价器重评不同年龄 trajectories，按任务、长度与环境版本匹配，比较通过率和错误类型。限制队列最大年龄，或固定同一策略生成小批新 trajectories，与旧队列在相同更新预算下对照。若仅奖励版本变化，可重算一致奖励；若动作依赖已失效的 observation 或权限，重打分不能修复 trajectories。

### 恢复决策

暂缓扩大异步队列，先限制陈旧程度和消费速率，保留坏版本 checkpoint 与证据。只有算法支持且行为概率完整时才讨论重要性加权，并监控权重方差与裁剪偏差。无法恢复行为概率时不能声称做了精确修正；对严重环境漂移应 resampling。

## 面试追问

**旧数据全部扔掉最安全吗？** 可能浪费仍有价值的覆盖，也无法定位根因。按语义有效性、奖励一致性与策略差异分别处理，而不是只设一个时间阈值。

**throughput 提高为何不等于训练效率提高？** 有效独立任务和可信训练信号可能减少，需比较单位计算成本的独立评测收益，而非只比较 tokens/s。

**策略版本不记，只记 seed 能恢复吗？** 不足。模型权重、sampling 参数、环境和工具响应共同决定 trajectories。
