---
id: lc-20-valid-parentheses
section: stack
order: 1
level: S
title: LC 20 · 有效的括号
quick: >-
  左括号入栈，右括号必须与栈顶成对再弹出。扫完栈空才有效。时间
  $O(n)$。
tags:
  - Stack
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 20. 有效的括号
    url: https://leetcode.cn/problems/valid-parentheses/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

字符串只含 `()`、`[]`、`{}`。判断括号是否匹配：类型对应、顺序嵌套正确。

## 思路

栈。遇左括号入栈；遇右括号时栈空或栈顶对不上则假，对上则弹出。结束时栈必须空，否则有未闭合的左括号。

`([)]` 类型交错，栈顶是 `(` 对不上 `]`。`{[]}` 先内后外，合法。用映射 `右 -> 左` 少写一堆分支。

## 参考代码

```python
def isValid(s: str) -> bool:
    mp = {")": "(", "]": "[", "}": "{"}
    st = []
    for ch in s:
        if ch in mp:
            if not st or st[-1] != mp[ch]:
                return False
            st.pop()
        else:
            st.append(ch)
    return not st


if __name__ == "__main__":
    assert isValid("()") is True
    assert isValid("()[]{}") is True
    assert isValid("(]") is False
    assert isValid("([)]") is False
    assert isValid("{[]}") is True
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。每个字符进出栈至多一次。

## 边界

- 空串：栈空，返回真。
- 只有右括号：栈空却要弹，立即假。
- 只有左括号：扫完栈非空，假。
- 长度为奇数：不可能配对完，必假（仍按栈模拟即可，不必先判奇偶）。
- `([)]` 类型交错：栈顶对不上。

## 追问

- **最长有效括号（LC 32）？** 栈里放下标，先压 $-1$ 当哨兵。遇 `(` 压下标；遇 `)` 先弹，若栈空则把当前下标当新哨兵（这段已经坏了），否则用 $i - st[-1]$ 更新最长。哨兵是「最后一个未匹配右括号」的位置，有效段长度是当前与它的距离。时间 $O(n)$。DP 也可：`dp[i]` 为以 $i$ 结尾的最长有效长，`()` 贡献 $dp[i-2]+2$，`))` 且前面能配上则再累加更早的 `dp`。不要只计数左右括号个数，那判不了交错。

```python
def longestValidParentheses(s):
    st, best = [-1], 0
    for i, ch in enumerate(s):
        if ch == "(":
            st.append(i)
        else:
            st.pop()
            if not st:
                st.append(i)
            else:
                best = max(best, i - st[-1])
    return best
```

- **生成所有合法括号串（LC 22）？** 这是构造不是判定。回溯两个计数器：还能放左括号就放（$open \lt n$）；右括号只有少于已放左括号时才放（$close \lt open$）。长度 $2n$ 时必合法。方案数是卡特兰数。不要先生成全部再拿本题过滤。独立卡见 `lc-22-generate-parentheses`。

```python
def generateParenthesis(n):
    ans = []

    def dfs(s, open_n, close_n):
        if len(s) == 2 * n:
            ans.append(s)
            return
        if open_n < n:
            dfs(s + "(", open_n + 1, close_n)
        if close_n < open_n:
            dfs(s + ")", open_n, close_n + 1)

    dfs("", 0, 0)
    return ans
```
