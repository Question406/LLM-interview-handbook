---
id: drustz-1ecdfd16a11a6d6278
section: openai
order: 164
level: A
title: Excel Sheet Operation
quick: original-structured-preparation-guide · Excel Sheet Operation
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
      https://www.1point3acres.com/interview/problems/106dedaf-ce19-4c30-a62d-39cf777e507e
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Excel Sheet Operation：按需求值的迷你表格

## 证据边界

当前标题只写 Excel Sheet Operation；同题族公开页提供 `setCell/getCell`、数字、单元格引用、四则公式和循环检测。下面采用这个基础版本；缓存传播属于另一个明确带 Caching 的 UUID，不在本题中假定为硬要求。

## 题面、接口与输入输出示例

```text
setCell("A1", "1")
setCell("A2", "2")
setCell("A3", "=A1+A2")
getCell("A3") -> 3.0
setCell("A1", "10")
getCell("A3") -> 12.0
```



公式支持 `+ - * /` 与 cell reference；若 `A1="=B1+1"`、`B1="=A1+1"`，查询必须报告 circular dependency，而不是无限递归。不存在单元格返回 0、None 还是错误，需要以现场测试确认。

## 解法与数据结构

`raw[cell]` 保存原始数字或公式。get 时解析表达式为 token/AST，对引用做 DFS；`visiting` 集合表示当前递归栈，重遇即成环，`memo` 缓存本次查询已经算出的共享子表达式。不要直接对不可信字符串调用语言 `eval`，应写有限的 tokenizer 与运算符解析器。set 只替换 raw，因此后续查询自然读取最新依赖；求值失败不能污染 memo 或 raw。

DFS 离开单元格时必须从 visiting 移除；否则两个互不成环、但共享依赖的分支会被误判。memo 与 visiting 作用不同：前者表示本次查询已算完，后者只表示当前调用栈正在计算。每次顶层 get 新建二者，便不会在 set 后错误复用旧结果。

## 复杂度与边界

set 为 `O(|value|)`；一次 get 访问可达的 `V` 个 cell、`E` 条引用，约 `O(V+E+公式字符数)`，递归栈 `O(V)`。测试自引用、长环与钻石依赖、A1/A10 token 边界、负数与括号、除零、非法公式、重复引用、空白、未知 cell、大小写以及非常深依赖链；深链可改显式栈避免递归上限。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/106dedaf-ce19-4c30-a62d-39cf777e507e)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
