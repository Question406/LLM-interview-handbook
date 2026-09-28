---
id: lc-208-implement-trie-prefix-tree
section: trie
order: 1
level: S
title: LC 208 · 实现 Trie (前缀树)
quick: >-
  26 叉（或哈希）前缀树。`insert` 沿路建节点并标词尾；`search` 必须走到词尾标记；`startsWith`
  走到前缀即可。三种操作都是 $O(L)$。
tags:
  - Trie
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 208. Implement Trie (Prefix Tree)
    url: https://leetcode.com/problems/implement-trie-prefix-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

实现 `Trie`：`insert(word)`、`search(word)`（整词是否插入过）、`startsWith(prefix)`（是否存在以该前缀开头的已插入词）。字符为小写字母，词长 $[1, 2000]$，总调用次数不超过 $3 \times 10^4$。

## 思路

每个节点挂一排孩子（数组 $26$ 或哈希）和布尔 `is_end`。插入：沿字符走，缺了就新建，最后一个节点 `is_end=True`。查找整词：走完且 `is_end`。查前缀：走完即可，不必是词尾。

`app` 与 `apple` 共存靠 `is_end` 区分，别把「走到空孩子」和「不是词尾」混为一谈。用哈希集合存所有词也能 $O(L)$ 判整词，但查前缀要扫全部词；Trie 把公共前缀合并成一条路径，前缀查询也是 $O(L)$。我会先画一条链，再讲分叉。

## 参考代码

```python
class Trie:
    def __init__(self):
        self.children = {}
        self.is_end = False

    def insert(self, word: str) -> None:
        node = self
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Trie()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return bool(node and node.is_end)

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, s: str):
        node = self
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node


if __name__ == "__main__":
    t = Trie()
    t.insert("apple")
    assert t.search("apple") is True
    assert t.search("app") is False
    assert t.startsWith("app") is True
    t.insert("app")
    assert t.search("app") is True
    assert t.search("apples") is False
    assert t.startsWith("b") is False
    t.insert("apple")
    assert t.search("apple") is True
    print("ok")
```

## 复杂度

设词长 $L$。三次操作都是 $O(L)$。空间与插入过的字符节点数成正比，最坏为所有词长之和乘以每节点的孩子表大小。

## 边界

- 空前缀：`_walk("")` 停在根，`startsWith` 为真（任何词都以空串为前缀）。
- 短词是长词前缀：只插了 `"apple"` 时 `search("app")` 为假，`startsWith("app")` 为真；再 `insert("app")` 后短词 `is_end` 才变真。
- 同一个词重复插入：路径已存在，只是再置一次 `is_end`，幂等。

## 追问

- **如何删除单词？** 词可能是别的词的前缀，不能整链砍掉。递归走到词尾：若该节点不是 `is_end` 则词不存在；否则把 `is_end` 置假。回溯时，若孩子节点「既非词尾、又无孩子」，从父节点删掉。允许同一词插入多次时，改用 `end_cnt` / 经过计数，减到 $0$ 才清词尾。

```python
def delete(self, word: str) -> bool:
    def dfs(node, i):
        if i == len(word):
            if not node.is_end:
                return False
            node.is_end = False
            return not node.children
        ch = word[i]
        if ch not in node.children:
            return False
        prune = dfs(node.children[ch], i + 1)
        if prune:
            del node.children[ch]
        return (not node.is_end) and (not node.children)

    return dfs(self, 0)
```

- **带 `'.'` 的通配搜词（LC 211）？** 普通字母仍走固定边；遇到 `'.'` 对当前节点所有孩子 DFS，走到串尾看 `is_end`。最坏 $26^L$。前缀树在搜索推荐（`lc-1268-search-suggestions-system`）里也能用，每个节点缓存前 $3$ 个词。

```python
def searchWildcard(self, word: str) -> bool:
    def dfs(node, i):
        if i == len(word):
            return node.is_end
        ch = word[i]
        if ch == ".":
            return any(dfs(child, i + 1) for child in node.children.values())
        if ch not in node.children:
            return False
        return dfs(node.children[ch], i + 1)

    return dfs(self, 0)
```
