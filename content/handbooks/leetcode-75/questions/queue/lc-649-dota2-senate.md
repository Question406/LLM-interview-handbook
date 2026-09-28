---
id: lc-649-dota2-senate
section: queue
order: 2
level: A
title: LC 649 · Dota2 参议院
quick: >-
  贪心：每个参议员都禁掉下一个将要行动的对手。两个队列按下标存 R 和 D，每次比较队头，下标小的先行动、禁掉对方队头，自己以 `i+n`
  重新入队进入下一轮。某队空了另一方获胜。时间 $O(n)$，额外空间 $O(n)$。
tags:
  - String
  - Queue
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 649. Dota2 Senate
    url: https://leetcode.com/problems/dota2-senate/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

字符串 `senate` 只含 `'R'`（天辉）和 `'D'`（夜魇），按下标顺序一轮一轮行动。轮到某个还有权利的参议员时，他可以禁止任意一个参议员之后所有轮次的权利，或者在只剩本阵营时宣布胜利。被禁的人跳过。双方都采取最优策略，返回 `"Radiant"` 或 `"Dire"`。$1 \le n \le 10^4$。

## 思路

最优动作是禁掉「下一个将要行动的对方参议员」。交换论证：如果禁的是更靠后的对手 $y$，而离得最近的对手 $x$ 保留了下来，$x$ 会先于 $y$ 出手，对本方的威胁不小于 $y$；换成禁 $x$ 不会让局面变差。

实现上用两个队列存下标。每次取两队队头 `r`、`d`，小的先行动：它禁掉对方队头（直接弹掉），自己以下标 `+ n` 回到队尾，表示下一轮再次出手。每次比较永久移除一个人，最多 $n$ 次就分出胜负。逐轮扫字符串、标记被禁者的模拟需要多轮，且每次找下一个对手要额外扫描。

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

## 复杂度

时间 $O(n)$：每次循环两个出队、一个入队，总人数减一。额外空间 $O(n)$。

## 边界

- 只有一方：循环不执行，直接获胜。
- 人数相同时先手占优：`"RD"` 天辉赢，`"DR"` 夜魇赢。
- 人数少的一方也可能赢，如 `"RRDDD"`：两个 R 先禁掉前两个 D，最后那个 D 只能禁掉一个 R，第二轮剩下的 R 先出手把它禁掉。

## 追问

- **只用一个队列加计数的写法？** 队列里放字符，另记「待禁的 R 数」「待禁的 D 数」。弹出一个人：如果本阵营有待禁名额就消耗一个、他出局；否则给对方待禁数加一，自己回到队尾。某一方存活人数归零时结束。

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

- **为什么重新入队用 `i + n`？** 下一轮的顺序是「本轮剩下的人在前，已经行动过的人在后」。加 $n$ 让已行动者的下标大于本轮所有未行动者，两队队头比较仍然正确反映出手先后。
