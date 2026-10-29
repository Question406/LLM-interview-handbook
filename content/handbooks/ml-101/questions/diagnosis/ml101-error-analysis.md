---
id: ml101-error-analysis
section: diagnosis
order: 6
level: A
title: 错误分析怎么从总体指标走到可行动的数据切片？
quick: >-
  先把错误归类到有业务含义的切片，比较错误率、样本量与错误总贡献，再抽样看具体失败原因。比如低清图错误率高，但只有少量流量，是否优先修还要看影响；发现的切片要用留出数据复核，避免只是在追噪声。
tags:
  - ML101
  - diagnosis
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'Error Analysis: Understanding model errors'
    url: 'https://erroranalysis.ai/'
    type: primary
---

错误分析要把总体分数拆成“哪些样本错、错在哪里、修哪一类最有价值”。我会先按时间、设备、语言、输入长度或业务人群分组，同时记录样本数、错误率和错误数量，找出平均分掩盖的薄弱部分。 [Error Analysis: Understanding model errors](https://erroranalysis.ai/)

例如总体准确率不错，低清图片的错误率却明显更高。先看这组有多少样本，再读一些错例，判断是文字看不清、label definitions 不同，还是预处理裁掉目标。仅知道低清组分数低，还不足以决定加模型还是补数据。

行动按诊断结果定：标签问题做复核，覆盖不足补代表性样本，固定处理错误先修管道。把改动与切片假设记下来，在留出集复测目标切片和总体表现，并检查别的切片是否退化。

## 追问

**错误率最高的切片一定最优先吗？**
不一定。还要看样本量、业务代价和修复成本。极小切片可能只是估计不稳定。

**自动发现的切片能直接当原因吗？**
不能。它说明误差与某些属性同时出现，需要读样本和做验证来寻找原因。

**一直拆切片会有什么问题？**
尝试得越多，越容易偶然发现很差的小组。预先定义核心切片，并用新数据确认探索得到的发现。
