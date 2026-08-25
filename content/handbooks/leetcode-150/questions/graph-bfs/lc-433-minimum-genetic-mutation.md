---
id: lc-433-minimum-genetic-mutation
section: graph-bfs
order: 2
level: A
title: LC 433 · 最小基因变化
quick: >-
  每次改一个字符（`A/C/G/T`），新串必须在 `bank`。BFS 求到终点的最少变化次数，到不了返回
  $-1$。
tags:
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 433. 最小基因变化
    url: https://leetcode.cn/problems/minimum-genetic-mutation/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

基因串长 $8$，字符仅 `A`、`C`、`G`、`T`。从 `startGene` 开始，每次改一个位置，中间结果必须出现在 `bank`。求变成 `endGene` 的最少次数；无法到达返回 $-1$。

## 思路

隐式图：点是 `bank` 里的串（加上起点），边是「只差一位」。BFS 一层一步。枚举当前串每个位置改成四种碱基，落在剩余 `bank` 集合里就入队并删掉，避免回头。

`endGene` 不在 `bank` 则直接 $-1$（除非起终点相同，按题意一般仍要在库里）。这是 LC 127 的短字符集缩小版。

## 参考代码

```python
from collections import deque
from typing import List


def minMutation(startGene: str, endGene: str, bank: List[str]) -> int:
    bank_set = set(bank)
    if endGene not in bank_set:
        return 0 if startGene == endGene else -1
    q = deque([(startGene, 0)])
    bank_set.discard(startGene)
    bases = "ACGT"
    while q:
        gene, steps = q.popleft()
        if gene == endGene:
            return steps
        for i in range(len(gene)):
            for b in bases:
                nxt = gene[:i] + b + gene[i + 1 :]
                if nxt in bank_set:
                    bank_set.remove(nxt)
                    q.append((nxt, steps + 1))
    return -1


if __name__ == "__main__":
    assert minMutation("AACCGGTT", "AACCGGTA", ["AACCGGTA"]) == 1
    assert (
        minMutation(
            "AACCGGTT",
            "AAACGGTA",
            ["AACCGGTA", "AACCGCTA", "AAACGGTA"],
        )
        == 2
    )
    assert minMutation("AACCGGTT", "AACCGGTA", []) == -1
    print("ok")
```

## 复杂度

时间 $O(B\cdot L\cdot 4)$，$B$ 为库大小，$L=8$。空间 $O(B)$。

## 边界

- `bank` 为空：终点若不就是起点，返回 $-1$。
- 起点已是终点：若题意允许 $0$ 次且不必进库，直接 $0$；否则仍要求终点在 `bank`。上面代码对「同串且不在库」返回 $0$。
- 终点不在库中：无法作为合法中间/终止态，返回 $-1$。完整 26 字母、变长词版见 LC 127，独立卡 `lc-127-word-ladder`。

## 追问

- **允许不在 `bank` 的中间态？** 约束一放开，图变成所有长 $8$ 的碱基串，点数 $4^8=65536$。BFS 照样做：每位改成其余 $3$ 种碱基，不必查 `bank`，只 vis 去重。最坏 $O(4^8\cdot 8)$，规模可接受。终点仍可能极远，但连通的话最长也不超过 $8$（每位最多改一次，实际因可绕路更长，vis 保证最短）。

```python
from collections import deque

def minMutationFree(start, end):
    if start == end:
        return 0
    bases = "ACGT"
    q = deque([(start, 0)])
    seen = {start}
    while q:
        gene, steps = q.popleft()
        for i in range(len(gene)):
            for b in bases:
                if b == gene[i]:
                    continue
                nxt = gene[:i] + b + gene[i + 1 :]
                if nxt in seen:
                    continue
                if nxt == end:
                    return steps + 1
                seen.add(nxt)
                q.append((nxt, steps + 1))
    return -1
```

- **变成单词接龙？** 字母表扩成 $26$、长度 $L$ 不固定、词必须在 `wordList`，求的是序列长度（含起终点）而不是变化次数。骨架同本题：隐式图 + BFS + 入队删词。即 LC 127，独立卡 `lc-127-word-ladder`。双向 BFS 在词表大时更有用。
