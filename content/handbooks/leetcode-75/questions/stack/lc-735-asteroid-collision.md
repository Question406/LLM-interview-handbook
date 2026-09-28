---
id: lc-735-asteroid-collision
section: stack
order: 2
level: S
title: LC 735 · 小行星碰撞
quick: >-
  栈里存目前还活着的行星。只有「栈顶向右、当前向左」才会相撞：小的爆炸，一样大一起爆，当前行星更大就继续撞新的栈顶。每颗最多进出栈一次，时间
  $O(n)$，额外空间 $O(n)$。
tags:
  - Array
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 735. Asteroid Collision
    url: https://leetcode.com/problems/asteroid-collision/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

整数数组 `asteroids` 表示一排行星，绝对值是大小，正数向右飞、负数向左飞，速度相同。两颗相遇时小的爆炸；大小相同则都爆炸；同向的永远不会相遇。返回碰撞全部结束后剩下的行星（保持原顺序）。元素非零，$2 \le n \le 10^4$。

## 思路

从左往右处理，栈里是已经稳定下来的行星。新行星 `a` 只可能和栈顶相撞，且只有栈顶向右、`a` 向左这一种情况。撞的时候比大小：栈顶小就弹掉，`a` 继续和新栈顶比；一样大就弹掉栈顶，`a` 也没了；栈顶大则 `a` 没了。`a` 活到最后才入栈。

向左飞的行星如果栈顶也向左或栈为空，它会一直飞出去，直接入栈。栈底可能是一串负数，后面是一串正数，这个形状保证了结果不会再有碰撞。容易漏的是「当前行星更大」时要继续循环，不是只撞一次。

## 参考代码

```python
from typing import List


def asteroidCollision(asteroids: List[int]) -> List[int]:
    stack: List[int] = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
                continue
            if stack[-1] == -a:
                stack.pop()
            alive = False
        if alive:
            stack.append(a)
    return stack


if __name__ == "__main__":
    assert asteroidCollision([5, 10, -5]) == [5, 10]
    assert asteroidCollision([8, -8]) == []
    assert asteroidCollision([10, 2, -5]) == [10]
    assert asteroidCollision([-2, -1, 1, 2]) == [-2, -1, 1, 2]
    assert asteroidCollision([1, -2, -2, -2]) == [-2, -2, -2]
    assert asteroidCollision([-2, 1, -1, -2]) == [-2, -2]
    assert asteroidCollision([1, 2, 3, -10]) == [-10]
    print("ok")
```

## 复杂度

时间 $O(n)$：每颗行星最多入栈一次、出栈一次，`while` 的总次数被出栈次数限住。额外空间 $O(n)$。

## 边界

- 负数在前、正数在后：彼此背离，全部保留。
- 一颗很大的向左行星：一路把栈顶的向右行星清空，然后入栈。
- 大小相同：两颗一起消失，当前行星不入栈。

## 追问

- **为什么 `while` 嵌在 `for` 里还是 $O(n)$？** 每进一次 `while` 要么弹出一颗（总共最多 $n$ 次），要么让当前行星死亡并退出循环（每颗最多一次），合起来 $O(n)$，是摊还分析。
- **改规则：相撞后大的那颗大小减去小的那颗？** 骨架不变，只是当前行星赢了要把自己的大小减掉栈顶大小再继续撞，栈顶赢了要把栈顶改小。

```python
def asteroidCollisionShrink(asteroids):
    stack = []
    for a in asteroids:
        while a < 0 and stack and stack[-1] > 0:
            top = stack.pop()
            if top > -a:
                stack.append(top + a)
                a = 0
                break
            if top == -a:
                a = 0
                break
            a += top
        if a != 0:
            stack.append(a)
    return stack
```
