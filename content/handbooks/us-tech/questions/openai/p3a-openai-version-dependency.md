---
id: p3a-openai-version-dependency
section: openai
order: 620
level: A
title: "OpenAI：包版本依赖：约束解析与求解"
quick: "用允许版本集合表示每个包的约束，选定一个版本后，把它的依赖与已有集合求交集，冲突就回溯。拓扑排序只决定安装先后，不能解决多版本冲突；参考实现优先试候选最少的包，找任意可行解，无解返回 None。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · version-dependency"
    url: https://www.1point3acres.com/interview/problems/company/openai/version-dependency
    type: secondary
---

## 题目描述

实现精确版本依赖解析，返回满足所有根约束和传递依赖的一组版本选择。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`resolve(repo,roots)` 返回 `{包名:版本}` 或 None。repo[pkg][version] 是该版本的依赖字典，依赖项映射到允许版本集合；roots 同样是包名到允许版本集合。版本为非负整数。

返回结果必须包含全部根包及其传递依赖，每个包只选一个 repo 中存在的版本，同时满足所有来自根或已选依赖的版本约束。允许依赖环，只要能一致满足；缺失包或无法满足的约束返回 None。不要求选择最大版本，任意合法完整方案均可。包不超过 15 个，每包不超过 5 个版本。

### 示例

```text
repo 中 A@1 依赖 B 的 {1}，A@2 依赖 B 的 {2}；B@1、B@2 无依赖。
roots={A:{1,2},B:{1}}，返回 {A:1,B:1}。
roots={A:{2},B:{1}}，返回 None。
```

## 解题思路与参考答案

我会把依赖解析成约束满足问题，用候选版本集合加回溯求解。比如 A2 要求 B2，根需求却只允许 B1，就要退回尝试 A1；只做拓扑排序无法改变版本冲突。每选一个版本就传播依赖约束，集合为空或已选版本不再满足时立即回溯。

给一个包仓库，每个包有多个版本，每个版本声明自己依赖哪些包的哪些版本。要求解析这些依赖关系，支持查询，并为一组根需求选出一组互相兼容的版本。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。网站摘要对完整求解器的规格并不确定；下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

把每个包的候选版本和依赖约束显式建模：每个包对应一个「还允许哪些版本」的集合。选定某个包的某个版本后，把它的依赖要求和对应包的允许集合求交集，这一步就是约束传播。某个集合变空，说明这条路走不通，回溯换一个版本。

单纯的拓扑排序解决不了这个问题。拓扑排序只回答「先装谁」，而这里的难点是同一个包有多个版本，选了 A 的某个版本会限制 B 能用哪些版本，不同选择之间会冲突。贪心地给每个包选最高版本也可能走进死路，必须能回退。

动手前先问清楚：是必须为整棵依赖树求出全局一致的解，还是只解析单个包；无解时返回什么；有多个解时是否要求某种最优（比如版本尽量高）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `repo[package][version]`：这个版本的依赖，格式是 `{依赖包: 允许的版本集合}`。版本号是非负整数。
- `resolve(repo, roots)`：`roots` 是 `{包: 允许的版本集合}`。返回一个覆盖根需求和全部传递依赖的版本选择 `{包: 版本}`，无解时返回 `None`。
- 允许依赖成环，只要版本约束一致就有解。依赖了仓库里不存在的包视为无解。
- 最多 15 个包，每个包最多 5 个版本。要求精确回溯，找到任意一个可行解即可，不要求版本最高。

### 输入输出示例

```text
repo = {A: {1: {B: {1}}, 2: {B: {2}}}, B: {1: {}, 2: {}}}
resolve(repo, {A: {1, 2}, B: {1}})   -> {A: 1, B: 1}
resolve(repo, {A: {2}, B: {1}})      -> None    # A2 需要 B2，与根要求冲突
```

### 解题思路与正确性

`search(chosen, allowed)` 维护两样东西：已经定下版本的包，以及每个已知包当前还允许的版本集合。每层先检查已选版本是否仍在允许集合里，因为新加入的依赖可能收紧了之前选过的包。然后挑一个还没定版本、候选最少的包（MRV 启发式），逐个尝试它的候选版本，把这个版本的依赖并入约束后递归。

