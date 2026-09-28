---
id: lc-17-letter-combinations-of-a-phone-number
section: backtracking
order: 1
level: A
title: LC 17 · 电话号码的字母组合
quick: >-
  数字到字母映射。回溯：第 $i$ 位枚举对应字母，拼到长度等于
  `digits`。空串返回空列表。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 17. 电话号码的字母组合
    url: https://leetcode.cn/problems/letter-combinations-of-a-phone-number/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

数字串 `digits`（`'2'` 到 `'9'`），按九键映射成字母组合，返回所有可能字符串。`digits` 为空则返回空列表。

## 思路

标准回溯：下标 $i$ 对应第 $i$ 个数字，枚举它映射的每个字母追加到路径，递归 $i+1$。$i$ 走到头就收一条。映射表写死即可。

空输入要特判，否则会收一条空串。迭代版用队列按层扩展，和回溯是同一棵树。可以画「每位分叉 3 或 4」方便讲。

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
    assert letterCombinations("23") == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
    assert letterCombinations("") == []
    assert letterCombinations("2") == ["a", "b", "c"]
    print("ok")
```

## 复杂度

设长度为 $n$，每位最多 $4$ 叉。时间 $O(4^n\cdot n)$（收答案时拷贝），空间 $O(n)$ 递归栈另加输出。

## 边界

- 空串：必须特判返回 `[]`。不判的话 `dfs(0)` 会在 $i=0=n$ 时收一条空串。
- 单数字：答案就是该键的 $3$ 或 $4$ 个字母，递归一层即停。
- 含 `'7'` / `'9'`：四个字母，该位 $4$ 叉，复杂度上界按 $4^n$ 估。

## 追问

- **输入里有 `'0'` / `'1'`？** 标准九键这两键没有字母。映射写成空串则该位 `for ch in ""` 不进，整棵树被剪掉，答案变成 `[]`。若产品约定 `'0'` 映射空格、`'1'` 无字母，只改映射表即可，回溯骨架不动。先问清题意，再决定是拒绝还是跳过。

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

- **只要组合个数、不要字符串？** 不必回溯。空串约定个数为 $0$（不是 $1$）；否则把每位字母数相乘。含无字母键则积为 $0$。

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
