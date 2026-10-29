---
id: dt-mixture-factorial-budget
section: panel
order: 48
level: A
title: Panel 情景：数学和工具数据单独都有效，一起加入为什么掉点？
quick: >-
  用固定总预算的四组实验估计单独效果与交互，排查替换基础数据、重复率、gradient
  与格式冲突。单独收益不能简单相加，组合表现差也不能直接推出“这两种能力互斥”。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 情景练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
---

## 题目描述

原创实验设计题。四组短训练使用相同 checkpoint、总 token、步数和独立测试：

| 配方 | 平衡能力得分 |
| --- | --- |
| baseline | 70 |
| 加数学数据 A | 74 |
| 加工具数据 B | 73 |
| 同时加 A、B | 71 |

你需要解释交互、审核实验是否公平，并在只剩两次短训练预算时选择后续对照。数字为假设；得分单位为百分点。

## 解题思路与参考答案

组合相对 baseline 只增 1 个点，单独 A 和 B 分别增 4、3 点。二阶交互估计为 `71-74-73+70=-6` 个点，即组合效果低于简单相加的预期。它是当前设置下的交互迹象，不是所有 data mix、规模与任务上的必然结论，且需要考虑测量与训练随机性。

### 公平的四组如何构造

例如固定 80% 共同基础数据，再设两个 10% 的替换槽：baseline 两槽都用基础数据；A 组只替换第一个槽；B 组只替换第二个；AB 两个都替换。这样总预算相同，但解释中要承认改变的是相对被替换基础内容的效果。若 AB 实际删掉了更多关键基础数据、长度或 epoch 也变化，就不能简单 attribution A 与 B 冲突。

### 两次实验怎么选

先不用训练预算做样本审计：检查重复、语言比例、工具格式是否掺入数学解释、长推理是否淹没短工具回复、loss mask 是否一致。若明显是顺序或格式冲突，可一次改为分阶段训练，一次使用修复格式的联合训练；从相同 baseline 开始、匹配总计算并记录训练顺序。若没有机制证据，则优先一次复现实验、一次降低一个数据源权重验证剂量效应。选择应随诊断证据调整，不保证两次就能辨认所有原因。

### 评价方式

拆开数学、工具、基础语言和安全 evaluation slices，查看是不是平衡总分掩盖局部收益。先定主指标和容忍回归，再测跨 seed 或区间。避免在同一小测试上反复挑最高配方后声称普遍有效。

## 面试追问

**为什么不直接删 B？** 单独 B 有收益，问题可能是比例、格式或基础覆盖被挤掉，删除不一定是最佳预算选择。

**gradient 夹角能直接证明原因吗？** 只是局部诊断信号，不等于长期训练结果。需要与受控干预和独立评测对应。

**顺序训练更好就解决了吗？** 还要确认不是增加了训练 token、更新步数或改变了最终任务权重，并检查遗忘。