这个搜索会枚举所有可能的版本组合，只剪掉已经确定冲突的分支，所以有解时一定能找到，返回 `None` 时就证明了无解。依赖环不会导致死循环：已经定了版本的包不会再被选择，环上的约束只是被反复求交集。

### 完整参考实现（Python 3）

```python
def resolve(repo, roots):
    """为根需求及其全部传递依赖选出一组一致的版本，无解时返回 None。

    repo[package][version] 是这个版本的依赖：{依赖包: 允许的版本集合}。
    roots 是 {包: 允许的版本集合}。返回 {包: 选中的版本}。
    """

    def search(chosen, allowed):
        # 已选的版本必须仍满足所有约束（新加的依赖可能收紧了它）
        for package, version in chosen.items():
            if version not in allowed[package]:
                return None
        pending = [package for package in allowed if package not in chosen]
        if not pending:
            return chosen

        candidates = {
            package: sorted(set(repo.get(package, {})) & allowed[package])
            for package in pending
        }
        # 先处理候选最少的包（MRV），冲突能更早暴露
        package = min(pending, key=lambda name: (len(candidates[name]), name))
        for version in candidates[package]:
            next_allowed = narrow(allowed, repo[package][version])
            if next_allowed is None:
                continue
            answer = search({**chosen, package: version}, next_allowed)
            if answer is not None:
                return answer
        return None

    def narrow(allowed, dependencies):
        """把一个版本的依赖并入约束；某个包没有可选版本时返回 None。"""
        next_allowed = {package: set(versions) for package, versions in allowed.items()}
        for dependency, versions in dependencies.items():
            current = next_allowed.get(dependency, set(repo.get(dependency, {})))
            next_allowed[dependency] = current & set(versions)
        if any(not versions for versions in next_allowed.values()):
            return None
        return next_allowed

    initial = {package: set(versions) for package, versions in roots.items()}
    return search({}, initial)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert resolve(repo, {"A": {1, 2}, "B": {1}}) == {"B": 1, "A": 1}` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
repo = {
    "A": {1: {"B": {1}}, 2: {"B": {2}}},
    "B": {1: {}, 2: {}},
}

# A1 依赖 B1，与根要求的 B1 一致
assert resolve(repo, {"A": {1, 2}, "B": {1}}) == {"B": 1, "A": 1}

# A2 依赖 B2，但根要求 B1，无解
assert resolve(repo, {"A": {2}, "B": {1}}) is None

# 依赖环本身不是错误
cyclic = {"A": {1: {"B": {1}}}, "B": {1: {"A": {1}}}}
assert resolve(cyclic, {"A": {1}}) == {"A": 1, "B": 1}

# 仓库里没有的包无法满足
assert resolve(repo, {"X": {1}}) is None

# 需要回溯：先试的 A1 会把 C 限制到不存在的版本
backtrack = {
    "A": {1: {"C": {9}}, 2: {"C": {1}}},
    "C": {1: {}},
}
assert resolve(backtrack, {"A": {1, 2}}) == {"A": 2, "C": 1}
```

### 复杂度与追问

设包数为 P、每个包的版本数为 V。最坏情况要尝试 $O(V^P)$ 种组合，每个分支还要复制约束、处理依赖。这种指数级是精确依赖求解本身的特点（一般情况下这个问题是 NP 完全的）；MRV 能在实践中大幅减少搜索，但不改变最坏情况的上界。

- 追问「想要尽量新的版本」：候选按版本从高到低尝试，返回的第一个解就偏向新版本；如果要求全局最优，需要在搜索中维护当前最优并继续枚举，或者交给 SAT/优化求解器。
- 追问「真实的 SemVer 范围和可选依赖」：要先把 `^1.2`、`>=2,<3` 之类的范围解析成具体版本集合，可选依赖要额外建模成「装或不装」两个分支。本题已经直接给了版本集合，省掉了这一步。
