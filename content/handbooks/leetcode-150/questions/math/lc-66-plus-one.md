---
id: lc-66-plus-one
section: math
order: 2
level: A
title: LC 66 · 加一
quick: 从最低位往高位走，不到 $9$ 就加一返回，是 $9$ 就置 $0$ 继续进位；全是 $9$ 时在最前面补一个 $1$。时间 $O(n)$。
tags:
  - Array
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 66. 加一
    url: 'https://leetcode.cn/problems/plus-one/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

一个非负整数用十进制数字数组表示，最高位在前，每个元素存一位。给这个整数加 1，返回结果的数字数组。结果可能比输入多一位，不能假定整个整数能放进固定宽度整数类型。

### 输入与输出

实现 `plusOne(digits) -> list[int]`。返回加一后的十进制数字序列，仍按高位到低位排列，不带多余前导零。

### 约束与约定

- `1 <= len(digits) <= 100`。
- 每位为 0 到 9，输入没有多余前导零。

### 示例

```text
输入：digits = [1,2,3]
输出：[1,2,4]
```

[1,2,3] 表示 123，加一后返回 [1,2,4]。

[官方原题与完整题面](https://leetcode.com/problems/plus-one/description/)。

## 解题思路与参考答案

## 题意

`digits` 从高位到低位表示一个非负整数，每个元素是一位数字，返回加一之后的数组。

## 思路

我从右往左模拟进位，大多数情况只改最后一位就能返回。当前位小于 $9$，加一直接返回，前面不用动；当前位是 $9$，写成 $0$，进位继续往左。

拿 `[1, 2, 3]` 和 `[9]` 对比一下。`[1, 2, 3]` 末位 3 加一就返回 `[1, 2, 4]`；`[9]` 的 9 变成 0 之后已经到头了，说明全是 $9$，在前面补一个 1，得到 `[1, 0]`。

一路进位到头，就说明全是 $9$，结果长度加一，最高位为 $1$，其余为 $0$。别先转成整数再加，位数可以很长。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert plusOne([1, 2, 3]) == [1, 2, 4]
assert plusOne([4, 3, 2, 1]) == [4, 3, 2, 2]
assert plusOne([9]) == [1, 0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间最坏 $O(n)$（全 $9$ 时新开数组）。没有进位到头时，额外空间是 $O(1)$。

## Edge Cases

- `[0]` 得到 `[1]`。
- `[9,9,9]` 一路进位，返回 `[1,0,0,0]`。
- 最低位不是 $9$ 时，只改最后一位就返回，前面不动。

## 追问

**位数很大怎么办？**
照样按位进位，最坏扫一遍就行。别写 `int(''.join(map(str, digits)))+1`，位数可以到题目上限，有的语言会溢出，还多一次 $O(n)$ 的字符串开销。

**同一个整数用链表表示呢？**
头结点是高位时，用递归（或栈）从最右边往回传进位，全 $9$ 时在最前面补一个 $1$。LC 369 就是加一的链表版。加一个哨兵结点，就不用单独处理多出来的那一位。

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
