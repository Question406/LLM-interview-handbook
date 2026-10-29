---
id: lc-20-valid-parentheses
section: stack
order: 1
level: S
title: LC 20 · 有效的括号
quick: 括号后开先关，用栈：左括号入栈，右括号必须和栈顶配成一对才弹出，配不上就无效。扫完栈为空才有效。时间 $O(n)$。
tags:
  - Stack
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 20. 有效的括号
    url: 'https://leetcode.cn/problems/valid-parentheses/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个只包含圆括号、方括号和花括号的字符串，判断所有括号能否正确匹配。每个右括号必须与此前尚未匹配的同类型左括号组成一对，匹配顺序必须保持合法嵌套；最后不能剩下未匹配的括号。

### 输入与输出

实现 `isValid(s: str) -> bool`。完全匹配返回 `True`，否则返回 `False`。例如 `([])` 合法，而 `([)]` 虽然每种括号数量相同，交叉的配对仍不合法。

### 约束

- `1 <= len(s) <= 10^4`。
- 字符仅为 `(`、`)`、`[`、`]`、`{`、`}`。

### 示例

```text
输入：s = "()"
输出：true
```

## 解题思路与参考答案

## 题意

字符串只含 `()`、`[]`、`{}`。判断括号是否匹配：类型对应、顺序嵌套正确。

## 思路

括号是后开的先关，所以用栈。遇到左括号入栈；遇到右括号时，如果栈空或者栈顶对不上就返回假，对上了就弹出。扫完以后栈必须为空，否则还有没闭合的左括号。

拿 `([)]` 看。`(`、`[` 依次入栈，遇到 `)` 时，最近一个没配对的左括号是 `[`，类型对不上，直接无效。`{[]}` 是先关里面再关外面，栈一路对得上，合法。

写的时候用一个 `右 -> 左` 的映射，能少写一堆分支。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isValid("()") is True
assert isValid("()[]{}") is True
assert isValid("(]") is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。每个字符进出栈至多一次。

## Edge Cases

空串栈是空的，返回真。

只有右括号时，栈空还要弹，立刻返回假。只有左括号时，扫完栈不空，也是假。

长度为奇数一定配不完，按栈模拟自然会返回假，不用先单独判奇偶。

## 追问

**最长有效括号（LC 32）怎么做？**
栈里改放下标，先压一个 $-1$ 当哨兵。遇到 `(` 压下标；遇到 `)` 先弹，弹完栈空就把当前下标当新哨兵，说明这段已经断了；不空就用 $i - st[-1]$ 更新最长。哨兵是「最后一个未匹配右括号」的位置，有效段长度就是当前位置到它的距离，时间 $O(n)$。也可以 DP：`dp[i]` 是以 $i$ 结尾的最长有效长度，`()` 贡献 $dp[i-2]+2$，`))` 且前面能配上就再累加更早的 `dp`。只数左右括号的个数判不了交错。

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

**生成所有合法括号串（LC 22）呢？**
那是构造题，用回溯加两个计数器。还能放左括号就放（$open \lt n$）；右括号只在少于已放的左括号时才放（$close \lt open$）。长度到 $2n$ 时一定合法，方案数是卡特兰数。别先生成全部再拿这题过滤。独立卡见 `lc-22-generate-parentheses`。

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
