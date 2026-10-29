---
id: lc-212-word-search-ii
section: trie
order: 3
level: A
title: LC 212 · 单词搜索 II
quick: >-
  对每个词单独做 LC 79 会超时，所以先把单 vocabulary 建成 Trie，再从每个格子四向 DFS、沿 Trie
  往下走，走不通立刻剪。找到一个词就把词尾清空防重，掏空的子树可以删掉。
tags:
  - Trie
  - Backtracking
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 212. 单词搜索 II
    url: 'https://leetcode.cn/problems/word-search-ii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定小写字母网格 board 和不重复的单词列表 words，返回列表中所有能在网格上找到的单词。一个单词可从任意格子开始，每一步走到上、下、左、右相邻格；同一次拼写路径不能重复使用同一个格子。

### 接口与输出

实现 `findWords(board: List[List[str]], words: List[str]) -> List[str]`。输出单词列表，顺序不限，每个找到的单词只返回一次；不同单词的查找可以使用同一格子。

### 合法输入与约束

网格行列数均为 1 到 12；`1 <= len(words) <= 30000`，每个单词长度为 1 到 10。网格和单词仅含小写英文字母；对角线不能作为相邻移动。

### 示例

```text
输入：board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]], words = ["oath","pea","eat","rain"]
输出：["eat","oath"]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/word-search-ii/description/)。

## 解题思路与参考答案

## 题意

$m\times n$ 字母网格和单 vocabulary。从任意格四连通走，不能重复使用同一格，把所有能在网格里走出的单词（去重）列出来。

## 思路

对每个词单独跑一遍 LC 79 会超时。我会先把 `words` 插进 Trie，让所有词共享前缀，这样一次网格 DFS 能同时查多个词，不用每个词从头遍历网格。

从每个格子出发 DFS。当前字母不在当前 Trie 节点的孩子里，就回退；走到带词尾的节点，就收集这个词，并把词尾清空，避免重复加入。访问过的格子先标记，回溯时恢复。某个子节点被掏空以后，从父节点删掉它，后面的搜索路径会更短。

拿样例里的 `oath` 看。从左上角的 `o` 出发，Trie 里有 `o` 这条边；往右走到 `a`，再往下到 `t`、`h`，到 `h` 时节点上存着 `oath`，收下来。`pea` 在 Trie 里有，但网格里根本没有 `p`，第一步就走不通。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
board = [
    ["o", "a", "a", "n"],
    ["e", "t", "a", "e"],
    ["i", "h", "k", "r"],
    ["i", "f", "l", "v"],
]
assert sorted(findWords(board, ["oath", "pea", "eat", "rain"])) == ["eat", "oath"]
assert findWords([["a", "b"], ["c", "d"]], ["abcb"]) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

最坏仍接近 $O(mn\cdot 4^L)$，$L$ 为最长词；Trie 与删空节点会大幅剪枝。空间 $O(\sum |word|)$ 加递归栈。

## Edge Cases

vocabulary 里有前缀重叠时，比如 `app` 和 `apple`，节点上存的是完整的 `word`，走到 `app` 先收下，再继续往 `l` 走，长词不会被提前剪掉。

同一个词有多条路径时，第一次找到就设 `node.word = None`，后面的路径再走到这个节点也不会重复加入。

网格很小、词很长时，Trie 走不通立刻返回，比按词暴力跑 LC 79 好得多。一词一判定见 LC 79，独立卡 `lc-79-word-search`。

## 追问

**只判断一个词呢？**
那就不用建 Trie，从每个格子 DFS 去匹配 `word[i]`，改盘标记、回溯恢复，这就是 LC 79，独立卡 `lc-79-word-search`。多个词才值得先建 Trie，共享前缀只走一遍网格。

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

**为什么找到以后要清空 `word`？**
为了结果去重。同一个单词可能从不同起点、沿不同的蛇形路线走到同一个 Trie 词尾。清空（或者改成 `None`）以后节点还在，长词后面的字母不受影响；要是把词尾标记以外的结构也 `del` 掉，可能误伤前缀词。子树被掏空后再 `del node.children[ch]` 是另一件事，它剪掉的是再也不会命中的分支，目的是加速，和去重无关。通配搜词（`'.'`）见 LC 211，独立卡 `lc-211-design-add-and-search-words-data-structure`。
