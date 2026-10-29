---
id: drustz-73a0a1ff2e819edbc6
section: anthropic
order: 55
level: A
title: Python Data Analysis on a Provided Dataset (Capacity Management Context)
quick: >-
  original-structured-preparation-guide · Python Data Analysis on a Provided
  Dataset (Capacity Management Context)
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
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
      https://www.1point3acres.com/interview/problems/d03ad0c8-580a-4af4-8619-328ea8011719
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Python Data Analysis：Capacity Management

> 完整数据集和问题列表未公开。旧内容是系统设计资料，并不能替代数据分析题。下面给出不依赖虚构列名的分析流程。

## 分析目标

容量管理通常要回答：当前使用率是多少、何时会耗尽、哪些资源或租户形成热点、需要多少安全余量，以及数据质量是否足以支持预测。

## 推荐步骤

1. 读取数据并检查 schema、时间范围、单位、重复行和缺失值；
2. 将时间列解析为统一时区，确认sampling间隔；
3. 定义 `utilization = used / capacity` 与 `headroom = capacity - used`；
4. 按资源、区域或租户 groupby，计算平均、p95、p99 和峰值；
5. 用时间序列图检查趋势、周期、突发和变更点；
6. 区分 capacity 变化与 demand 变化，不能只外推 utilization；
7. 给出阈值告警和带confidence interval的耗尽日期；
8. 记录假设、异常处理规则和无法回答的问题。

```python
df["utilization"] = df["used"] / df["capacity"]
summary = (
    df.groupby("resource")["utilization"]
    .agg(mean="mean", peak="max", p95=lambda s: s.quantile(0.95))
    .sort_values("p95", ascending=False)
)
```



## 复杂度

`n` 行数据的清洗和 groupby 通常为 `O(n)` 平均时间；排序或精确 quantile 常为 `O(n log n)`；DataFrame 内存为 `O(n × columns)`。

## 边界

capacity 为 0、单位混用、缺失时间段、sampling频率改变、counter reset、峰值被平均掩盖、未来扩容计划未入表，以及把相关性误当成需求增长原因。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/d03ad0c8-580a-4af4-8619-328ea8011719)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
