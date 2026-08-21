---
id: lc-22-generate-parentheses
section: backtracking
order: 6
level: S
title: LC 22 · 括号生成
quick: >-
  生成 $n$ 对合法括号。回溯约束：`open < n` 才能加
  `(`；`close < open` 才能加 `)`。长度到 $2n$ 收答案。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 22. 括号生成
    url: https://leetcode.cn/problems/generate-parentheses/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定 $n$，生成所有由 $n$ 对括号组成的合法括号串。合法：任意前缀中左括号不少于右括号，且总数各 $n$。

## 思路

回溯两个计数器。还能放左括号就放（`open < n`）；右括号只有少于已放左括号时才放（`close < open`），否则前缀非法。长度 $2n$ 时必合法。

不要先生成再过滤。卡特兰数 $C_n$ 就是方案数。面试先讲两条约束，再写递归。

## 参考代码

```python
from typing import List


def generateParenthesis(n: int) -> List[str]:
    ans = []

    def dfs(s: str, open_n: int, close_n: int) -> None:
        if len(s) == 2 * n:
            ans.append(s)
            return
        if open_n < n:
            dfs(s + "(", open_n + 1, close_n)
        if close_n < open_n:
            dfs(s + ")", open_n, close_n + 1)

    dfs("", 0, 0)
    return ans


if __name__ == "__main__":
    assert generateParenthesis(3) == [
        "((()))",
        "(()())",
        "(())()",
        "()(())",
        "()()()",
    ]
    assert generateParenthesis(1) == ["()"]
    print("ok")
```

## 复杂度

方案数为第 $n$ 个卡特兰数 $C_n=\frac{1}{n+1}\binom{2n}{n}$。时间 $O(C_n\cdot n)$，空间 $O(n)$ 加输出。

## 边界

- $n=1$：只有 `"()"`。
- $n=2$：只有 `"(())"` 与 `"()()"`，没有 `")(()"` 这类前缀非法串。
- $n=0$：按题意通常不出现；若出现，卡特兰 $C_0=1$，对应空串。

## 追问

- **只求合法括号串的个数？** 不必枚举。第 $n$ 个卡特兰数 $C_n=\dfrac{1}{n+1}\binom{2n}{n}$，递推 $C_0=1$，

$$
C_i=\sum_{j=0}^{i-1} C_j\,C_{i-1-j}.
$$

含义：最外层一对 `()` 里塞 $j$ 对，右边再拼 $i-1-j$ 对。时间 $O(n^2)$。

```python
def numParenthesis(n):
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        dp[i] = sum(dp[j] * dp[i - 1 - j] for j in range(i))
    return dp[n]
```

- **判断一条括号串是否合法？** 扫一遍维护余额 `bal`：遇 `(` 加一，遇 `)` 减一；过程中 `bal \lt 0` 则前缀右括号过多，结束时 `bal=0` 才合法。也可用栈。多种括号（`()` `[]` `{}`）见 LC 20，独立卡 `lc-20-valid-parentheses`。

```python
def isValidParens(s):
    bal = 0
    for ch in s:
        bal += 1 if ch == "(" else -1
        if bal < 0:
            return False
    return bal == 0
```
