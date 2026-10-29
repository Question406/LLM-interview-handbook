---
id: drustz-b0399ec3be383cbab9
section: anthropic
order: 54
level: A
title: Basic SQL Exercise + Learning/Skill-Growth Discussion
quick: >-
  original-structured-preparation-guide · Basic SQL Exercise +
  Learning/Skill-Growth Discussion
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
      https://www.1point3acres.com/interview/problems/a278d355-79f7-44a0-8a10-ce7e6c8e055f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Basic SQL + Learning / Skill-Growth Discussion

> 旧正文是字段级 NoSQL OA，与标题不符。公开页面没有表结构和逐字问题，因此不虚构具体查询。

## SQL 答题方法

先确认表、主外键、基数、NULL 语义和期望输出粒度，再按逻辑执行顺序推导：

```text
FROM / JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY / LIMIT
```



复杂查询用 CTE 分步验证，特别检查 join 是否因一对多关系放大行数。窗口函数要明确 partition、order 和并列处理。

## Growth 行为题

使用 STAR，但重点是可验证的学习闭环：

- 具体能力缺口与为什么重要；
- 主动学习、请教和反馈方式；
- 如何衡量已经掌握；
- 怎样应用到真实项目；
- 结果、复盘和下一步。

## 复杂度与边界

全扫 `O(N)`；索引查询约 `O(log N + K)`；hash join `O(N+M)`；排序/窗口常为 `O(N log N)`。覆盖 NULL 三值逻辑、重复行、LEFT JOIN、COUNT 差异、聚合后过滤、排名并列、时区和除零。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a278d355-79f7-44a0-8a10-ce7e6c8e055f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
