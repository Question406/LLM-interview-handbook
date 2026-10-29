---
id: drustz-5f8d271eb43b8cf384
section: anthropic
order: 6
level: A
title: Ml Configuration System
quick: locally-saved-research-summary · Ml Configuration System
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-research-summary
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/ml-configuration-system
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## ML Configuration System 轮（RE/MLE 店面 track，2026 新）

四选一 track 之一，2026 年 5-6 月多帖求经/组队但正文均在登录墙内：interview thread 1164302 'ML Configuration System Tech Phone Screen'（含店面后 HR call 和 onsite 流程说明）、1166993 'ML Configuration System Interview Experience Exchange'、1166655。已知只有题目家族名'ML Configuration System'——实现/设计管理 ML 实验配置的系统。

### 解题与准备提示

我的推断（基于题名+同类公司考法）：实现 config 系统支持嵌套配置、默认值+覆盖合并、类型/约束验证、实验 sweep（笛卡尔积展开）、序列化与 reproducibility；用 Python dataclass/dict merge 实现，重点在 API 设计和 edge case（冲突、循环引用、deep merge 语义）。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/ml-configuration-system)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
