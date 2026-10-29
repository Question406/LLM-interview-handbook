---
id: drustz-a15c5eb9c3120486ad
section: anthropic
order: 74
level: A
title: In-Memory Database
quick: original-structured-preparation-guide · In-Memory Database
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
      https://www.1point3acres.com/interview/problems/a52d691f-b59e-48ad-86b1-be301c9921fd
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 简单 In-Memory Database：值计数也要保持一致

> 证据边界：当前 UUID 的公开 description 已给出完整操作和样例；下文是中文改写与原创实现分析，不是会员原文或站内答案。

## 完整题面

从标准输入逐行处理命令：`SET name value` 写入或覆盖字符串；`GET name` 返回当前值，缺失输出 `NULL`；`UNSET name` 删除，缺失时无事发生；`NUMEQUALTO value` 返回当前等于该值的 name 数量；`END` 立即终止。这里没有事务、TTL 或历史查询，不要把其他数据库 OA 的功能加进来。

例：依次执行 `SET name Bob`、`GET name`、`SET name Alice`、`NUMEQUALTO Bob`、`UNSET name`、`GET name`，输出依次为 `Bob`、`0`、`NULL`。

## 数据结构与实现

维护 `values: name -> value` 和 `counts: value -> number of names`。`SET` 覆盖已有 name 时，先把旧值计数减一，再写新值并把新计数加一；即使新旧值相同，也可特判直接返回，避免不必要变动。`UNSET` 同样先从 `values` 取旧值再同步递减；计数降到零可删除键。命令解析若允许 value 含空格，应只切分前两个 token，其余拼回 value；否则按公开合同处理单 token。

所有操作期望 `O(1)`，空间 `O(N+U)`，其中 `N` 为 name 数、`U` 为不同 value 数。边界测试包括重复覆盖、同值多个 name、删除不存在项、删到计数为零、空数据库查询、名字和值相同、连续 `END` 后的命令不可执行，以及输出命令与无输出命令的行数严格对应。

建议把状态更新封装成 `_inc(value)` 与 `_dec(value)`，让 SET 和 UNSET 共用，避免一个分支忘记维护反向计数。可在随机测试中每执行一条命令，就用朴素方式从 `values` 重数所有 value，并断言结果等于 `counts`；这个不变量比只测给定样例更容易抓住覆盖旧值时的错误。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a52d691f-b59e-48ad-86b1-be301c9921fd)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
