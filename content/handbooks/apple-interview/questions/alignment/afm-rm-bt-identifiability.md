---
id: afm-rm-bt-identifiability
section: alignment
order: 100
level: A
title: RM 基础：preference probability 80%，为什么不能说 chosen 的成功率是 80%？
quick: 我会先分清它预测的是“更喜欢 A”，还是“A 做对了”。preference model 的分数通常不能直接当任务成功率。
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
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

## 面试官可能这样问

RM 给 A 打3分、B 打1分，能说 A 有95%的成功率吗？

## 可以这样回答

这里我会先问，这个模型训练时的标签是什么。如果标签是人更喜欢 A 还是 B，它学到的就是两条回答的相对偏好。A 打3分、B 打1分，我可以用分差去估计 A 胜过 B 的概率，但不能把 A 自己的分数变成任务成功率。

比如两条回答都答错了，人仍然可能更喜欢其中一条。要预测任务成功，我还需要实际成功/失败的标签。另外，同一问题下把所有分数一起加上一个常数，排序和 preference probability 都没变，这也说明绝对分数本身没有那么直接的解释。

## 技术备查

## 场景与问题
同一问题的回答 A、B 奖励为 3、1。业务同学把 sigmoid(3) 当作 A 的任务成功率。请写出正确概率，说明可识别性，并设计一个 calibration 实验。以下均为原创练习。

## 参考答案
Bradley–Terry 假设 $P(A\succ B\mid x)=\sigma(r(x,A)-r(x,B))$，这里是 $\sigma(2)\approx0.881$，不能从中推出 A 独立成功的概率。对同一 prompt 的所有奖励加 $c(x)$，损失不变；训练没有确定每个 prompt 的绝对零点。尺度并非也可任意改动：乘常数会改变预测 confidence，数据可分时还可能出现 margin 持续增长。

calibration 先定义事件“人类更喜欢 A”，在按任务家族隔离的 validation set 上评估 pairwise NLL、Brier 与可靠性分箱；温度参数只在 validation set 拟合。如果要预测执行成功，另收成功标签并训练或 calibration 成功头。不要混用两个目标。

## 追问
**把奖励减均值后就能跨任务排队了吗？** 不能。normalization 提供工程尺度，不自动赋予相同效用含义，跨任务预算仍需独立效用定义。
**相同准确率的两个 RM 怎么选？** 比较 calibration、困难 evaluation slices 及固定候选上的 top-1 选择收益，准确率看不到过度自信。

