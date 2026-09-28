---
id: lc-139-word-break
section: dp-1d
order: 3
level: A
title: LC 139 · 单词拆分
quick: >-
  $dp[i]$：前 $i$ 个字符能否拆成词典单词。枚举切分点 $j$，若 $dp[j]$ 且 $s[j:i]$
  在词典则 $dp[i]$ 为真。时间约 $O(n^2)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 139. 单词拆分
    url: https://leetcode.cn/problems/word-break/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

字符串 `s` 与单词表 `wordDict`。判断 `s` 能否空格切成若干词典单词（可重复用）。

## 思路

布尔 DP。$dp[0]=\mathrm{true}$（空前缀）。对每个右端 $i$，枚举左端 $j\lt i$：`dp[j] and s[j:i] in words` 则 `dp[i]=True`。答案是 $dp[n]$。

词典放进 `set`，判断 $O(1)$。可用词典最长词长限制内层循环。BFS / 记忆化搜索同样是「前缀能否拆」。$dp[i]$ 表示前 $i$ 个字符能否拆开。

## 参考代码

```python
from typing import List


def wordBreak(s: str, wordDict: List[str]) -> bool:
    words = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[n]


if __name__ == "__main__":
    assert wordBreak("leetcode", ["leet", "code"]) is True
    assert wordBreak("applepenapple", ["apple", "pen"]) is True
    assert wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
    print("ok")
```

## 复杂度

时间 $O(n^2\cdot L)$（$L$ 为切片哈希），额外空间 $O(n+|dict|)$。用最大词长可把内层压到 $O(n\cdot maxlen)$。

## 边界

- `s` 本身就是一个词：`j=0` 时 `s[0:n]` 在词典，`dp[n]` 直接成真。
- 词典词比 `s` 长：切片对不上，不影响正确性；可用最大词长把内层循环截断。
- 完全拼不出：除 `dp[0]` 外全假，返回 `False`。

## 追问

- **输出一种 / 全部拆法（LC 140）？** 布尔 DP 只回答能否。先算后缀可行性 `can[i]`：`s[i:]` 能否拆。再从下标 $0$ 回溯，只沿 `can[j]` 为真且 `s[i:j]` 在词典的切分走；走到 $n$ 就把路径用空格拼成句子。只要一种则搜到就返回。最坏方案数指数级。

```python
def wordBreakII(s, wordDict):
    words = set(wordDict)
    n = len(s)
    can = [False] * (n + 1)
    can[n] = True
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if can[j] and s[i:j] in words:
                can[i] = True
                break
    ans, path = [], []
    def dfs(i):
        if i == n:
            ans.append(" ".join(path))
            return
        for j in range(i + 1, n + 1):
            if can[j] and s[i:j] in words:
                path.append(s[i:j])
                dfs(j)
                path.pop()
    if can[0]:
        dfs(0)
    return ans
```

- **词典很大？** 把词典建成 Trie。对每个可行起点 $i$，沿 Trie 扫 `s[i:]`，走到词末就把更远的 `dp` 置真。避免对每个 $(j,i)$ 做切片哈希。时间仍最坏 $O(n^2)$，常数更好。

```python
def wordBreakTrie(s, wordDict):
    trie = {}
    for w in wordDict:
        node = trie
        for ch in w:
            node = node.setdefault(ch, {})
        node["#"] = True
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(n):
        if not dp[i]:
            continue
        node = trie
        j = i
        while j < n and s[j] in node:
            node = node[s[j]]
            j += 1
            if "#" in node:
                dp[j] = True
        if dp[n]:
            return True
    return dp[n]
```
