---
id: lc-134-gas-station
section: array-string
order: 14
level: A
title: LC 134 · 加油站
quick: >-
  总油 $\lt$ 总耗则无解。否则从「环上累计亏空最低」的下一站出发必能走一圈。一次扫描，时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 134. 加油站
    url: https://leetcode.cn/problems/gas-station/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

环上 $n$ 站。`gas[i]` 为 $i$ 站加油量，`cost[i]` 为从 $i$ 开到下一站的油耗。求能绕一圈的出发站下标；不存在返回 $-1$。若有解则唯一。

## 思路

先比总和：$\sum(\texttt{gas}[i]-\texttt{cost}[i]) \lt 0$ 则无解。否则一定有解。记 `diff[i] = gas[i]-cost[i]`，前缀和最低点的下一站就是起点：从那里出发，后面不会再把油箱开成负。

等价写法：扫的过程中累计 `tank`，一旦变负，说明当前起点到 $i$ 都不可行，把起点改成 $i+1$ 并清零 `tank`。面试两种说法选一种讲透。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。`sum` 与主循环各一遍。

## 边界

- 只有一站：`gas[0] >= cost[0]` 则起点是 $0$，否则 $-1$。
- 起点是 $0$：全程 `tank` 不变负，`start` 不会被改掉。
- 唯一可行站在末尾：前面每一段都会把 `tank` 打成负，最终 `start = n - 1`。

## 追问

- **为什么「亏空后改起点」正确？** 先由总和判断：总油少于总耗则无解。有解时题面保证唯一。若从 $s$ 走到 $i$ 时油箱变负，说明 $s$ 到 $i$ 这段净和为负，那么 $s,s+1,\ldots,i$ 都不该当起点：从其中任一站出发，到达 $i$ 时前面的净和只可能更小（少了一段非负前缀），仍会在 $i$ 处失败。于是把起点改成 $i+1$ 并清零 `tank`。扫完后 `start` 就是答案，不必再模拟一圈——总和非负已经保证从那里能走通。易错点是忘记先比总和，否则末站之后的「假起点」可能越界还当答案。时间 $O(n)$，额外空间 $O(1)$。

- **要输出沿途油量 / 路径？** 先用上面的方法求出起点（或不存在）。再从起点模拟一整圈，维护当前油箱，每到一站先加油再减耗，记录每天油量。时间再 $O(n)$。不要在第一次扫描里硬记路径：第一次扫描的 `tank` 被清零过，不是真实油箱。若只要判断能否走完，第一次扫描已经够。

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

