---
id: lc-433-minimum-genetic-mutation
section: graph-bfs
order: 2
level: A
title: LC 433 · 最小基因变化
quick: "把 `bank` 里的串当节点、只差一位的串连边，BFS 一层算一次变化：每位换成 `A/C/G/T`，落在剩余 `bank` 里就入队并删掉。第一次到达终点的层数就是最少变化次数，到不了返回 $-1$。"
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

## 题目描述

基因串由 A、C、G、T 四种字符构成，长度固定为 8。给定起始基因 startGene、目标基因 endGene 和合法基因库 bank，每次突变只能改动一个字符，而且每次改动后的基因必须在 bank 中。求从起始串到目标串所需的最少突变次数。

### 接口与输出

实现 `minMutation(startGene: str, endGene: str, bank: List[str]) -> int`。无法到达目标时返回 -1；startGene 作为初始状态，不要求已经存在于 bank。

### 合法输入与约束

`0 <= len(bank) <= 10`；startGene、endGene 及 bank 中每个字符串的长度都是 8，字符只可能是 A/C/G/T。不是求有多少条突变路线。

### 示例

```text
输入：startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]
输出：1
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/minimum-genetic-mutation/description/)。

## 解题思路与参考答案

## 题意

基因串长 $8$，字符只有 `A`、`C`、`G`、`T`。从 `startGene` 开始，每次改一个位置，中间结果必须出现在 `bank` 里，求变成 `endGene` 的最少次数；无法到达返回 $-1$。

## 思路

我会在隐式图上做 BFS。点是 `bank` 里的串加上起点，边是「只差一位」，每次变化代价都是 $1$，所以 BFS 的层数就是最少次数。枚举当前串的每个位置，改成四种碱基，落在剩余的 `bank` 集合里就入队并删掉，避免回头。

拿 `AACCGGTT` 到 `AAACGGTA`、`bank = ["AACCGGTA", "AACCGCTA", "AAACGGTA"]` 来说，第一步改最后一位得到 `AACCGGTA`，第二步改第三位得到 `AAACGGTA`，答案是 $2$。

`endGene` 不在 `bank` 里就直接返回 $-1$（除非起点终点相同，按题意一般终点仍要在库里）。LC 127 是同一套骨架，只是字母表更大、长度不固定。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(B\cdot L\cdot 4)$，$B$ 为库大小，$L=8$；空间 $O(B)$。

## 边界

`bank` 为空时，只要终点不就是起点，就返回 $-1$。起点已经是终点时，如果题意允许 $0$ 次且不要求进库，直接返回 $0$；否则仍要求终点在 `bank` 里。上面的代码对「同串且不在库」返回 $0$。终点不在库中时，它没法作为合法的中间态或终止态，返回 $-1$。完整 26 字母、变长词的版本见 LC 127，独立卡 `lc-127-word-ladder`。

## 追问

**允许不在 `bank` 里的中间态呢？**
约束放开以后，图变成所有长度为 $8$ 的碱基串，点数 $4^8=65536$，照样可以 BFS。每位改成其余 $3$ 种碱基，不用检查 `bank`，用访问集合去重就行。最坏 $O(4^8\cdot 8)$，规模可以接受。连通的话最短步数不超过 $8$，因为每位最多改一次；搜索中可能出现绕远的路径，访问集合（vis）保证拿到的是最短的。

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

**变成单词接龙呢？**
字母表扩成 $26$、长度 $L$ 不固定、词必须在 `wordList` 里，求的是含起终点的序列长度，比变化次数多一。骨架和本题一样，隐式图加 BFS 加入队删词，就是 LC 127，独立卡 `lc-127-word-ladder`。词表大时双向 BFS 更有用。
