---
id: drustz-81060fb8a48ba4a33f
section: openai
order: 53
level: A
title: Plant Infection by Neighbor Count
quick: original-structured-preparation-guide · Plant Infection by Neighbor Count
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
      https://www.1point3acres.com/interview/problems/1130d2a4-2742-5561-83f4-a44975909a44
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Plant Infection by Neighbor Count：按邻居数量感染

> **证据边界**：标题确认核心是“感染邻居的数量”；公开同家族题和本地面经都出现过 **8 邻域**，其中公开题还明确给出阈值。当前 UUID 的完整会员题面未取得，所以 `K` 的具体值、究竟数 4 邻域还是 8 邻域仍应以原页为准，下面把二者做成参数。

## 题意模型

给定植物网格，`.` 表示健康，`X` 表示已感染。每天开始时，统计每棵健康植物在 `directions` 中有多少个感染邻居；数量至少为 `K` 的植物在**下一天一起**变成 `X`。已经感染的植物保持感染。返回网格不再变化前经过的天数。

例如采用 8 邻域、`K=2` 时，某健康格当天相邻两个 `X`，它会在次日感染；它不能立刻帮助同一天的下一格达标。

## 算法

初始扫描所有 `X`，为每个健康邻居累加计数；达到 `K` 时进入 `next_frontier`。按天处理 frontier：先收集本轮新感染，再统一落盘，并把它们对健康邻居贡献的计数加一。每格只感染一次，且只需在计数首次达到 `K` 时入队。

```text
while next_frontier 非空:
    本日 = 去重后的 next_frontier
    同时把本日所有格标为 X
    再更新它们周围健康格的 infected_count
    days += 1
```



## 复杂度与边界

设网格有 `R×C` 格、邻居数上限为 `d`（4 或 8），时间 `O(RC·d)`，空间 `O(RC)`。全健康且无人达阈值、初态已稳定都返回 `0`；`K<=0`、空网格、重复入队、边界格邻居不足，以及错误的“边扫描边感染”都要单独测试。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1130d2a4-2742-5561-83f4-a44975909a44)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
