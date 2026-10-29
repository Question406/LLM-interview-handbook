---
id: drustz-d978c9a6f4fe282a4a
section: anthropic
order: 48
level: A
title: Task Management System (CRUD + Priority Ordering + User Quota + History Query)
quick: >-
  original-structured-preparation-guide · Task Management System (CRUD +
  Priority Ordering + User Quota + History Query)
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
      https://www.1point3acres.com/interview/problems/284aa27f-5e4a-45d2-b3d9-49d46fd2b2e5
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Task Management：CRUD、排序、配额与历史状态

## 证据边界与可练习题面

公开页只固定四级能力，没有固定函数签名。为使题目可编程，这里采用一套明确合同：任务含 `id, created_at, priority, title, assignee, deleted`。实现 `create(t,title,priority)`、`get(id)`、`update(t,id,title,priority)`、`delete(t,id)`；`list_tasks()` 按 priority 降序、创建序升序；`add_user(id,quota)` 与 `assign(t,task,user)`，用户当前未删除任务数达到 quota 时拒绝；`get_at(task_id,t)` 返回该时刻任务快照或空。这个合同是练习定义，不冒充缺失的会员参数。

例：创建 `T1(p=5)`、`T2(p=9)` 后列表为 `[T2,T1]`；用户 quota=1，分配 T2 成功，再分配 T1 失败；时刻 7 把 T2 优先级改为 2，`get_at(T2,6)` 仍返回 9。

## 数据结构、复杂度与边界

用 `tasks` 保存当前态，自增序号保证 ID 与 tie-break 永不复用；每个用户维护 active task set；每个任务保存按时间排列的不可变快照或事件日志，`get_at` 对时间数组 `bisect_right`。所有校验先完成再原子修改任务与用户集合，失败操作不能写半份状态。

CRUD/分配期望 `O(1)`，历史查询 `O(log H)`；全量排序 `O(N log N)`，历史空间 `O(H)`。测试同优先级、更新后重排、删除释放 quota、重复分配、quota 为零、查询创建前/删除后/删除前、失败更新不写历史、同 timestamp 的约定，以及 title 可重复但 ID 唯一。

历史最稳妥的实现是每次成功变更后追加完整浅快照；字段少时简单可靠。若改存事件以省空间，读取时需从最近 checkpoint 重放，复杂度变为 `O(log H + R)`。删除写 tombstone 而不是移除日志；重新创建是否允许、旧 ID 是否复活必须在合同中先定，本练习选择 ID 永不复用。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/284aa27f-5e4a-45d2-b3d9-49d46fd2b2e5)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
