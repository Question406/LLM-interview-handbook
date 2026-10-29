---
id: drustz-915e6e57e2a1cad9a6
section: openai
order: 19
level: A
title: Version Dependency
quick: original-structured-preparation-guide · Version Dependency
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
      https://www.1point3acres.com/interview/problems/company/openai/version-dependency
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Version Dependency：包版本依赖解析

> 修正说明：旧正文是“二分查找第一个支持某 feature 的版本”，与 package dependency resolver 不是同一题，已经移除。公开摘要没有四个子问题的完整 API，下面给出与已知题意一致的实现模型。

## 可以确认的题意

输入若干包、可用版本和版本依赖，例如：

```text
A@1.0 requires B >= 2.0
```



需要解析依赖、回答查询，并选择一组彼此兼容的包版本。题目可能分四个阶段逐步加入查询、传递依赖、冲突检测和真正的版本求解。

## 基础数据模型

```text
available[package] = 按语义版本排序的版本列表
requires[(package, version)] = [Dependency(name, constraint), ...]
```



不要用字符串字典序比较版本：`"10.0"` 会排在 `"2.0"` 前面。至少把 `major.minor.patch` 解析成整数 tuple；如果要求完整 SemVer，还要处理 prerelease。

## 求解思路

1. 从根包的约束开始维护 `constraints[package]`；
2. 选择一个尚未确定版本的包；
3. 从满足当前全部约束的候选版本中选择一个，例如先尝试最高版本；
4. 把该版本的依赖约束传播到其他包；
5. 某个包没有可用候选时回溯；
6. 所有可达包都确定且约束满足时返回解。

可以优先选择候选最少的包，尽早发现冲突。依赖环本身不一定错误；只有环中的版本约束无法同时满足时才失败。

```text
solve(assignments, constraints):
    if every required package is assigned: return assignments
    p = unassigned package with fewest valid versions
    for v in valid_versions(p), high to low:
        tentatively assign p = v and propagate requirements
        if no conflict and solve(...) succeeds: return solution
    return no solution
```



## 复杂度

只遍历固定版本的传递依赖是 `O(V + E)`。允许多个版本并需要回溯时，本质接近 SAT/CSP，最坏时间是指数级；空间取决于依赖图、约束和回溯栈。

## 边界

包不存在、版本字符串非法、同一包收到互斥约束、重复依赖、环依赖、prerelease、选择最高还是最低兼容版本，以及错误信息是否要给出最小冲突链。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/version-dependency)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
