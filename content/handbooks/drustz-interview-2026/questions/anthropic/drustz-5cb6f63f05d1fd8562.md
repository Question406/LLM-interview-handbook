---
id: drustz-5cb6f63f05d1fd8562
section: anthropic
order: 39
level: A
title: Multi-Level In-Memory Database with TTL and Time Travel
quick: >-
  original-structured-preparation-guide · Multi-Level In-Memory Database with
  TTL and Time Travel
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
      https://www.1point3acres.com/interview/problems/a3816a9d-04af-5a4a-8363-20be75018fd2
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 多级内存数据库：TTL 与时间旅行

## 证据边界与练习题面

当前公开标题能确认三项主题，本地非会员同题族保存了四级接口；下面据此整理成可运行的练习合同，不声称是会员原文。数据库保存 `key -> field -> integer value`，时间戳严格递增。实现 `set_at`、`get_at`、`compare_and_set_at`、`compare_and_delete_at`、`scan_at`、`scan_by_prefix_at`；再加入 `set_at_with_ttl(t,key,field,value,ttl)`，有效区间为 `[t,t+ttl)`；最后实现 `get_when(now,key,field,at)` 查询过去 `at` 时刻的值，不存在返回空串。

例：时刻 1 写 `A.x=10, ttl=5`，时刻 3 改成永久值 20；在时刻 10 查询 `at=2` 得 10，查询 `at=7` 得 20。扫描按 field 字典序输出 `field(value)`。

## 解法、复杂度与测试

为每个 `(key,field)` 保存按起始时间递增的版本数组，元素含 `start,end,value,deleted`；新写入先关闭旧版本，再追加新版本，TTL 令 `end=min(下一版本时间,start+ttl)`。`get_when` 用 `bisect_right(start_times, at)-1` 找候选，再检查 `at < end` 且非墓碑。当前读和 CAS 复用同一可见性函数，避免 TTL 规则分叉。

写入均摊 `O(1)`，历史单字段查询 `O(log H)`；扫描 `F` 个字段需 `O(F log H + F log F)`，历史占 `O(H)`。重点测试恰在过期时刻、删除后查过去、同字段多次覆盖、CAS 命中过期值、空前缀、缺失 key、`at > now`、TTL 非正数，以及永久版本被带 TTL 版本覆盖。

实现时要保持一个核心不变量：同一字段的可见版本区间互不重叠。物理清除过期当前值时不能删掉历史数组，否则时间旅行会失真；可只做惰性不可见，或把冷历史转移到归档。扫描必须对每个字段在目标时刻分别判活，不能因为 record 当前为空就断定过去也为空。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a3816a9d-04af-5a4a-8363-20be75018fd2)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
