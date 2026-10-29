---
id: lc-17-letter-combinations-of-a-phone-number
section: backtracking
order: 1
level: A
title: LC 17 · 电话号码的字母组合
quick: 用回溯，每一层给一个数字挑一个对应字母，处理完所有数字就把这条组合存下来，数字到字母的映射直接写死。空输入要特判返回空列表，否则会收到一条空串。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 17. 电话号码的字母组合
    url: 'https://leetcode.cn/problems/letter-combinations-of-a-phone-number/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定由数字 2 到 9 组成的字符串 digits，每一位从电话按键对应的字母中选择一个字母，保持数字位置的顺序，返回所有可能的字母字符串。映射为：`2→abc`、`3→def`、`4→ghi`、`5→jkl`、`6→mno`、`7→pqrs`、`8→tuv`、`9→wxyz`。

### 接口与输出

实现 `letterCombinations(digits: str) -> List[str]`。每个结果的长度等于 digits 的长度，结果之间不重复，返回顺序不限。

### 合法输入与约束

官方公开约束为 `1 <= len(digits) <= 4`，每个字符均在 2 到 9 之间。本手册接口兼容空字符串，约定空字符串返回 `[]`；不涉及按键 0 或 1。

### 示例

```text
输入：digits = "23"
输出：["ad","ae","af","bd","be","bf","cd","ce","cf"]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/letter-combinations-of-a-phone-number/description/)。

## 解题思路与参考答案

## 题意

数字串 `digits`（`'2'` 到 `'9'`），按九键映射成字母组合，返回所有可能字符串。`digits` 为空则返回空列表。

## 思路

这是标准回溯。下标 $i$ 对应第 $i$ 个数字，枚举它映射的每个字母追加到路径上，再递归 $i+1$；$i$ 走到头就收一条答案。映射表写死就行。

讲的时候可以画一棵「每位分叉 3 或 4」的树。拿 `"23"` 来说，第一层在 `abc` 里选一个，第二层在 `def` 里选一个，叶子从左到右就是 `ad`、`ae`、`af`、`bd`……一共 9 条。

空输入要先特判，否则会收到一条空串。迭代写法用队列按层扩展，走的是同一棵树。

## 参考代码

```python
from typing import List

MP = {
    "2": "abc",
    "3": "def",
    "4": "ghi",
    "5": "jkl",
    "6": "mno",
    "7": "pqrs",
    "8": "tuv",
    "9": "wxyz",
}


def letterCombinations(digits: str) -> List[str]:
    if not digits:
        return []
    ans = []
    path = []

    def dfs(i: int) -> None:
        if i == len(digits):
            ans.append("".join(path))
            return
        for ch in MP[digits[i]]:
            path.append(ch)
            dfs(i + 1)
            path.pop()

    dfs(0)
    return ans


if __name__ == "__main__":
    assert letterCombinations("23") == [
        "ad",
        "ae",
        "af",
        "bd",
        "be",
        "bf",
        "cd",
        "ce",
        "cf",
    ]
    assert letterCombinations("") == []
    assert letterCombinations("2") == ["a", "b", "c"]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert letterCombinations("23") == [
    "ad",
    "ae",
    "af",
    "bd",
    "be",
    "bf",
    "cd",
    "ce",
    "cf",
]
assert letterCombinations("") == []
assert letterCombinations("2") == ["a", "b", "c"]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

设长度为 $n$，每位最多 $4$ 叉。时间 $O(4^n\cdot n)$，乘 $n$ 是因为收答案时要拷贝；空间是 $O(n)$ 的递归栈，另加输出。

## Edge Cases

空串必须特判返回 `[]`，不判的话 `dfs(0)` 会在 $i=0=n$ 时收一条空串。只有一个数字时，答案就是该键的 $3$ 或 $4$ 个字母，递归一层就停。含 `'7'` 或 `'9'` 时那一位有四个字母，是 $4$ 叉，所以复杂度上界按 $4^n$ 估。

## 追问

**输入里有 `'0'` / `'1'` 怎么办？**
先问清题意，再决定是拒绝还是跳过。标准九键这两个键没有字母，映射写成空串的话，该位 `for ch in ""` 一次都不进，整棵树被剪掉，答案变成 `[]`。如果产品约定 `'0'` 映射空格、`'1'` 没有字母，只改映射表，回溯骨架不用动。

```python
MP0 = {**MP, "0": " ", "1": ""}


def letterCombinationsWith01(digits):
    if not digits:
        return []
    ans, path = [], []

    def dfs(i):
        if i == len(digits):
            ans.append("".join(path))
            return
        for ch in MP0[digits[i]]:
            path.append(ch)
            dfs(i + 1)
            path.pop()

    dfs(0)
    return ans
```

**只要组合个数、不要字符串呢？**
那就不用回溯，把每位的字母数乘起来。空串约定个数为 $0$，别算成 $1$；含无字母的键，乘积就是 $0$。

```python
def letterCombinationsCount(digits):
    if not digits:
        return 0
    sizes = {"2": 3, "3": 3, "4": 3, "5": 3, "6": 3, "7": 4, "8": 3, "9": 4}
    ans = 1
    for d in digits:
        if d not in sizes:
            return 0
        ans *= sizes[d]
    return ans
```
