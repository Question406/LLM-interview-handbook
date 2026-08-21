---
id: lc-212-word-search-ii
section: trie
order: 3
level: A
title: LC 212 · 单词搜索 II
quick: >-
  单词先建成 Trie。网格四向 DFS，沿 Trie 往下走；走不通立刻剪。找到就把词尾清空防重，空子树可删。
tags:
  - Trie
  - Backtracking
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 212. 单词搜索 II
    url: https://leetcode.cn/problems/word-search-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 字母网格和单词表。从任意格四连通走，不能重复使用同一格，把所有能在网格里走出的单词（去重）列出来。

## 思路

对每个词做 LC 79 会超时。先把 `words` 插进 Trie。从每个格子 DFS：当前字母不在当前 Trie 节点的孩子里就回退；走到带词尾的节点就收集，并把词尾清空以免重复加入。格子先标记再回溯。子节点被掏空后可从父节点删掉，后续路径更短。

面试对比 79：「一词暴力、多词必须 Trie 剪枝」。

## 参考代码

```python
from typing import List


class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None


def findWords(board: List[List[str]], words: List[str]) -> List[str]:
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.word = w

    m, n = len(board), len(board[0])
    ans = []

    def dfs(r: int, c: int, node: TrieNode) -> None:
        ch = board[r][c]
        if ch not in node.children:
            return
        nxt = node.children[ch]
        if nxt.word:
            ans.append(nxt.word)
            nxt.word = None
        board[r][c] = "#"
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] != "#":
                dfs(nr, nc, nxt)
        board[r][c] = ch
        if not nxt.children:
            del node.children[ch]

    for i in range(m):
        for j in range(n):
            dfs(i, j, root)
    return ans


if __name__ == "__main__":
    board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    assert sorted(findWords(board, ["oath", "pea", "eat", "rain"])) == ["eat", "oath"]
    assert findWords([["a", "b"], ["c", "d"]], ["abcb"]) == []
    print("ok")
```

## 复杂度

最坏仍接近 $O(mn\cdot 4^L)$，$L$ 为最长词；Trie 与删空节点会大幅剪枝。空间 $O(\sum |word|)$ 加递归栈。

## 边界

- 词表有前缀重叠（`app` / `apple`）：节点上存完整 `word` 而不是布尔词尾，走到 `app` 先收再继续往 `l` 走，不会提前剪掉长词。
- 同一词多条路径：第一次找到就把 `node.word = None`，后续路径再走到同一节点不会重复加入。
- 网格很小、词很长：Trie 走不通立刻返回，比按词暴力 LC 79 好得多。一词一判定见 LC 79，独立卡 `lc-79-word-search`。

## 追问

- **只判断某一个词？** 不必建 Trie。从每个格子 DFS，匹配 `word[i]`，改盘标记、回溯恢复。即 LC 79，独立卡 `lc-79-word-search`。多词才值得预处理 Trie：共享前缀只走一遍网格。

```python
def exist(board, word):
    m, n = len(board), len(board[0])

    def dfs(r, c, i):
        if i == len(word):
            return True
        if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != word[i]:
            return False
        tmp, board[r][c] = board[r][c], "#"
        ok = (
            dfs(r + 1, c, i + 1)
            or dfs(r - 1, c, i + 1)
            or dfs(r, c + 1, i + 1)
            or dfs(r, c - 1, i + 1)
        )
        board[r][c] = tmp
        return ok

    return any(dfs(i, j, 0) for i in range(m) for j in range(n))
```

- **为何找到后清空 `word`？** 结果要去重。同一单词可能从不同起点、不同蛇形走到同一个 Trie 词尾。清空（或改成 `None`）后节点还在，长词的后续字母不受影响；若直接 `del` 词尾标记以外的结构，可能误伤前缀词。子树被掏空再 `del node.children[ch]` 是另一件事：那是剪掉再也不会命中的分支，加速而不是去重。通配搜词（`'.'`）见 LC 211，独立卡 `lc-211-design-add-and-search-words-data-structure`。
