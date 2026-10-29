---
id: lc-79-word-search
section: backtracking
order: 7
level: S
title: LC 79 · 单词搜索
quick: 从每个格子出发做四方向 DFS。进入格子时把它改成标记再搜邻居，回溯时恢复；越界、已访问或字母不匹配就立刻返回。时间 $O(mn\cdot 4^L)$。
tags:
  - Backtracking
  - Grid
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 79. 单词搜索
    url: 'https://leetcode.cn/problems/word-search/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定字符矩阵 `board` 和字符串 `word`，判断能否沿矩阵中的一条路径依次读出 word。可以从任意格子开始，每一步只走到上、下、左、右相邻格子；同一条路径内不能重复使用同一个格子，不能沿对角线移动。

### 输入与输出

实现 `exist(board, word) -> bool`。若存在满足条件的路径返回 True，否则返回 False。路径上的字符必须与 word 按顺序完全一致。

### 约束

- 矩阵有 m 行 n 列，`1 <= m, n <= 6`。
- `1 <= len(word) <= 15`。
- 矩阵和单词都只包含大小写英文字母；大小写按不同字符处理。

### 示例

```text
输入：board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/word-search/description/)

## 解题思路与参考答案

## 题意

$m\times n$ 字符网格与单词 `word`。判断能否从某一格出发，每次走四连通相邻格（不可重复使用同一格）拼出该词。

## 思路

我会枚举起点做 DFS，从和 `word[0]` 匹配的格子出发。状态是「当前坐标 + 已匹配长度」，越界、已访问、字母对不上就失败，匹配长度走到词长就成功。访问标记直接改在盘上，先把格子改成占位符，四个方向递归，回来再改回原字母。

拿题里的盘和 `ABCB` 看。`A→B→C` 都能走通，下一步要再找一个 `B`，可唯一相邻的 `B` 就是刚走过的那个，它已经被改成 `'#'`，所以失败，返回假。

一条路径搜完后一定要恢复标记，让后面的路径还能用这些格子；用一个全局 `visited` 又不恢复，会误封住其他起点。一次搜很多词时可以用 Trie 共享前缀，就是 LC 212。

## 参考代码

```python
from typing import List


def exist(board: List[List[str]], word: str) -> bool:
    m, n = len(board), len(board[0])

    def dfs(r: int, c: int, i: int) -> bool:
        if i == len(word):
            return True
        if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != word[i]:
            return False
        tmp = board[r][c]
        board[r][c] = "#"
        found = (
            dfs(r + 1, c, i + 1)
            or dfs(r - 1, c, i + 1)
            or dfs(r, c + 1, i + 1)
            or dfs(r, c - 1, i + 1)
        )
        board[r][c] = tmp
        return found

    return any(dfs(i, j, 0) for i in range(m) for j in range(n))


if __name__ == "__main__":
    board = [
        ["A", "B", "C", "E"],
        ["S", "F", "C", "S"],
        ["A", "D", "E", "E"],
    ]
    assert exist(board, "ABCCED") is True
    assert exist(board, "SEE") is True
    assert exist(board, "ABCB") is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
board = [
    ["A", "B", "C", "E"],
    ["S", "F", "C", "S"],
    ["A", "D", "E", "E"],
]
assert exist(board, "ABCCED") is True
assert exist(board, "SEE") is True
assert exist(board, "ABCB") is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn\cdot 4^L)$，$L$ 是词长。原地标记，额外空间只有 $O(L)$ 的递归栈。

## Edge Cases

单词长 $1$ 时，只要盘上有这个字母就为真，DFS 第一步匹配后 `i+1==len` 返回。整盘刚好有一条蛇形路径拼出该词时，标记保证不走回头路，能走通。需要回头但格子已经用过的情况，就是上面 `ABCB` 想复用中间的 `B`，应返回假。

## 追问

**同一格能用两次吗？**
不能，题目要求路径上的格子互不相同。所以进入时要改盘（或者记 `visited`），四个方向搜完再恢复。忘了回溯会把后续起点的路也堵死；忘了标记，会在两个相邻的相同字母之间来回震荡。

**一次要搜很多词呢？**
对每个词跑一遍本题是 $O(|words|\cdot mn\cdot 4^L)$，共享前缀会被重复走。把 vocabulary 建成 Trie，从每个格子沿 Trie 往下 DFS，走不通立刻剪；找到一个词就清掉词尾标记防止重复收，空子树可以删掉。这就是 LC 212，独立卡 `lc-212-word-search-ii`。

```python
def existMany(board, words):
    trie = {}
    for w in words:
        node = trie
        for ch in w:
            node = node.setdefault(ch, {})
        node["#"] = w
    m, n = len(board), len(board[0])
    ans = []

    def dfs(r, c, node):
        ch = board[r][c]
        if ch not in node:
            return
        nxt = node[ch]
        if "#" in nxt:
            ans.append(nxt.pop("#"))
        board[r][c] = "."
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] != ".":
                dfs(nr, nc, nxt)
        board[r][c] = ch
        if not nxt:
            del node[ch]

    for i in range(m):
        for j in range(n):
            dfs(i, j, trie)
    return ans
```
