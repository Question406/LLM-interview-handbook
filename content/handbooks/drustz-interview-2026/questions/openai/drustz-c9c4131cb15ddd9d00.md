---
id: drustz-c9c4131cb15ddd9d00
section: openai
order: 120
level: A
title: Resolve Python Dependency Versions
quick: original-structured-preparation-guide · Resolve Python Dependency Versions
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
      https://www.1point3acres.com/interview/problems/7edea219-bdbe-49a3-bf45-7958cb6188ac
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Resolve Python Dependency Versions

> 这条 OJ 的完整约束未公开。标题与公开的 package version dependency 题属于同一问题家族，但下面是独立编写的 Python 依赖求解准备题，不是逐字原题。

## 清晰的问题模型

给定每个 package 的可用版本，以及每个具体版本声明的依赖约束，选择一组能同时满足全部约束的版本。如果无解，返回冲突。

```text
available["A"] = [1.0.0, 2.0.0]
requires[("A", 2.0.0)] = ["B>=3.0,<4.0"]
```



## 解题思路

把它视为 constraint satisfaction problem：

1. 解析 PEP 440 或题目指定的简化版本格式，不要直接比较字符串；
2. 为每个包维护当前全部约束；
3. 选择合法候选版本最少的未赋值包；
4. 尝试一个版本并传播它的新依赖；
5. 某个包候选集变空时撤销本次修改并回溯；
6. 所有可达包都有版本时返回结果。

```python
def solve(assignments, constraints):
    if all_required_packages_assigned(assignments, constraints):
        return assignments.copy()

    package = choose_most_constrained_package(assignments, constraints)
    for version in valid_versions(package, constraints):
        changes = assign_and_propagate(package, version, assignments, constraints)
        if changes is not None:
            answer = solve(assignments, constraints)
            if answer is not None:
                return answer
        rollback(changes, assignments, constraints)
    return None
```



## 复杂度

固定版本的依赖遍历是 `O(V + E)`；需要选择版本和回溯时，最坏情况是指数级。实际可通过“候选最少优先”、冲突缓存和提前传播显著剪枝。

## 边界

依赖环、互斥上下界、包或版本不存在、pre-release、平台条件依赖、重复约束，以及解析规则究竟采用 SemVer 还是 PEP 440。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/7edea219-bdbe-49a3-bf45-7958cb6188ac)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
