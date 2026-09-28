---
id: lc-17-letter-combinations-of-a-phone-number
section: backtracking
order: 1
level: A
title: LC 17 · 电话号码的字母组合
quick: >-
  数字到字母写死一张映射表。回溯：第 $i$ 位枚举该键的每个字母，拼到长度等于 `digits` 就收一条。空串返回空列表。时间
  $O(4^n\cdot n)$，额外空间 $O(n)$（不计输出）。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 17. Letter Combinations of a Phone Number
    url: https://leetcode.com/problems/letter-combinations-of-a-phone-number/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

数字串 `digits`，每位是 `'2'` 到 `'9'`，长度 $0\le n\le 4$。按手机九键映射成字母，返回所有可能的字母组合，顺序任意。`digits` 为空则返回空列表。

## 思路

标准回溯：下标 $i$ 对应第 $i$ 个数字，枚举它映射的每个字母追加到路径，递归 $i+1$，回来再弹出。$i$ 走到 $n$ 就把路径拼成字符串收进答案。整棵树每层分叉 $3$ 或 $4$，叶子数就是答案数。

空输入要特判，否则会在 $i=0=n$ 时收一条空串。迭代版用列表按层扩展：每读一位，把已有前缀各接上该键的字母，和回溯是同一棵树。

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

## 复杂度

设长度为 $n$，每位最多 $4$ 叉。时间 $O(4^n\cdot n)$，$n$ 来自每条答案的拼接；额外空间 $O(n)$ 递归栈与路径，输出另计。

## 边界

- 空串：必须特判返回 `[]`，不判会收一条 `""`。
- 单数字：答案就是该键的 $3$ 或 $4$ 个字母。
- 含 `'7'` / `'9'`：该位 $4$ 叉，复杂度上界按 $4^n$ 估。

## 追问

- **不用递归怎么写？** 按位滚动：`res` 初始为 `[""]`，每读一位就把 `res` 里每个前缀接上该键的每个字母。最后结果与回溯相同，时间同阶，但中间层要整层存下，空间是最后一层的大小。

```python
def letterCombinationsIter(digits):
    if not digits:
        return []
    res = [""]
    for d in digits:
        res = [p + ch for p in res for ch in MP[d]]
    return res
```

- **只要组合个数？** 不用枚举，把每位字母数相乘；空串按题意是 $0$ 而不是 $1$。
