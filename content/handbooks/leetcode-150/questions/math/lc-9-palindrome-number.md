---
id: lc-9-palindrome-number
section: math
order: 1
level: A
title: LC 9 · 回文数
quick: >-
  负数与「以 $0$ 结尾的非零数」直接否。不转字符串：反转后半段数字，与前半比较。偶数位
  `x == rev`，奇数位丢掉中间位 `x == rev // 10`。
tags:
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 9. 回文数
    url: https://leetcode.cn/problems/palindrome-number/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断整数 `x` 是否回文：正着读与反着读相同。进阶：不要转成字符串。

## 思路

负数带符号，不是回文。末位为 $0$ 且自身不是 $0$，反转会丢前导零，也不是。

不转字符串就反转**一半**。`rev` 从右往左拼数字，`x` 不断去掉末位，直到 `x <= rev`。偶数位两半相等；奇数位中间那位在 `rev` 里，整除 $10$ 丢掉再比。只反转一半，也避开整段反转的溢出。

转字符串再对撞指针能过，面试先承认，再写一半反转。

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

## 复杂度

时间 $O(\log_{10} x)$（位数），额外空间 $O(1)$。

## 边界

- $x=0$：是回文。
- $x=10$：末尾 $0$ 且自身非 $0$，反转会丢前导零，直接否。
- 奇数位如 $12321$：循环后 `x=12`、`rev=123`，比较 `x == rev // 10`，丢掉中间位。

## 追问

- **转字符串？** `s=str(x)`，左右指针对撞或 `s == s[::-1]`。能过，但不满足「不转字符串」进阶。负数 `str` 带 `-`，直接否。面试先承认这写法，再写一半反转。

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

- **整段反转？** 把整个 $x$ 反转再与原值比较。32 位里反转可能溢出（如较大的回文候选）。只反转一半：循环条件 `x > rev`，溢出空间减半，也自然处理奇数中间位。Python 不溢出，面试仍要主动提。

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
