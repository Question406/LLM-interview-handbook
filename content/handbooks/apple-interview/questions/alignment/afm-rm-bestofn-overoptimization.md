---
id: afm-rm-bestofn-overoptimization
section: alignment
order: 105
level: A
title: Best-of-N 越大越差：怎么画出 reward overoptimization 的证据？
quick: 我会先暂停扩大 N，检查那些高分失败答案。模型可能找到了评审器喜欢、但对任务没有帮助的写法。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: 'https://arxiv.org/abs/2210.10760'
    type: primary
---

## 面试官可能这样问

N 越大，RM 分越高，任务成功率却下降，你怎么办？

## 可以这样回答

我会先暂停继续扩大 N，拿被 RM 选中的失败答案来看。比如 agent 根本没完成工具操作，却写了一段非常完整的成功说明，RM 反而给了高分。这种情况下，增加 sampling 次数可能只是在增加找到这种答案的机会。

不过我会先确认比较条件一样：是不是同一批任务、同一个生成模型、相同的执行环境。确认以后，再补这类高分错例，或者限制目前的 sampling 规模。改完还得用独立任务结果检查，不能因为新 RM 给自己的分数好看，就认为问题解决了。

## 技术备查

## 场景与问题
N=1/4/16/64 时 RM 分持续上涨，隐藏工具测试成功率为 65/74/70/58%。请设计下一轮实验与停止规则，数字为虚构练习数据。

## 参考答案
同一 prompt 预生成 64 条固定 seed 候选，用嵌套候选子集比较各 N，控制生成器、温度与长度上限。冻结独立 executor 和人工抽查，记录高分失败类型及 confidence interval。这里应暂停扩大 N，优先查输出是否伪造工具成功或靠套话取高分。

overoptimization 研究在合成 gold RM 设定中展示了代理优化与真实目标的分离；不能把其中拟合曲线当作当前系统定律。本题建议是原创实验设计：加入对抗负例、限制候选分布、calibration 或更新 RM 后重新评价，不能只把 RM 分除以长度来宣告解决。

## 追问
**KL penalty 保证不会 hack 吗？** 不保证，它限制偏离程度，但漏洞可能就在原策略附近。
**停止阈值怎么定？** 预先约定任务质量、关键错误上限与成本，按独立 development set 选 N，最终盲测只验收。

