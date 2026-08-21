---
id: lc-211-design-add-and-search-words-data-structure
section: trie
order: 2
level: A
title: LC 211 · 添加与搜索单词 - 数据结构设计
quick: >-
  Trie 存词。`search` 遇 `'.'` 表示任意字母，对当前节点所有孩子 DFS；其余字符与普通
  Trie 一样走固定边。
tags:
  - Trie
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 211. 添加与搜索单词 - 数据结构设计
    url: https://leetcode.cn/problems/design-add-and-search-words-data-structure/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

实现 `WordDictionary`：`addWord(word)` 加词；`search(word)` 判断是否匹配任一已加词。模式串里 `'.'` 可匹配任意一个字母。

## 思路

底层仍是前缀树。`addWord` 与 LC 208 的 `insert` 相同。`search` 改成 DFS：普通字母只走对应孩子；遇到 `'.'` 则枚举当前节点全部孩子。走到串尾时看 `is_end`。

不要把整棵树展成正则去扫。面试讲清「通配只在当前层分叉」，并提最坏 $26^L$。

## 参考代码

```python
class WordDictionary:
    def __init__(self):
        self.children = {}
        self.is_end = False

    def addWord(self, word: str) -> None:
        node = self
        for ch in word:
            if ch not in node.children:
                node.children[ch] = WordDictionary()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        def dfs(node: "WordDictionary", i: int) -> bool:
            if i == len(word):
                return node.is_end
            ch = word[i]
            if ch == ".":
                return any(dfs(child, i + 1) for child in node.children.values())
            if ch not in node.children:
                return False
            return dfs(node.children[ch], i + 1)

        return dfs(self, 0)


if __name__ == "__main__":
    d = WordDictionary()
    d.addWord("bad")
    d.addWord("dad")
    d.addWord("mad")
    assert d.search("pad") is False
    assert d.search("bad") is True
    assert d.search(".ad") is True
    assert d.search("b..") is True
    print("ok")
```

## 复杂度

`addWord` $O(L)$。`search` 无通配 $O(L)$，全是 `'.'` 时最坏 $O(26^L)$。空间同插入节点数。

## 边界

- 只搜未加过的词：普通路径走丢或走到尾但 `is_end` 为假，返回假。
- 模式全是点且长度刚好匹配：`'.'` 每层枚举全部孩子，等于「是否存在该长度的词」。
- 短于 / 长于已加词：长度必须一致，前缀不是命中（没有 `startsWith`）。无通配的整词 / 前缀查询见 LC 208，独立卡 `lc-208-implement-trie-prefix-tree`。

## 追问

- **`'*'` 匹配任意长度（含空）？** 比 `'.'` 多一个「吃多少字符」的选择。在当前节点面对 `'*'`：
  1. 匹配空串，跳过 `'*'`，继续 `word[i+1]`；
  2. 吃掉一个孩子字母，**仍停在同一个 `'*'`**，以便继续吃。
  可与 `'.'` 并存。这是 glob 语义，不是正则里「前面那个字符重复」。最坏指数级，可用记忆化 `(id(node), i)`。

```python
def searchGlob(self, word: str) -> bool:
    def dfs(node, i):
        if i == len(word):
            return node.is_end
        ch = word[i]
        if ch == "*":
            if dfs(node, i + 1):
                return True
            return any(dfs(child, i) for child in node.children.values())
        if ch == ".":
            return any(dfs(child, i + 1) for child in node.children.values())
        if ch not in node.children:
            return False
        return dfs(node.children[ch], i + 1)

    return dfs(self, 0)
```

- **网格上一次搜很多词？** 通配是「模式对 Trie 分叉」；多词搜索是「棋盘 DFS 沿 Trie 往下走」。把 `words` 建成 Trie，从每个格子出发，字母不在当前孩子里就剪。即 LC 212，独立卡 `lc-212-word-search-ii`。一词一搜则退回 LC 79，独立卡 `lc-79-word-search`。
