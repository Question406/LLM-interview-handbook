---
id: lc-380-insert-delete-getrandom-o1
section: array-string
order: 12
level: A
title: LC 380 · O(1) 时间插入、删除和获取随机元素
quick: "数组存元素、哈希表存「值 $\\to$ 下标」：数组负责均匀随机抽样，哈希负责快速找到位置。删除时把末尾元素换到被删位置再 `pop`，避开从中间删除的 $O(n)$。三个操作均摊 $O(1)$。"
tags:
  - Hash
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 380. O(1) 时间插入、删除和获取随机元素
    url: https://leetcode.cn/problems/insert-delete-getrandom-o1/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

设计一个动态整数集合，支持插入、删除，以及从当前集合中等概率随机取出一个值。集合不会保存重复值，每次随机调用都必须让当前每个元素被选中的概率相同。

### 输入与输出

实现类 `RandomizedSet`：构造时为空；`insert(val)` 在值原本不存在时插入并返回 `True`，已存在则返回 `False`；`remove(val)` 在值存在时删除并返回 `True`，否则返回 `False`；`getRandom()` 返回当前集合中的一个随机整数。每个操作要求平均时间 O(1)。

### 约束

- `-2^31 <= val <= 2^31-1`。
- 三种方法合计最多调用 `2 * 10^5` 次。
- 调用 `getRandom()` 时保证集合非空。

### 示例

```text
输入：["RandomizedSet", "insert", "remove", "insert", "getRandom", "remove", "insert", "getRandom"]
[[], [1], [2], [2], [], [1], [2], []]
输出：[null, true, false, true, 2, true, false, 2]
```

操作名数组与参数数组一一对应；构造器的输出记为 `null`。第一次 getRandom 时集合为 `{1,2}`，示例中的 2 只是一个可能结果，返回 1 也合法；最后集合只剩 2。

## 解题思路与参考答案

## 题意

实现 `RandomizedSet`：`insert` / `remove` 成功返回 `true`（值已在 / 不在则失败），`getRandom` 等概率返回当前集合中任一元素。均摊 $O(1)$。

## 思路

我会用数组加哈希表，因为只靠哈希表没法 $O(1)$ 均匀随机，遍历键是 $O(n)$。数组提供按下标随机，哈希提供值到下标。插入时，值不存在就追加到数组末尾，并记下索引。删除时把数组末尾元素搬到被删的下标，更新它在哈希里的位置，再 `pop` 末尾，这样就避开了从中间 `pop` 的 $O(n)$；删的正好是末尾时直接 `pop`。

拿一个例子走一遍：插入 $1$、$2$ 后数组是 `[1, 2]`；删除 $1$ 时把末尾的 $2$ 搬到下标 $0$，哈希里改成 $2 \to 0$，再 `pop`，数组变成 `[2]`，这时 `getRandom` 只会返回 $2$。

## 参考代码

```python
import random
from typing import Dict, List


class RandomizedSet:
    def __init__(self) -> None:
        self.idx: Dict[int, int] = {}
        self.arr: List[int] = []

    def insert(self, val: int) -> bool:
        if val in self.idx:
            return False
        self.idx[val] = len(self.arr)
        self.arr.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.idx:
            return False
        i = self.idx[val]
        last = self.arr[-1]
        self.arr[i] = last
        self.idx[last] = i
        self.arr.pop()
        del self.idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.arr)


if __name__ == "__main__":
    s = RandomizedSet()
    assert s.insert(1) is True
    assert s.remove(2) is False
    assert s.insert(2) is True
    assert s.getRandom() in (1, 2)
    assert s.remove(1) is True
    assert s.insert(2) is False
    assert s.getRandom() == 2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
s = RandomizedSet()
assert s.insert(1) is True
assert s.remove(2) is False
assert s.insert(2) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`insert` / `remove` / `getRandom` 均摊 $O(1)$ 时间。空间 $O(n)$。

## 边界

删除唯一元素时，换尾后数组变空、哈希清空，之后就不能再调 `getRandom`。删除的正好是末尾时，换尾是自身赋值，直接 `pop` 并删哈希就行。插入已存在的值时哈希命中，返回 `false`，数组长度不变。

## 追问

**允许重复呢（LC 381）？**
哈希改成值 $\to$ 下标集合，数组里存重复元素。值可以出现多次时，`getRandom` 要按出现次数均匀，所以每次出现都得在数组里占一格。`insert` 总是追加，返回此前是否不存在。`remove` 只删一次：从该值的下标集合里拿出一个 `i`，把末尾元素搬到 `i`，更新末尾值的下标集合（加上 `i`、去掉旧的尾部下标），再 `pop`；删的正好是最后一个下标时，加和删会抵消，别特判错。均摊仍是 $O(1)$（集合增删），空间 $O(n)$。搬尾时忘了改哈希、或者下标集合空了没从哈希里删掉导致误判还在，是最常见的两个错。

```python
import random


class RandomizedCollection:
    def __init__(self):
        self.idx = {}
        self.arr = []

    def insert(self, val):
        self.idx.setdefault(val, set()).add(len(self.arr))
        self.arr.append(val)
        return len(self.idx[val]) == 1

    def remove(self, val):
        if val not in self.idx or not self.idx[val]:
            return False
        i = self.idx[val].pop()
        last = self.arr[-1]
        self.arr[i] = last
        self.idx[last].add(i)
        self.idx[last].discard(len(self.arr) - 1)
        self.arr.pop()
        if not self.idx[val]:
            del self.idx[val]
        return True

    def getRandom(self):
        return random.choice(self.arr)
```

**要支持并发或持久化呢？**
现在这版没有锁，线程不安全，三个方法共用同一对数组和哈希。两个线程同时 `insert` 可能写到同一个尾部下标，`remove` 换尾时并发 `getRandom` 可能抽到半删除状态。要并发就给三个方法加同一把互斥锁，均摊时间仍是 $O(1)$，但吞吐受锁限制；读写锁收益不大，因为 `getRandom` 也依赖长度和内容。持久化必须同时快照 `arr` 和 `idx`，只存数组不够，下标会随删除变化。随机性来自 `random.choice`，单测时应该注入 RNG。遍历哈希键当随机既不均匀，也是 $O(n)$，别这么做。
