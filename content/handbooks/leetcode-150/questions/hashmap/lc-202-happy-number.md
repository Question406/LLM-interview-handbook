---
id: lc-202-happy-number
section: hashmap
order: 7
level: A
title: LC 202 · 快乐数
quick: >-
  反复把各位平方和替换当前数。到 $1$ 为快乐；出现重复则有环。用 `seen` 集合或快慢指针检环。时间约
  $O(\log n)$。
tags:
  - Hash
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 202. 快乐数
    url: https://leetcode.cn/problems/happy-number/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

定义下一步为各位数字的平方和。从 $n$ 出发不断替换，若最终到 $1$ 则是快乐数；否则会在某个不含 $1$ 的环里转。

## 思路

下一步函数确定，状态空间有限，非 $1$ 必入环。两种检环：

- `seen` 集合：出现过的数再出现就停。
- 快慢指针：`slow` 走一步、`fast` 走两步，相遇且不是 $1$ 则有环。

$19$：$1^2+9^2=82\to 68\to 100\to 1$。$2$ 会掉进 $4,16,37,\ldots$ 的环。

## 参考代码

```python
def isHappy(n: int) -> bool:
    def nxt(x: int) -> int:
        s = 0
        while x:
            x, d = divmod(x, 10)
            s += d * d
        return s

    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = nxt(n)
    return n == 1


if __name__ == "__main__":
    assert isHappy(19) is True
    assert isHappy(2) is False
    assert isHappy(1) is True
    print("ok")
```

## 复杂度

时间 $O(\log n)$ 量级（下一步迅速掉进三位数以内），额外空间：集合 $O(1)$ 量级，快慢指针 $O(1)$。

## 边界

- $n=1$ 已经在终点，直接真。
- $n=7$ 也会走到 $1$，不要只背 $19$ 这一个样例。

## 追问

- **只要 $O(1)$ 额外空间？** 下一步函数当链表的 `next`，用 Floyd 快慢指针检环：`slow` 走一步、`fast` 走两步。`fast` 先到 $1$ 就是快乐数；否则二者在非 $1$ 处相遇说明入环。初始化可让 `fast` 先走一步，循环条件写成「`fast != 1` 且 `slow != fast`」。时间仍是状态空间大小的量级，空间 $O(1)$。不要把相遇当成快乐：相遇只说明有环，还要看是不是 $1$。

```python
def isHappy(n):
    def nxt(x):
        s = 0
        while x:
            x, d = divmod(x, 10)
            s += d * d
        return s

    slow, fast = n, nxt(n)
    while fast != 1 and slow != fast:
        slow = nxt(slow)
        fast = nxt(nxt(fast))
    return fast == 1
```

- **为什么非 $1$ 必入环、不会无限变大？** 各位平方和是确定函数：一位数最多 $81$，三位数 $999$ 的下一步是 $3\times 81=243$，四位数立刻掉回三位数以内。所以从任意 $n$ 出发，有限步后状态落在 $\{1,\ldots,243\}$ 这个有限集。有限集上每个点出度恰好 $1$，从一点出发要么到 $1$，要么进入某个不含 $1$ 的环（常见是 $4\to 16\to 37\to\cdots\to 4$）。因此检环或集合去重都能判定，不存在「越算越大」的逃逸路径。
