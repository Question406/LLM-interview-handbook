---
id: lc-134-gas-station
section: array-string
order: 14
level: A
title: LC 134 · 加油站
quick: "先比总油量和总油耗，总油不够就无解，够的话一定有解。再扫每站净增油量，累计油箱一变负就把起点挪到下一站并清零，这等价于找前缀和最低点的下一站。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 134. 加油站
    url: https://leetcode.cn/problems/gas-station/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

一条环形公路上有 n 个加油站，按下标递增的方向行驶，最后一站的下一站为第 0 站。`gas[i]` 是在第 i 站能加入的油量，`cost[i]` 是从该站驶向下一站消耗的油量。汽车的油箱容量不受限制，出发时油箱为空。请选择一个出发站，使汽车在任何一段路上都不会缺油，并且能完整绕行一圈。

### 接口与输出

实现 `canCompleteCircuit(gas: List[int], cost: List[int]) -> int`。有解时返回出发站的 0-based 下标，无解时返回 `-1`；题目保证有解时答案唯一。

### 合法输入与约束

两个数组等长；`1 <= n <= 100000`，`0 <= gas[i], cost[i] <= 10000`。油量可以恰好为 0，抵达下一站时不要求仍有剩余油量。

### 示例

```text
输入：gas = [1,2,3,4,5], cost = [3,4,5,1,2]
输出：3
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/gas-station/description/)。

## 解题思路与参考答案

## 题意

环上 $n$ 站。`gas[i]` 是 $i$ 站加油量，`cost[i]` 是从 $i$ 开到下一站的油耗。求能绕一圈的出发站下标；不存在返回 $-1$。有解的话唯一。

## 思路

我先比总和：$\sum(\texttt{gas}[i]-\texttt{cost}[i]) \lt 0$ 就无解，否则一定有解。剩下的问题是找起点。记 `diff[i] = gas[i]-cost[i]`，前缀和最低点的下一站就是起点，因为从那里出发，后面油箱不会再变负。

代码里我用等价的写法：扫的过程中累计 `tank`，一旦变负，说明当前起点到 $i$ 都不可行，就把起点改成 $i+1$、`tank` 清零。拿 `gas=[1,2,3,4,5]`、`cost=[3,4,5,1,2]` 走一遍：前三站净值都是 $-2$，每站都把 `tank` 打成负，起点依次挪到 $1$、$2$、$3$；从 $3$ 开始净值是 $+3$、$+3$，不再变负，答案是 $3$。

两种说法白板上选一种讲透就行。

## 参考代码

```python
from typing import List


def canCompleteCircuit(gas: List[int], cost: List[int]) -> int:
    if sum(gas) < sum(cost):
        return -1
    tank = 0
    start = 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        tank += g - c
        if tank < 0:
            start = i + 1
            tank = 0
    return start


if __name__ == "__main__":
    assert canCompleteCircuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert canCompleteCircuit([2, 3, 4], [3, 4, 3]) == -1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert canCompleteCircuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
assert canCompleteCircuit([2, 3, 4], [3, 4, 3]) == -1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。`sum` 和主循环各一遍。

## 边界

只有一站时，`gas[0] >= cost[0]` 起点就是 $0$，否则返回 $-1$。起点是 $0$ 的话全程 `tank` 不变负，`start` 不会被改掉。唯一可行站在末尾时，前面每一段都会把 `tank` 打成负，最后 `start = n - 1`。

## 追问

**为什么「亏空后改起点」是对的？**
因为从 $s$ 走到 $i$ 时油箱变负，说明 $s$ 到 $i$ 这段净和为负，那么 $s,s+1,\ldots,i$ 都不该当起点。从中间任一站出发，相当于少了一段非负的前缀，到 $i$ 时净和只会更小，照样在 $i$ 失败，所以起点直接跳到 $i+1$、`tank` 清零。扫完后 `start` 就是答案，不必再模拟一圈：前面已经用总和判过无解，总和非负就保证从那里能走通，题面也保证有解时唯一。忘了先比总和的话，末站之后的「假起点」可能越界还被当成答案。时间 $O(n)$，额外空间 $O(1)$。

**要输出沿途油量或路径呢？**
分两步做。先用上面的方法求出起点，或者判出不存在；再从起点模拟一整圈，每到一站先加油再减耗，记下当前油箱，这又是 $O(n)$。别在第一次扫描里顺手记路径，那里的 `tank` 被清零过，不是真实油箱。如果只要判断能否走完，第一次扫描就够了。

```python
def circuit_fuel(gas, cost, start):
    n = len(gas)
    tank = 0
    path = []
    for k in range(n):
        i = (start + k) % n
        tank += gas[i] - cost[i]
        path.append(tank)
        if tank < 0:
            return None
    return path
```
