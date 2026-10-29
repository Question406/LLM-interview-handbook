---
id: lc-649-dota2-senate
section: queue
order: 2
level: A
title: LC 649 · Dota2 参议院
quick: >-
  贪心，每个参议员都禁掉下一个将要行动的对手。两个队列按下标存 R 和 D，每次比较队头，下标小的先行动、禁掉对方队头，自己以 `i+n`
  重新入队进入下一轮；某队空了，另一方获胜。时间 $O(n)$，额外空间 $O(n)$。
tags:
  - String
  - Queue
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 649. Dota2 Senate
    url: 'https://leetcode.com/problems/dota2-senate/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

字符串 `senate` 表示按座位顺序排列的参议员，R 属于 Radiant 阵营，D 属于 Dire 阵营。按字符串顺序一轮接一轮行动：仍有权利的人在自己回合可以永久禁止一名其他参议员的权利，被禁止者在之后所有回合均跳过；如果所有仍有权利的人都属于同一阵营，该阵营可以宣布胜利。双方都以让本阵营获胜为目标采取最优行动。

### 输入与输出

实现 `predictPartyVictory(senate) -> str`，返回最终获胜阵营的英文名称 `Radiant` 或 `Dire`。结果不是缩写 R/D，也不需要返回具体的禁权操作序列。

### 约束

- `1 <= len(senate) <= 10^4`。
- 字符串中的每个字符只可能是 R 或 D。
- 行动先后由原座位顺序决定，被禁止的人不会在后续轮次恢复。

### 示例

```text
输入：senate = "RD"
输出："Radiant"
```

[LeetCode 原题](https://leetcode.com/problems/dota2-senate/description/)

## 解题思路与参考答案

## 题意

字符串 `senate` 只含 `'R'`（天辉）和 `'D'`（夜魇），按下标顺序一轮一轮行动。轮到某个还有权利的参议员时，他可以禁止任意一个参议员之后所有轮次的权利，或者在只剩本阵营时宣布胜利。被禁的人跳过。双方都采取最优策略，返回 `"Radiant"` 或 `"Dire"`。$1 \le n \le 10^4$。

## 思路

我会用贪心加两个队列，每个参议员的最优动作是禁掉「下一个将要行动的对方参议员」。用交换论证说明，如果禁的是更靠后的对手 $y$，而离得最近的对手 $x$ 保留了下来，$x$ 会先于 $y$ 出手，对本方的威胁不小于 $y$；换成禁 $x$ 不会让局面变差。

实现上用两个队列存下标。每次取两队队头 `r`、`d`，小的先行动，它禁掉对方队头（直接弹掉），自己以下标 `+ n` 回到队尾，表示下一轮再次出手。每次比较永久移除一个人，最多 $n$ 次就分出胜负。如果逐轮扫字符串、标记被禁者，要跑很多轮，每次找下一个对手还得额外扫描。

拿 `"RDD"` 走一遍。R 队是 `[0]`，D 队是 `[1, 2]`。0 比 1 小，R 先出手，禁掉下标 1 的 D，自己以 3 回到队尾。接着比 3 和 2，D 先出手，禁掉这个 R。R 队空了，夜魇赢。

## 参考代码

```python
from collections import deque


def predictPartyVictory(senate: str) -> str:
    n = len(senate)
    radiant, dire = deque(), deque()
    for i, c in enumerate(senate):
        (radiant if c == "R" else dire).append(i)
    while radiant and dire:
        r, d = radiant.popleft(), dire.popleft()
        if r < d:
            radiant.append(r + n)
        else:
            dire.append(d + n)
    return "Radiant" if radiant else "Dire"


if __name__ == "__main__":
    assert predictPartyVictory("RD") == "Radiant"
    assert predictPartyVictory("RDD") == "Dire"
    assert predictPartyVictory("R") == "Radiant"
    assert predictPartyVictory("D") == "Dire"
    assert predictPartyVictory("DDRRR") == "Dire"
    assert predictPartyVictory("RRDDD") == "Radiant"
    assert predictPartyVictory("DR") == "Dire"
    assert predictPartyVictory("DRRR") == "Radiant"
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert predictPartyVictory("RD") == "Radiant"
assert predictPartyVictory("RDD") == "Dire"
assert predictPartyVictory("R") == "Radiant"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$：每次循环两个出队、一个入队，总人数减一。额外空间 $O(n)$。

## Edge Cases

只有一方时循环不执行，直接获胜。

人数相同时先手占优，`"RD"` 天辉赢，`"DR"` 夜魇赢。

人数少的一方也可能赢，比如 `"RRDDD"`。两个 R 先禁掉前两个 D，最后那个 D 只能禁掉一个 R，第二轮剩下的 R 先出手把它禁掉。

## 追问

**只用一个队列加计数怎么写？**
队列里放字符，另记「待禁的 R 数」「待禁的 D 数」。弹出一个人时，如果本阵营有待禁名额，就消耗一个，他出局；否则给对方待禁数加一，自己回到队尾。某一方存活人数归零时结束。

```python
from collections import Counter, deque


def predictPartyVictoryCount(senate):
    q = deque(senate)
    alive = Counter(senate)
    ban = {"R": 0, "D": 0}
    while alive["R"] and alive["D"]:
        c = q.popleft()
        if ban[c]:
            ban[c] -= 1
            alive[c] -= 1
        else:
            ban["D" if c == "R" else "R"] += 1
            q.append(c)
    return "Radiant" if alive["R"] else "Dire"
```

**为什么重新入队用 `i + n`？**
因为下一轮的顺序是「本轮剩下的人在前，已经行动过的人在后」。加 $n$ 让已行动者的下标大于本轮所有未行动者，两队队头比较仍然正确反映出手先后。
