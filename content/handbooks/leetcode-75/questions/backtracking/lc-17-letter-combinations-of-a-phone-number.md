---
id: lc-17-letter-combinations-of-a-phone-number
section: backtracking
order: 1
level: A
title: LC 17 · 电话号码的字母组合
quick: >-
  数字到字母写死一张映射表，然后回溯：第 $i$ 位枚举该键的每个字母，拼到和 `digits` 一样长就收一条，空串返回空列表。时间 $O(4^n\cdot
  n)$，额外空间 $O(n)$（不计输出）。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 17. Letter Combinations of a Phone Number
    url: 'https://leetcode.com/problems/letter-combinations-of-a-phone-number/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定一个由数字 2 到 9 组成的字符串，按手机按键的字母映射生成全部可能的字母组合。映射为：2 对应 abc，3 对应 def，4 对应 ghi，5 对应 jkl，6 对应 mno，7 对应 pqrs，8 对应 tuv，9 对应 wxyz。每一位数字选一个对应字母，选出的字母保持数字的原顺序。

### 输入与输出

实现 `letterCombinations(digits: str) -> List[str]`。每个输出字符串长度与 digits 相同，返回顺序不限。

### 约束

- 官方当前题面给定 `1 <= len(digits) <= 4`，每位在 2 到 9。
- 本手册另外保留空字符串输入的练习约定：digits 为空时返回 `[]`。

### 示例

```text
输入：digits = "23"
输出：["ad","ae","af","bd","be","bf","cd","ce","cf"]
```

## 解题思路与参考答案

## 题意

数字串 `digits`，每位是 `'2'` 到 `'9'`，长度 $0\le n\le 4$。按手机九键映射成字母，返回所有可能的字母组合，顺序任意。`digits` 为空则返回空列表。

## 思路

这是标准回溯，答案就是一棵按位分叉的树的所有叶子。下标 $i$ 对应第 $i$ 个数字，枚举它映射的每个字母追加到路径，递归 $i+1$，回来再弹出。$i$ 走到 $n$ 就把路径拼成字符串收进答案。每层分叉 $3$ 或 $4$，叶子数就是答案数。

拿 `"23"` 走一遍：第一层从 `abc` 里选一个，比如 `a`，第二层从 `def` 里选，得到 `ad`、`ae`、`af`；回到第一层换成 `b`、`c` 再来一遍，一共 9 条。

空输入要特判，否则 $i=0=n$ 时会收一条空串。

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
    ans: List[str] = []
    path: List[str] = []

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
    assert sorted(letterCombinations("23")) == sorted(
        ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
    )
    assert letterCombinations("") == []
    assert sorted(letterCombinations("2")) == ["a", "b", "c"]
    assert len(letterCombinations("79")) == 16
    assert len(letterCombinations("2345")) == 81
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert sorted(letterCombinations("23")) == sorted(
    ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
)
assert letterCombinations("") == []
assert sorted(letterCombinations("2")) == ["a", "b", "c"]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

设长度为 $n$，每位最多 $4$ 叉。时间 $O(4^n\cdot n)$，其中 $n$ 来自每条答案的拼接；额外空间 $O(n)$，是递归栈和路径，输出另计。

## Edge Cases

- 空串必须特判返回 `[]`，不判会收一条 `""`。
- 单个数字时，答案就是该键的 $3$ 或 $4$ 个字母。
- 含 `'7'` / `'9'` 时该位 $4$ 叉，复杂度上界按 $4^n$ 估。

## 追问

**不用递归怎么写？**
按位滚动。`res` 初始为 `[""]`，每读一位，就把 `res` 里每个前缀接上该键的每个字母，和回溯是同一棵树。结果相同，时间同阶，但中间层要整层存下，空间是最后一层的大小。

```python
def letterCombinationsIter(digits):
    if not digits:
        return []
    res = [""]
    for d in digits:
        res = [p + ch for p in res for ch in MP[d]]
    return res
```

**只要组合个数呢？**
不用枚举，把每位的字母数相乘就行。空串按题意是 $0$，别算成 $1$。
