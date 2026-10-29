---
id: lc-283-move-zeroes
section: two-pointers
order: 1
level: S
title: LC 283 · 移动零
quick: >-
  用一个写指针 `w` 指向下一个非零数该放的位置，读指针遇到非零就和 `w` 交换，`w` 前移。这样非零数的相对顺序不变，零被挤到末尾。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 283. Move Zeroes
    url: 'https://leetcode.com/problems/move-zeroes/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定一个整数数组，把所有值为 0 的元素移到数组末尾，同时保持其他非零元素原来的相对顺序。必须直接修改输入数组，不能创建另一个数组作为重排结果。

### 输入与输出

实现 `moveZeroes(nums: List[int]) -> None`。函数没有结果数组返回值，调用后的 nums 就是答案；数组长度和每个值的出现次数都保持不变。

### 约束

- `1 <= len(nums) <= 10^4`。
- 元素位于 32 位有符号整数范围内，非零元素可以为负数。

### 示例

```text
输入：nums = [0,1,0,3,12]
输出：[1,3,12,0,0]
```

原数组中非零元素依次为 1、3、12，移动后仍按这个顺序排列，两个零放在末尾。

## 解题思路与参考答案

## 题意

原地把数组里所有 $0$ 移到末尾，非零元素保持原有相对顺序。不能拷贝数组，函数无返回值。长度到 $10^4$。

## 思路

我会用快慢指针原地交换，一遍扫完，$O(n)$ 时间、$O(1)$ 空间。维护的不变式是 `w` 左边全是处理好的非零数，`[w, i)` 全是 $0$。读指针 `i` 扫到非零时，和 `nums[w]` 交换，然后 `w += 1`。这次交换把一个 $0$ 换到 `i` 的位置，不变式还成立，扫完后 $0$ 就全在尾部。

拿 `[0, 1, 0, 3, 12]` 走一遍。`i=0` 是 $0$，跳过；`i=1` 是 $1$，和 `nums[0]` 交换，数组变成 `[1, 0, 0, 3, 12]`，`w=1`；`i=2` 是 $0$，跳过；`i=3` 是 $3$，和 `nums[1]` 交换得到 `[1, 3, 0, 0, 12]`，`w=2`；`i=4` 是 $12$，和 `nums[2]` 交换，最后是 `[1, 3, 12, 0, 0]`。

另一种写法是先把非零数依次覆盖到前面，最后把 `[w, n)` 填 $0$，写操作次数差不多。每遇到一个 $0$ 就把后面整体左移是 $O(n^2)$，面试官会追问。

## 参考代码

```python
from typing import List


def moveZeroes(nums: List[int]) -> None:
    w = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[w], nums[i] = nums[i], nums[w]
            w += 1


if __name__ == "__main__":

    def run(a):
        moveZeroes(a)
        return a

    assert run([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]
    assert run([0]) == [0]
    assert run([1, 2, 3]) == [1, 2, 3]
    assert run([0, 0, 1]) == [1, 0, 0]
    assert run([4, 0, -2, 0, 0, 5]) == [4, -2, 5, 0, 0, 0]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
def run(a):
    moveZeroes(a)
    return a


assert run([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]
assert run([0]) == [0]
assert run([1, 2, 3]) == [1, 2, 3]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

没有 $0$ 时，每次都是 `w == i` 的自交换，数组不变。

全是 $0$ 时，`w` 一直停在 $0$，不做任何交换。

负数也是非零，判断要写 `!= 0`，写成 `> 0` 会把负数当成零处理。

## 追问

**能不能尽量减少写操作？**
能，`w == i` 时跳过交换，前缀全是非零的数组就一次都不用写。总写次数不超过非零个数的两倍。

```python
def moveZeroes_fewer_writes(nums):
    w = 0
    for i, x in enumerate(nums):
        if x != 0:
            if i != w:
                nums[w], nums[i] = x, 0
            w += 1
```

**换成「移除等于 `val` 的元素并返回新长度」（LC 27）怎么写？**
套同一个写指针模板，不等于 `val` 就写到 `w`，最后返回 `w`。题目不要求保留尾部内容，所以直接覆盖就行，不用交换。
