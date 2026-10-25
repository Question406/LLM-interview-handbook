---
id: lc-139-word-break
section: dp-1d
order: 3
level: A
title: LC 139 · 单词拆分
quick: "用前缀 DP：$dp[i]$ 表示前 $i$ 个字符能否拆成词典单词，$dp[0]$ 为真。对每个 $i$ 枚举切分点 $j$，$dp[j]$ 为真且 $s[j:i]$ 在词典里，$dp[i]$ 就为真。时间约 $O(n^2)$，可用最大词长截断内层。"
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

## 题目描述

给定字符串 s 与单词列表 wordDict，判断能否把整个 s 分成一个或多个连续片段，使每个片段都是词典中的一个单词。片段必须不重叠且完整覆盖 s；同一个词典单词允许反复使用。

### 输入与输出

实现 `wordBreak(s, wordDict) -> bool`。能完整切分返回 True，否则返回 False；不需要返回具体切分方法。

### 约束与约定

- `1 <= len(s) <= 300`。
- 词典有 1 到 1000 个不同单词，每个词长 1 到 20。
- s 与词典单词都只含小写英文字母。

### 示例

```text
输入：s = "leetcode", wordDict = ["leet","code"]
输出：true
```

示例可分成 leet 和 code，两个部分都在词典中。

[官方原题与完整题面](https://leetcode.com/problems/word-break/description/)。

## 解题思路与参考答案

## 题意

给字符串 `s` 和单词表 `wordDict`，判断 `s` 能否用空格切成若干个词典单词，单词可以重复用。

## 思路

我会用前缀 DP。整串能不能拆，取决于某个前缀能拆、并且剩下的最后一段正好是个词，这就是天然的子问题。

定义 $dp[i]$ 为前 $i$ 个字符能否由词典单词拼成。空前缀可行，所以 $dp[0]=\mathrm{true}$。对右端 $i$ 枚举切分点 $j\lt i$：前半段可行，即 `dp[j]`，并且最后一段 `s[j:i]` 在词典里，就有 `dp[i]=True`。最终看 $dp[n]$。拿 `leetcode` 和 `["leet", "code"]` 来说，$dp[4]$ 因为 `leet` 为真；到 $i=8$ 时取 $j=4$，`dp[4]` 为真且 `code` 在词典里，所以 $dp[8]$ 为真。

词典先放进 `set`，查词是 $O(1)$；用词典里最长词的长度还能限制内层循环。BFS 或记忆化搜索也能做，本质上同样是在问「这个前缀能不能拆」。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert wordBreak("leetcode", ["leet", "code"]) is True
assert wordBreak("applepenapple", ["apple", "pen"]) is True
assert wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2\cdot L)$，$L$ 是切片哈希的代价；额外空间 $O(n+|dict|)$。用最大词长截断内层，可以压到 $O(n\cdot maxlen)$。

## 边界

`s` 本身就是一个词时，`j=0` 那次 `s[0:n]` 就在词典里，`dp[n]` 直接为真。词典词比 `s` 还长也不影响正确性，切片对不上而已，可以用最大词长把内层截断。完全拼不出时，除 `dp[0]` 外全是假，返回 `False`。

## 追问

**要输出一种或全部拆法（LC 140）怎么办？**
布尔 DP 只回答能不能，要拆法就得回溯。先倒着算后缀可行性 `can[i]`，即 `s[i:]` 能否拆；再从下标 $0$ 回溯，只沿 `can[j]` 为真且 `s[i:j]` 在词典里的切分往下走，走到 $n$ 就把路径用空格拼成句子。只要一种的话，搜到就返回。最坏情况下方案数是指数级的。

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

**词典很大怎么办？**
把词典建成 Trie。对每个可行的起点 $i$，沿 Trie 往后扫 `s[i:]`，每走到一个词尾就把对应的更远的 `dp` 置真，这样省掉了对每个 $(j,i)$ 做切片哈希。最坏时间仍是 $O(n^2)$，常数更好。

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
