---
id: afm-mock-debug-tools
section: mock
order: 30
level: A
title: 附件诊断 1：总体成功率涨了，两个任务桶为什么都退化？
quick: 先用统一分布重算指标，再用错误样本区分工具选择、参数与状态核验。当前汇总表只能说明分布混杂，不能单独证明某个训练源导致退化。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - 全流程模拟
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: RewardBench 2
    url: 'https://arxiv.org/abs/2506.01937'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

## 候选人材料
原创45分钟情景题；数据为人工构造，不是 Apple 记录。[指标 CSV](/apple-prep/tool_metrics.csv)、[逐条错误 JSONL](/apple-prep/tool_errors.jsonl)、[计算核对脚本](/apple-prep/analyze_cases.py)。前10分钟只看附件，先写假设再读答案。

| 版本 | 简单任务正确/总数 | 困难任务正确/总数 | 总体 |
| --- | --- | --- | --- |
| baseline | 18/20 | 40/80 | 58% |
| new | 68/80 | 9/20 | 77% |

产品据此想上线。你有2个训练实验名额：应补更多成功 JSON、失败恢复 trajectories，还是状态核验数据？要求给证据、区分性实验及上线条件。

## 建议时间
0–10分钟重算；10–20分钟读错误并做故障树；20–32分钟设计实验；32–40分钟规划数据；40–45分钟报告风险与结论。评分看诊断过程，不要求猜到唯一答案。

## 参考分析
简单任务90%降到85%，困难50%降到45%。用 baseline 的20%/80%权重，new 为53%，比58%低5个百分点。77%是新评测更偏向简单题的混合结果。这是描述性比较；分母不同、没有配对记录，不能直接计算配对显著性或 attribution 训练。

JSONL 同时给出工具选错、工具正确但参数错、超时后重复写入、空结果却报成功、timezone / DST handling 错误。应先审计 replay 器、工具 schema、策略模板与环境版本，再提出数据问题。小附件是刻意覆盖的教学样本，不能用其频率估计自然流量。

两个实验名额可用于固定环境/模板的 ablation study 与一种定向数据干预：例如用 oracle 工具选择、oracle 参数分别替换，确认主要瓶颈后补相应失败恢复与状态核验 trajectories。若条件允许，先做无需训练的 controlled substitution 诊断，避免浪费训练名额。训练对照固定算力、总 token 和原 mix，保留正常成功与权限拒绝 evaluation slices。副作用违规单独设上限，不能由其他得分抵消。

## 追问与评分
**看见三条超时就补超时数据？** 先确认 sampling 机制和 replay 可靠性，再用代表性样本估算问题规模。
**上线证据还缺什么？** 同一任务集的配对结果、足够样本、关键错误、延迟成本以及盲测。

五项各0–4：分母与 standardization、错误分类、竞争假设、可 attribution 实验、发布判断。14分为自练通过线；无法识别两桶同时下降时先重练指标分析。
