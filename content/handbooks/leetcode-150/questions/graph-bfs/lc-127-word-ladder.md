---
id: lc-127-word-ladder
section: graph-bfs
order: 3
level: S
title: LC 127 · 单词接龙
quick: >-
  单词图：只差一位的词相连。BFS 求 `beginWord` 到 `endWord`
  的最短变换序列长度（含起终点）。可双向 BFS。到不了返回 $0$。
tags:
  - BFS
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 127. 单词接龙
    url: https://leetcode.cn/problems/word-ladder/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

从 `beginWord` 每次改一个字母，中间词必须在 `wordList`。求变成 `endWord` 的最短序列长度（包含起终点）。无法变换返回 $0$。

## 思路

隐式无向图，边权 $1$，BFS 最短。不要 $O(N^2)$ 两两比词。对当前词每个位置换 $26$ 个字母，用哈希集合 $O(1)$ 判断是否在剩余词表；入队即删除，保证每个词只扩一次。

终点不在表里直接 $0$。双向 BFS：从起、终两端交替扩，相遇即最短，单词多时更快。白板我先写单向，再补双向。

## 参考代码

```python
from collections import deque
from typing import List


def ladderLength(beginWord: str, endWord: str, wordList: List[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0
    q = deque([(beginWord, 1)])
    word_set.discard(beginWord)
    letters = "abcdefghijklmnopqrstuvwxyz"
    while q:
        word, steps = q.popleft()
        if word == endWord:
            return steps
        for i in range(len(word)):
            for ch in letters:
                nxt = word[:i] + ch + word[i + 1 :]
                if nxt in word_set:
                    word_set.remove(nxt)
                    q.append((nxt, steps + 1))
    return 0


if __name__ == "__main__":
    assert (
        ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
    )
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    print("ok")
```

## 复杂度

时间 $O(N\cdot L\cdot 26)$ 量级（每次造新串再花 $O(L)$ 则再乘 $L$），$N$ 为词数，$L$ 为词长。空间 $O(N)$。

## 边界

- 终点不在 `wordList`：图里没有终点，直接 $0$。
- 起点已在表中：入队时 `discard`，避免第一步又扩到自己。
- 只有一步之差：BFS 第一层就命中，长度 $2$。短字符集缩小版见 LC 433，独立卡 `lc-433-minimum-genetic-mutation`。

## 追问

- **输出所有最短变换序列（LC 126）？** 不能只记一个前驱。BFS 按层扩展，记录每个词的最短层号；只有「下一层 = 当前层 $+1$」时才把当前词加入前驱集合（同层多条最短边都保留）。碰到终点后本层仍要走完，把所有最短前驱收齐，再从终点 DFS 回溯到起点拼路径。

```python
from collections import defaultdict, deque

def findLadders(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in word_set:
        return []
    letters = "abcdefghijklmnopqrstuvwxyz"
    parents = defaultdict(set)
    level = {beginWord: 0}
    q = deque([beginWord])
    found = False
    while q and not found:
        for _ in range(len(q)):
            w = q.popleft()
            step = level[w]
            for i in range(len(w)):
                for ch in letters:
                    nxt = w[:i] + ch + w[i + 1 :]
                    if nxt not in word_set:
                        continue
                    if nxt not in level:
                        level[nxt] = step + 1
                        q.append(nxt)
                    if level[nxt] == step + 1:
                        parents[nxt].add(w)
                    if nxt == endWord:
                        found = True
    ans = []

    def dfs(word, path):
        if word == beginWord:
            ans.append(path[::-1])
            return
        for p in parents[word]:
            path.append(p)
            dfs(p, path)
            path.pop()

    if found:
        dfs(endWord, [endWord])
    return ans
```

- **双向 BFS？** 从 `beginWord`、`endWord` 各持一个集合，每次扩展更小的一端。新词若落在对端集合里，两端相遇，步数相加即最短长度。入队即从词表删除，避免回头。单词多、分叉大时比单向快。注意先判断终点在表里，否则对端是空的。

```python
def ladderLengthBidirect(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in word_set:
        return 0
    front, back = {beginWord}, {endWord}
    word_set.discard(beginWord)
    steps = 1
    letters = "abcdefghijklmnopqrstuvwxyz"
    while front and back:
        if len(front) > len(back):
            front, back = back, front
        nxt_front = set()
        for w in front:
            for i in range(len(w)):
                for ch in letters:
                    nxt = w[:i] + ch + w[i + 1 :]
                    if nxt in back:
                        return steps + 1
                    if nxt in word_set:
                        word_set.remove(nxt)
                        nxt_front.add(nxt)
        front = nxt_front
        steps += 1
    return 0
```
