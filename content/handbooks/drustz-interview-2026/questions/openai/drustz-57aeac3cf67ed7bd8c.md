---
id: drustz-57aeac3cf67ed7bd8c
section: openai
order: 166
level: A
title: CRUD Backend API and Debugging
quick: original-structured-preparation-guide · CRUD Backend API and Debugging
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
      https://www.1point3acres.com/interview/problems/e971a19f-9946-4e1f-b431-aed746c00283
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Python CRUD 后端与调试

## 题目要做什么

为一个类似 ChatGPT 前端的本地应用实现 Python 后端：

- 先定位并修复一个已有的故障接口；
- 实现 Create、Read、Update、Delete；
- 可以使用 SQLite；
- 让前端能在本地调用这些接口；
- 测试创建、更新、删除、获取列表以及修复后的接口。

## 推荐 API

以用户资源为例：

```text
POST   /users
GET    /users
GET    /users/{id}
PATCH  /users/{id}
DELETE /users/{id}
```



可以使用 FastAPI、SQLAlchemy 和 SQLite。分别定义 `UserCreate`、`UserPatch`、`UserOut`，不要让数据库模型直接承担所有输入校验。

## 实现与调试顺序

1. 先为已有故障接口写一条稳定失败的测试。
2. 按“路由 → 请求 schema → 查询 → 事务 → 响应序列化”的顺序定位第一次偏离预期的位置。
3. 每个请求使用独立数据库 session。
4. 写操作成功后 `commit`，发生异常时 `rollback`；需要返回数据库生成字段时再 `refresh`。
5. 测试使用临时数据库，并覆盖应用的数据库依赖。
6. 修复后保留回归测试，确保不是只对某个样例打补丁。

## 复杂度

有主键索引时，单条查询、更新和删除通常为 `O(log n)`；列表接口为 `O(n)` 时间和 `O(n)` 响应空间。真实成本还取决于数据库实现与索引。

## 容易踩坑

- 重复 email 或其他唯一键；
- 空的 `PATCH`、非法 JSON、资源不存在时的 404；
- 异常后没有回滚，导致 session 不可继续使用；
- SQLite 并发写锁；
- CORS、分页和数据库迁移；
- “类似 ChatGPT”不代表可以自行猜测 conversation/message 的 API 合同。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/e971a19f-9946-4e1f-b431-aed746c00283)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
