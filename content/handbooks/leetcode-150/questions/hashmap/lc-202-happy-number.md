---
id: lc-202-happy-number
section: hashmap
order: 7
level: A
title: LC 202 · 快乐数
quick: >-
  不断把当前数换成各位数字的平方和，到 $1$ 就是快乐数，出现重复说明进了环。检环可以用 `seen` 集合，也可以用快慢指针，时间约 $O(\log
  n)$。
tags:
  - Hash
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 202. 快乐数
    url: 'https://leetcode.cn/problems/happy-number/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

从一个正整数 n 开始，反复把当前数字替换成“每一位十进制数字的平方之和”。如果最终能到达 1，则 n 是快乐数；如果不断重复这一过程仍无法到达 1，则不是快乐数。例如 19 的第一次替换得到 82，因为 `1*1 + 9*9 = 82`。

### 输入与输出

实现 `isHappy(n) -> bool`，返回是否最终能够到达 1。输入本身为 1 时也应返回 True，不要求输出整个变化序列。

### 约束

- `1 <= n <= 2^31 - 1`。
- 所有数位都按十进制解释。

### 示例

```text
输入：n = 19
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/happy-number/description/)

## 解题思路与参考答案

## 题意

下一步定义为各位数字的平方和。从 $n$ 出发不断替换，最终到 $1$ 就是快乐数；否则会在某个不含 $1$ 的环里一直转。

## 思路

这题本质是检环。下一步函数是确定的，状态空间又有限，到不了 $1$ 就一定会进环，所以我一边算一边看「这个数之前出现过没有」。

比如 $19$：$1^2+9^2=82\to 68\to 100\to 1$，是快乐数。$2$ 会掉进 $4,16,37,\ldots$ 这个环，永远到不了 $1$。别只背 $19$ 这一个样例，$2$ 这种进环的情况也要能走一遍。

检环有两种写法。参考代码用 `seen` 集合，出现过的数再出现就停。也可以用快慢指针，`slow` 走一步、`fast` 走两步，相遇时不是 $1$ 就说明有环，写法放在追问里。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isHappy(19) is True
assert isHappy(2) is False
assert isHappy(1) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间大约是 $O(\log n)$ 量级，因为下一步很快就掉进三位数以内。额外空间方面，集合是 $O(1)$ 量级，快慢指针是 $O(1)$。

## Edge Cases

$n=1$ 已经在终点，直接返回真。$n=7$ 也会走到 $1$。

## 追问

**只能用 $O(1)$ 额外空间呢？**
把下一步函数当成链表的 `next`，用 Floyd 快慢指针检环，`slow` 走一步、`fast` 走两步。`fast` 先到 $1$ 就是快乐数；否则两者在非 $1$ 的地方相遇，说明进了环。初始化时可以让 `fast` 先走一步，循环条件写成「`fast != 1` 且 `slow != fast`」。时间仍是状态空间大小的量级，空间 $O(1)$。别把相遇当成快乐，相遇只说明有环，还要看是不是 $1$。

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

**为什么到不了 $1$ 就一定进环，不会越算越大？**
因为数字很快就会变小。各位平方和是确定函数，一位数最多贡献 $81$，三位数 $999$ 的下一步是 $3\times 81=243$，四位数会立刻掉回三位数以内。所以从任意 $n$ 出发，有限步之后状态都落在 $\{1,\ldots,243\}$ 这个有限集里。有限集上每个点的出度恰好是 $1$，从一点出发要么到 $1$，要么进入某个不含 $1$ 的环，常见的是 $4\to 16\to 37\to\cdots\to 4$。所以检环或者集合去重一定能判出来，不存在越算越大逃出去的路径。
