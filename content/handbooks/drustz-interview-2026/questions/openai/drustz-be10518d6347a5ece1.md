---
id: drustz-be10518d6347a5ece1
section: openai
order: 114
level: A
title: Data Labeling Task Scheduler Construction
quick: >-
  original-structured-preparation-guide · Data Labeling Task Scheduler
  Construction
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
      https://www.1point3acres.com/interview/problems/380d0ad9-8d2e-460b-8a39-f347fe4e3328
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Data Labeling Task Scheduler：轮转构造与前缀均衡

## 证据边界

公开标题、本地直接面经和同题族保存页一致确认 `t` 个 task、`m` 个 model、`h` 个 human、目标 `k`，并要求任意 schedule 前缀内保持均衡。下述是基于这些证据的重新表述，不是当前会员页逐字原文；失败返回 None、空列表或异常需按现场接口决定。

## 完整题面、接口与示例

返回 `(task, model, human)` 列表：每个 human 至少参与 k 次；同一 `(task,human)` 最多一次；对每个固定 task，在任意输出前缀中，各 model 次数最大差不超过 1，各 human 次数最大差也不超过 1。`t=3,m=2,h=4,k=2` 可返回：

```text
[(0,0,0),(1,0,1),(2,0,2),(0,1,3),
 (1,1,0),(2,1,1),(0,0,2),(1,0,3)]
```



## 构造与正确性

若 `k>t` 则不可能，因为一名 human 不能重复同 task；否则做 k 轮，每轮依次处理所有 human u，令 `task=(u+round)%t`。维护 `task_seen[task]`，令 `model=task_seen[task]%m` 后再加一。每人每轮恰有一次，因此总数正好 k；同一人的 k 个 task 在 `k<=t` 时互异。每个 task 的 model 按 0..m-1 轮转，任意前缀计数只可能相差 1；task-human 的计数只有 0/1，均衡条件自动成立。输出长度 `h*k` 也是最短。

实现后最好再写独立 validator，逐条扫描 schedule，维护 human 总数、`(task,human)` 集合和每个 task 的 model/human 计数，并在每次追加后检查最大差。这样可验证“每个前缀”而不是只看最终分布，也能及时发现 tuple 字段顺序写反。

## 复杂度与边界

构造时间 `O(hk)`，辅助数组 `O(t)`，输出本身 `O(hk)`。`k=0` 返回空；k>0 时需 `t,m,h>0`。测试 `k=t`、m=1、h 远大于 t、每一条前缀而非只检查最终结果、tuple 重复、输入负数和确定性顺序。若要求每天分批或中途恢复，还需持久化 round、human 游标和 task_seen，那是额外变体。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/380d0ad9-8d2e-460b-8a39-f347fe4e3328)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
