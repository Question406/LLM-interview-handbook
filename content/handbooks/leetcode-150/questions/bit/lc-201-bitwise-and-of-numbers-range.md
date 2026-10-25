---
id: lc-201-bitwise-and-of-numbers-range
section: bit
order: 6
level: A
title: LC 201 · 数字范围按位与
quick: "区间 $[left,right]$ 所有数的按位与，就是 `left` 和 `right` 的公共二进制前缀后面补零。不断做 `right &= right - 1` 清掉 `right` 最低的 $1$，直到 `right <= left`。时间 $O(\\log right)$。"
tags:
  - Bit
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 201. 数字范围按位与
    url: https://leetcode.cn/problems/bitwise-and-of-numbers-range/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定两个非负整数 left 和 right，考虑闭区间 `[left,right]` 中的每一个整数。把这些整数依次做按位与，返回最终的整数结果；区间两端都包含在内。

### 接口与输出

实现 `rangeBitwiseAnd(left: int, right: int) -> int`。这是位运算的 AND，不是逻辑布尔判断，也不是只对 left 与 right 两个端点求与。

### 合法输入与约束

`0 <= left <= right <= 2^31-1`。left 与 right 可以相等，此时结果就是这个唯一整数。

### 示例

```text
输入：left = 5, right = 7
输出：4
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/bitwise-and-of-numbers-range/description/)。

## 解题思路与参考答案

## 题意

求闭区间 $[left, right]$ 内所有整数的按位与。

## 思路

区间可以大到 $2^{31}$，逐个计算按位与会耗时过长，所以我会直接求公共前缀。原因是区间只要在某一位上跨过了从 $0$ 变 $1$，这一位的与就是 $0$；能留下来的只有 `left` 和 `right` 的公共二进制前缀，后面全部补零。

实现上让 `right` 反复做 `&= right - 1`，去掉最低的 $1$，直到 `right <= left`，这时 `right` 就是公共前缀。两数一起右移到相等、再左移回来，效果相同。

拿 $[5, 7]$ 走一遍：$7$ 是 `111`，清掉最低的 $1$ 得到 `110`，也就是 $6$，还大于 $5$；再清一次得到 `100`，也就是 $4$，不再大于 $5$，答案是 $4$。$5$、$6$、$7$ 的公共前缀正是最高位那个 `1`。

## 参考代码

```python
def rangeBitwiseAnd(left: int, right: int) -> int:
    while right > left:
        right &= right - 1
    return right


if __name__ == "__main__":
    assert rangeBitwiseAnd(5, 7) == 4
    assert rangeBitwiseAnd(0, 0) == 0
    assert rangeBitwiseAnd(1, 2147483647) == 0
    assert rangeBitwiseAnd(6, 6) == 6
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert rangeBitwiseAnd(5, 7) == 4
assert rangeBitwiseAnd(0, 0) == 0
assert rangeBitwiseAnd(1, 2147483647) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每次至少清掉一个 $1$，时间 $O(\log right)$，额外空间 $O(1)$。

## 边界

`left == right` 时区间只有一个数，答案就是它，循环不进。`left=0` 时只要 `right\gt 0`，结果就会与到 $0$。区间跨过 $2^k$ 时公共前缀被清空，结果常是 $0$，比如 $[1, 2^{31}-1]$。

## 追问

**换成按位或呢？**
公共前缀照样保留；从最高的不同位往右，区间里一定能取到 $1$，所以或的结果是这些位全变成 $1$。做法是两数一起右移到相等，再左移回来，低位填满 $1$。

```python
def rangeBitwiseOr(left, right):
    if left == right:
        return left
    shift = 0
    a, b = left, right
    while a != b:
        a >>= 1
        b >>= 1
        shift += 1
    return (b << shift) | ((1 << shift) - 1)
```

**如果是数组，不是连续区间呢？**
那就没有「清最低的 $1$」这种单调性，公共前缀的结论也用不上。把所有数与一遍，中途变成 $0$ 就可以提前停，时间 $O(n)$。

```python
def arrayBitwiseAnd(nums):
    ans = nums[0]
    for x in nums[1:]:
        ans &= x
        if ans == 0:
            break
    return ans
```
