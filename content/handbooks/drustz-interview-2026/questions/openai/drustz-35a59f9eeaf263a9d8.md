---
id: drustz-35a59f9eeaf263a9d8
section: openai
order: 154
level: A
title: GPU Credit Management System
quick: original-structured-preparation-guide · GPU Credit Management System
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
      https://www.1point3acres.com/interview/problems/ed86e7bd-0545-4aa1-8a8a-4d1b5b4e60f0
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# GPU Credit Management System：乱序事件与时间线重放

> “Management System” 的公开标题未披露完整规则；本地 GPU Credits II 资料明确出现乱序事件。下面把它作为独立系统版准备，不与简单余额类混写。

## 接口与状态

```text
record(event_id, timestamp, GRANT | SUBTRACT, payload)
balance_at(timestamp) -> number | failure-state
```



事件按到达顺序追加，但结果必须像它们一直按逻辑时间执行。例如先收到 `SUBTRACT(t=5,3)`，后收到 `GRANT(t=1,10,expire=9)`，查询 `t=6` 时应按 `t=1` 再 `t=5` 重放，而不是按网络到达顺序。

## 算法

以 `event_id` 幂等去重，把事件存入按 `(timestamp,sequence)` 排序的结构。查询时从不晚于目标时间的 checkpoint 开始，依次应用事件；活跃 grant 用按 expire 的堆，扣减采用最早到期优先。插入旧事件后，废弃它之后的 checkpoint 并重新计算。基础实现每次从头重放最清晰，优化后可用分块快照或持久化有序树。

事件日志应不可变；更正旧事件可以追加 tombstone 或 replacement，而不是原地覆盖。checkpoint 必须记录其覆盖到的稳定排序键和 schema 版本，恢复后再重放后缀。并发写入由单一序列号分配器或数据库事务确定顺序，才能让相同输入在每次重放时得到相同结果。

## 复杂度与必须确认的规则

从头查询为 `O(E log G)`；有 checkpoint 时为 `O((E-C)log G)`，存储 `O(E+G)`。同 timestamp 必须有稳定 tie-break；还要测试重复事件、撤销/更正、过期、浮点时间和并发写入。资料并不能证明余额不足时是拒绝并回滚、允许部分消费，还是让后续 `get_balance` 返回 `None`；实现前必须询问，测试未确认时应在页面明确标“待确认”，不能把不同面经变体合成唯一题面。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ed86e7bd-0545-4aa1-8a8a-4d1b5b4e60f0)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
