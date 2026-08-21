---
id: lc-67-add-binary
section: bit
order: 1
level: A
title: LC 67 · 二进制求和
quick: >-
  从低位往高位加，维护进位。当前位是
  `carry & 1`，进位 `carry >>= 1`。不要先转整数，串可能很长。
tags:
  - Bit
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 67. 二进制求和
    url: https://leetcode.cn/problems/add-binary/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

二进制字符串 `a`、`b`（无前导零，除非就是 `"0"`），返回它们的和，仍是二进制字符串。

## 思路

模拟竖式。从尾部往前，缺位当 $0$，累加到 `carry`。这一位输出 `carry % 2`，进位变成 `carry // 2`。最后若还有进位，补一个 `"1"`。

Python 的 `int(a, 2) + int(b, 2)` 能过，但面试要看你写进位，也避免超长串转整数的争议。

## 参考代码

```python
def addBinary(a: str, b: str) -> str:
    i, j, carry = len(a) - 1, len(b) - 1, 0
    out = []
    while i >= 0 or j >= 0 or carry:
        if i >= 0:
            carry += int(a[i])
            i -= 1
        if j >= 0:
            carry += int(b[j])
            j -= 1
        out.append(str(carry & 1))
        carry >>= 1
    return "".join(reversed(out))


if __name__ == "__main__":
    assert addBinary("11", "1") == "100"
    assert addBinary("1010", "1011") == "10101"
    assert addBinary("0", "0") == "0"
    print("ok")
```

## 复杂度

时间 $O(\max(|a|,|b|))$，额外空间同阶（输出）。

## 边界

- 一侧为 `"0"`：缺位当 $0$，结果等于另一串（题保证无额外前导零）。
- `"1"+"1"`：循环结束后仍有进位，补出多一位，结果 `"10"`。
- 长度差很大：短的那侧指针先耗尽，之后只加另一侧和进位。

## 追问

- **十进制字符串相加（LC 415）？** 同一套从低到高进位，只是当前位 `carry % 10`、进位 `carry // 10`。字符转数字用 `ord(c)-48`。不要先转 `int`：串可以很长。

```python
def addStrings(num1, num2):
    i, j, carry = len(num1) - 1, len(num2) - 1, 0
    out = []
    while i >= 0 or j >= 0 or carry:
        if i >= 0:
            carry += ord(num1[i]) - 48
            i -= 1
        if j >= 0:
            carry += ord(num2[j]) - 48
            j -= 1
        out.append(str(carry % 10))
        carry //= 10
    return "".join(reversed(out))
```

- **链表存的二进制相加？** 链表头通常是高位。先反转两条链（或不改原链则压栈）变成低位在前，再按本题进位接新结点，最后把结果链反转回来。

```python
def addTwoBinaryLists(l1, l2):
    def rev(h):
        pre = None
        while h:
            h.next, pre, h = pre, h, h.next
        return pre
    a, b = rev(l1), rev(l2)
    dummy = ListNode(0)
    tail, carry = dummy, 0
    while a or b or carry:
        if a:
            carry += a.val
            a = a.next
        if b:
            carry += b.val
            b = b.next
        tail.next = ListNode(carry & 1)
        tail = tail.next
        carry >>= 1
    return rev(dummy.next)
```
