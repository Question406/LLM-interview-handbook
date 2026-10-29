---
id: lc-22-generate-parentheses
section: backtracking
order: 6
level: S
title: LC 22 · 括号生成
quick: >-
  用回溯，带两个计数器。`open < n` 时可以加 `(`，`close < open` 时才能加 `)`，这样任何前缀都合法，长度到 $2n$
  直接收答案。方案数是卡特兰数 $C_n$。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 22. 括号生成
    url: 'https://leetcode.cn/problems/generate-parentheses/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定正整数 n，列出恰好使用 n 对圆括号构成的所有合法括号字符串。合法表示每个右括号都能与前面尚未匹配的左括号配对，且最后没有剩余括号。

### 输入与输出

实现 `generateParenthesis(n) -> list[str]`。每个结果长度为 `2*n`，左、右括号各 n 个。结果不得重复，返回列表的顺序不限。

### 约束与约定

- `1 <= n <= 8`。

### 示例

```text
输入：n = 3
输出：["((()))","(()())","(())()","()(())","()()()"]
```

n=3 时共有示例列出的五个合法字符串，任何一个非法括号串都不能包含在结果中。

[官方原题与完整题面](https://leetcode.com/problems/generate-parentheses/description/)。

## 解题思路与参考答案

## 题意

给定 $n$，生成所有由 $n$ 对括号组成的合法括号串。合法指任意前缀中左括号不少于右括号，且总数各 $n$。

## 思路

我会直接回溯生成合法串，不先生成全部再过滤。两条约束先说清楚：还能放左括号就放，条件是 `open < n`；右括号只有在少于已放左括号时才能放，也就是 `close < open`，否则前缀就非法了。两条都守住，长度到 $2n$ 时串一定合法。

拿 $n=2$ 看。开头只能放 `(`；第二位可以再放 `(`，之后只能补两个 `)`，得到 `(())`；也可以放 `)`，接着又只能先放 `(`，得到 `()()`。以 `)` 开头的串在第一步就被 `close < open` 挡掉了。方案总数就是卡特兰数 $C_n$。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert generateParenthesis(3) == [
    "((()))",
    "(()())",
    "(())()",
    "()(())",
    "()()()",
]
assert generateParenthesis(1) == ["()"]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

方案数为第 $n$ 个卡特兰数 $C_n=\frac{1}{n+1}\binom{2n}{n}$。时间 $O(C_n\cdot n)$，空间 $O(n)$ 加输出。

## Edge Cases

$n=1$ 时只有 `"()"`。$n=2$ 时只有 `"(())"` 与 `"()()"`，`")(()"` 这类前缀非法的串不会出现。$n=0$ 按题意通常不出现；真出现的话，卡特兰 $C_0=1$，对应空串。

## 追问

**只求合法括号串的个数呢？**
不用枚举，答案是第 $n$ 个卡特兰数 $C_n=\dfrac{1}{n+1}\binom{2n}{n}$。也可以用递推，$C_0=1$，

$$
C_i=\sum_{j=0}^{i-1} C_j\,C_{i-1-j}.
$$

意思是最外层一对 `()` 里塞 $j$ 对，右边再拼 $i-1-j$ 对。这样算时间 $O(n^2)$。

```python
def numParenthesis(n):
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        dp[i] = sum(dp[j] * dp[i - 1 - j] for j in range(i))
    return dp[n]
```

**怎么判断一条括号串是否合法？**
扫一遍维护余额 `bal`，遇 `(` 加一，遇 `)` 减一。过程中 `bal \lt 0` 说明前缀右括号过多，结束时 `bal=0` 才合法。用栈也行。多种括号（`()` `[]` `{}`）是 LC 20，独立卡 `lc-20-valid-parentheses`。

```python
def isValidParens(s):
    bal = 0
    for ch in s:
        bal += 1 if ch == "(" else -1
        if bal < 0:
            return False
    return bal == 0
```
