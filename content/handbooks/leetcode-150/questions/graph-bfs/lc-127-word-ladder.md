---
id: lc-127-word-ladder
section: graph-bfs
order: 3
level: S
title: LC 127 · 单词接龙
quick: >-
  把只差一个字母的词连边，BFS 第一次到达 `endWord` 的层数就是最短变换序列长度（含起终点），到不了返回 $0$。邻居靠逐位换 26
  个字母、查哈希集合生成，入队即删词；vocabulary 大时可以用双向 BFS。
tags:
  - BFS
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 127. 单词接龙
    url: 'https://leetcode.cn/problems/word-ladder/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定起始单词 beginWord、目标单词 endWord 和单 vocabulary wordList，寻找最短的单词变换序列。序列以 beginWord 开始、endWord 结束，每对相邻单词恰好有一个位置的字母不同，起点以外的每个单词都必须出现在 wordList 中。起始单词不必在单 vocabulary 中。

### 输入与输出

实现 `ladderLength(beginWord: str, endWord: str, wordList: List[str]) -> int`。返回最短序列包含的单词个数，计入起点和终点；无法完成变换时返回 0。

### 约束

- 所有单词长度相同，长度为 1 到 10，且只含小写英文字母。
- `1 <= len(wordList) <= 5000`，表内单词互不相同，beginWord 与 endWord 不同。

### 示例

```text
输入：beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]
输出：5
```

一条最短序列为 `hit -> hot -> dot -> dog -> cog`，共 5 个单词，因此返回 5，而不是变换次数 4。

## 解题思路与参考答案

## 题意

从 `beginWord` 出发，每次改一个字母，中间词必须在 `wordList` 里，求变成 `endWord` 的最短序列长度（包含起点和终点）。无法变换返回 $0$。

## 思路

我会用 BFS。把单词看作节点，只差一个字母的词之间连边，每条边代表一次变换、代价都是 $1$，所以 BFS 第一次到达终点时得到的就是最短长度。

建图不用 $O(N^2)$ 两两比较词。对当前词的每个位置换 $26$ 个字母，用哈希集合 $O(1)$ 判断在不在剩余 vocabulary 里；入队时就把词从集合里删掉，保证每个词只扩展一次。拿 `hit` 到 `cog` 来说，`hit` 只能变成 `hot`，`hot` 再扩出 `dot`、`lot`，下一层是 `dog`、`log`，再下一层到 `cog`，序列 `hit → hot → dot → dog → cog` 长度为 $5$。

终点不在表里直接返回 $0$。双向 BFS 从起点、终点两端交替扩，相遇时就是最短，单词多时更快。白板上我先写单向，再补双向。

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
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间是 $O(N\cdot L\cdot 26)$ 量级，每次造新串还要花 $O(L)$ 的话再乘一个 $L$；$N$ 为词数，$L$ 为词长。空间 $O(N)$。

## Edge Cases

终点不在 `wordList` 里时，图里就没有终点，直接返回 $0$。起点已经在表里时，入队时 `discard` 掉，避免第一步又扩回自己。只差一步时 BFS 第一层就命中，长度 $2$。字符集更小的缩小版是 LC 433，独立卡 `lc-433-minimum-genetic-mutation`。

## 追问

**要输出所有最短变换序列（LC 126）呢？**
这时每个词要记下全部最短前驱，一个前驱不够用。BFS 按层扩展，记录每个词的最短层号；只有「下一层 = 当前层 $+1$」时才把当前词加进前驱集合，同层的多条最短边都保留。碰到终点后本层仍要走完，把所有最短前驱收齐，再从终点 DFS 回溯到起点拼路径。

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

**双向 BFS 怎么写？**
从 `beginWord`、`endWord` 各维护一个集合，每次扩展更小的那一端。新词如果落在对端集合里，说明两端相遇，步数相加就是最短长度。入队即从 vocabulary 删掉，避免回头。单词多、分叉大时比单向快。要先判断终点在表里，否则对端是空的。

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
