---
id: drustz-731e310f79ccf7de77
section: mlsd
order: 115
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 12. 迭代闭环：训练 → trace → 失败模式 → 改数据 ⭐⭐⭐
quick: >-
  作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 12. 迭代闭环：训练 → trace → 失败模式 →
  改数据 ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 12. 迭代闭环：训练 → trace → 失败模式 → 改数据 ⭐⭐⭐

```text
                 ┌──────────────────────────────────────────────┐
                 │                                              │
   数据 pipeline ─┴─→ 训练 run ─→ 训练动态指标 ─→ 下游 eval       │
   （§5–§8）           │            (熵/长度/          │         │
                       │             有效梯度率)       │         │
                       ↓                              ↓         │
                  分层 trace 抽样 (§10.2) ────→ 失败模式归类 ────┘
                                                  │
                    ┌─────────────────────────────┼──────────────────────┐
                    ↓                             ↓                      ↓
            改 verifier（§9）            改质量 gate（§5.3）      改难度带/配比（§7,§11）
            例：加严位置匹配              例：加「无矛盾」检查       例：抬高难度桶下限
```



**什么样的观察值得回流成 pipeline 改动**（不是每个 bug 都值得）：

| 观察 | 回流成什么 | 判据 |
|---|---|---|
| 一类 hack 在 >1% 的高 reward trace 里出现 | verifier 规则 + 一条离线检测指标 | 频率够高且可自动检测 |
| 某个数据源的 trace 大量格式错乱 | S0 解析器修复 + 该源整批重跑 | 源级问题，不是样本级 |
| 某题族稳定诱发失控推理 | 质量 gate 加一条题型排除 | 能刻画成规则 |
| 某个 checkpoint 后有效梯度率跌破阈值 | 触发 reserve 池重探（§7.4） | 自动触发，不需要人判断 |
| 单条题判错 | **不回流**，直接修那条 | 一次性问题做成规则会overfitting |

**节奏建议**（可以直接讲的运营方案）：数据版本按周切；每个训练 run 结束做一次固定格式的失败模式归类（类别 + 频率 + 是否可自动检测 + 修法）；每个季度做一次全量重探 + 全量去污重跑。

> **和 [08](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) 的关系**：那边讲的是产品系统的 offline→online 闭环，这里的闭环没有「线上」这一端——**裁判是下游 eval，反馈延迟是一个训练 run 的长度（几天）**，不是用户行为的几天。所以这里的闭环设计重点是**在一个 run 内部就能拿到的领先指标**（熵、长度、有效梯度率），否则你一次只能做一个实验。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
