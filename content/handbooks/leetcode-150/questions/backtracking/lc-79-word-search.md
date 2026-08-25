---
id: lc-79-word-search
section: backtracking
order: 7
level: S
title: LC 79 · 单词搜索
quick: >-
  从每个格子出发，四方向 DFS。当前格改成标记再搜邻居，回溯时恢复。字母不匹配或越界立刻返回。
tags:
  - Backtracking
  - Grid
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 79. 单词搜索
    url: https://leetcode.cn/problems/word-search/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 字符网格与单词 `word`。判断能否从某一格出发，每次走四连通相邻格（不可重复使用同一格）拼出该词。

## 思路

枚举起点，对 `word[0]` 匹配的格子 DFS。状态是「当前坐标 + 已匹配长度」。越界、已访问、字母对不上就失败。走到词长即成功。访问标记：先把格子改成占位符，四向递归，回来改回原字母。

不要用全局 `visited` 却忘了回溯。多词搜索应改 Trie，见 LC 212。白板我会强调「改盘 + 恢复」。

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

## 复杂度

时间 $O(mn\cdot 4^L)$，$L$ 为词长。额外空间 $O(L)$ 递归栈（原地标记）。

## 边界

- 单词长 $1$：只要盘上出现该字母即为真，DFS 第一步匹配后 `i+1==len` 返回。
- 整盘刚好一条蛇形路径拼出该词：标记保证不走回头路，能走通。
- 需要回头但格子已用：例如 `ABCB` 想复用中间的 `B`，标记 `'#'` 后失败，应返回假。

## 追问

- **同一格能否用两次？** 不能。题目要求路径上格子互异。必须在进入时改盘（或 `visited`），四向搜完再恢复。忘了回溯会把后续起点的路也堵死；忘了标记则会在两个相邻相同字母间来回震荡。

- **一次搜很多词？** 对每个词跑一遍本题是 $O(|words|\cdot mn\cdot 4^L)$，共享前缀会重复走。把词表建成 Trie，从每个格子沿 Trie 往下 DFS，走不通立刻剪；找到后清空词尾防重，空子树可删。即 LC 212，独立卡 `lc-212-word-search-ii`。

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
