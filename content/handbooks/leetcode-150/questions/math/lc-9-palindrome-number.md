---
id: lc-9-palindrome-number
section: math
order: 1
level: A
title: LC 9 · 回文数
quick: >-
  负数和以 $0$ 结尾的非零数直接判否。不转字符串，就反转后半段数字和前半段比，偶数位比 `x == rev`，奇数位丢掉中间位比 `x == rev //
  10`。
tags:
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 9. 回文数
    url: 'https://leetcode.cn/problems/palindrome-number/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个整数 x，判断其十进制表示是否正向读取和反向读取完全相同。十进制表示包含负号，因此负数不被视为回文；不允许为了凑回文而补前导零。

### 输入与输出

实现 `isPalindrome(x: int) -> bool`，回文返回 `True`，否则返回 `False`。输入是整数，不是字符串。

### 约束

- `-2^31 <= x <= 2^31-1`。
- 进阶要求不把输入转换为字符串。

### 示例

```text
输入：x = 121
输出：true
```

121 从两边读取都是 121；10 反向是 01，与原十进制表示不同。

## 解题思路与参考答案

## 题意

判断整数 `x` 是不是回文，也就是正着读和反着读一样。进阶要求不转成字符串。

## 思路

我反转一半数字来比，这样不用转字符串，也避开了整段反转的溢出。先排除两种情况，负数带符号，不是回文；末位是 $0$ 而自身不是 $0$，反转会丢掉前导零，也不是。

然后 `rev` 从右往左拼数字，`x` 不断去掉末位，直到 `x <= rev`。拿 $12321$ 走一遍，`rev` 依次变成 1、12、123，`x` 依次变成 1232、123、12。这时 `x=12`、`rev=123`，奇数位的中间那位落在 `rev` 里，整除 $10$ 丢掉后比较 `x == rev // 10`，成立，是回文。偶数位的数停下来时两半直接相等，比 `x == rev` 就行。

转成字符串用双指针也能过；题目要求不转字符串时，就用一半反转。

## 参考代码

```python
def isPalindrome(x: int) -> bool:
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    rev = 0
    while x > rev:
        rev = rev * 10 + x % 10
        x //= 10
    return x == rev or x == rev // 10


if __name__ == "__main__":
    assert isPalindrome(121) is True
    assert isPalindrome(-121) is False
    assert isPalindrome(10) is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isPalindrome(121) is True
assert isPalindrome(-121) is False
assert isPalindrome(10) is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log_{10} x)$（位数），额外空间 $O(1)$。

## Edge Cases

- $x=0$ 是回文。
- $x=10$ 末尾是 $0$ 且自身不为 $0$，反转会丢前导零，直接判否。

## 追问

**转字符串怎么写？**
`s=str(x)`，左右指针对撞，或者直接 `s == s[::-1]`。能过，但不满足「不转字符串」的进阶要求。负数的 `str` 带 `-`，自然判否。需要满足进阶要求时，改用一半反转。

```python
def isPalindromeStr(x):
    s = str(x)
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True
```

**为什么不整段反转？**
整段反转再和原值比也能做，但 32 位里反转可能溢出，比如较大的回文候选。只反转一半，循环条件是 `x > rev`，溢出空间减半，也顺带处理了奇数位的中间位。Python 不溢出，面试仍要主动提。

```python
def isPalindromeFullRev(x):
    if x < 0:
        return False
    orig, rev = x, 0
    while x:
        rev = rev * 10 + x % 10
        x //= 10
    return orig == rev
```
