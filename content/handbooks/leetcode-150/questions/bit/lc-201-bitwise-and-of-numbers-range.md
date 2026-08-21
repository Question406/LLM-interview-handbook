---
id: lc-201-bitwise-and-of-numbers-range
section: bit
order: 6
level: A
title: LC 201 · 数字范围按位与
quick: >-
  $[left,right]$ 的按位与等于公共前缀。不断 `right &= right - 1` 清掉 `right` 最低的
  $1$，直到 `right <= left`。时间 $O(\log right)$。
tags:
  - Bit
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 201. 数字范围按位与
    url: https://leetcode.cn/problems/bitwise-and-of-numbers-range/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

求闭区间 $[left, right]$ 内所有整数的按位与。

## 思路

区间一旦跨过某个比特从 $0$ 变 $1$，该比特的与就是 $0$。结果只能是 `left` 与 `right` 的公共二进制前缀，后面补零。

实现：`right` 反复 `&= right - 1`（去掉最低的 $1$），直到 `right <= left`。这时 `right` 就是公共前缀。两数一起右移直到相等、再左移回来，效果相同。

不要循环 $right-left$ 次去与，区间可达 $2^{31}$。

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

## 复杂度

时间 $O(\log right)$，每次至少清掉一个 $1$。额外空间 $O(1)$。

## 边界

- `left == right`：区间只有一个数，答案就是它，循环不进。
- `left=0`：只要 `right\gt 0` 就会与到 $0$。
- 跨过 $2^k$：公共前缀被清空，结果常为 $0$，如 $[1, 2^{31}-1]$。

## 追问

- **按位或？** 公共前缀保留；最高不同位及其右边，区间内一定能取到 $1$，或的结果是这些位全变成 $1$。两数一起右移直到相等，再左移回来并在低位填满 $1$。

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

- **数组而非连续区间？** 没有「清最低 $1$」的单调性，不能靠公共前缀。把所有数与一遍，中途变成 $0$ 可提前停。时间 $O(n)$。

```python
def arrayBitwiseAnd(nums):
    ans = nums[0]
    for x in nums[1:]:
        ans &= x
        if ans == 0:
            break
    return ans
```
