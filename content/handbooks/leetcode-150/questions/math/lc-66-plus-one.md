---
id: lc-66-plus-one
section: math
order: 2
level: A
title: LC 66 · 加一
quick: >-
  从最低位往高位走：不到 $9$ 就加一返回；是 $9$ 则置 $0$ 继续进位。全是 $9$ 时在最前面补一个
  $1$。时间 $O(n)$。
tags:
  - Array
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 66. 加一
    url: https://leetcode.cn/problems/plus-one/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`digits` 按高位到低位表示一个非负整数，每个元素是一位数字。返回加一后的数组。

## 思路

从右往左模拟进位。当前位小于 $9$，加一即可返回，后面不用动。当前位是 $9$，写成 $0$，进位继续往左。

若一路进到头，说明全是 $9$，结果长度加一，最高位为 $1$，其余为 $0$。不要先转成整数再加：位数可以很长。

## 参考代码

```python
from typing import List


def plusOne(digits: List[int]) -> List[int]:
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    return [1] + digits


if __name__ == "__main__":
    assert plusOne([1, 2, 3]) == [1, 2, 4]
    assert plusOne([4, 3, 2, 1]) == [4, 3, 2, 2]
    assert plusOne([9]) == [1, 0]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间最坏 $O(n)$（全 $9$ 时新开数组）。无进位则 $O(1)$ 额外空间。

## 边界

- `[0]` 得 `[1]`。
- `[9,9,9]` 一路进位，返回 `[1,0,0,0]`。
- 最低位不是 $9$：只改最后一位就返回，前面不动。

## 追问

- **很大位数？** 禁止 `int(''.join(map(str, digits)))+1`：位数可达题目上限，有的语言溢出，也多一次 $O(n)$ 字符串开销。按位进位即可，最坏扫一遍。

- **链表表示同一整数？** 头结点是高位时，用递归（或栈）从最右往回传进位；全 $9$ 时在最前面补一个 $1$。LC 369 就是加一的链表版。哨兵结点避免单独处理「多出一位」。

```python
def plusOneList(head):
    dummy = ListNode(0, head)
    def rec(node):
        if not node:
            return 1
        s = node.val + rec(node.next)
        node.val = s % 10
        return s // 10
    rec(dummy)
    return dummy if dummy.val else dummy.next
```
