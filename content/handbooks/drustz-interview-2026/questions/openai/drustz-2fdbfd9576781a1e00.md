---
id: drustz-2fdbfd9576781a1e00
section: openai
order: 70
level: A
title: Infectious Disease Simulation / Containment (unspecified)
quick: >-
  original-structured-preparation-guide · Infectious Disease Simulation /
  Containment (unspecified)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/06f15ce5-2ae4-473c-baa8-1edfdb0936f8
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Infectious Disease Simulation / Containment：先确认目标再编码

> **重要限制**：公开信息只给出标题中的 “Simulation / Containment”，没有当前 UUID 的精确状态、邻接方式、可执行的隔离动作或优化目标。其他同家族材料出现过免疫、康复、死亡阈值和烧掉一行/列，但这些都只能作为**可配置变体**，不能写成这道题已经确认的原题。

## 通用模型

把每格表示为 `S`（易感）、`X(age)`（感染）、`I`（免疫/隔离）或 `D`（死亡/永久障碍）。`neighbors`、感染阈值、感染持续天数和每日 containment 动作都由 `Rules` 提供。每天从不可变的旧状态计算 `next_state`，这样不会发生同一天连锁传播。

例如，若允许每天把一格设为 `I`，状态 `X . .` 可在传播前隔离中间格；若隔离发生在传播后，结果完全不同。因此必须先问清“动作在一天的哪个阶段发生”。

## 解题路线

若隔离方案已给定，只需逐日模拟：先应用当天隔离，再收集传播、康复或死亡事件，最后统一提交。若要求**选择**隔离位置以最小化感染/死亡，则这已经是搜索或优化问题：小网格可把 `(grid, day)` 作为状态做 BFS/DP；大网格通常只能给贪心或启发式，并说明不保证最优。不能用一次多源 BFS 冒充 containment 最优解。

```text
old -> apply_containment -> collect_events(old) -> commit(next)
```



## 复杂度与边界

固定策略模拟 `T` 天为 `O(T·RC)` 时间、`O(RC)` 空间；枚举每天 `A` 个动作可能指数增长。需覆盖无感染源、全隔离、无法阻断、并列最优方案、动作与传播同日冲突，以及状态重复导致的循环。拿到原题后再补充准确目标和返回值。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/06f15ce5-2ae4-473c-baa8-1edfdb0936f8)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
