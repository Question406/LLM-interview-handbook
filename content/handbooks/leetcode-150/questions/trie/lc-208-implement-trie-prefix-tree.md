---
id: lc-208-implement-trie-prefix-tree
section: trie
order: 1
level: S
title: LC 208 · 实现 Trie (前缀树)
quick: "用 26 叉（或哈希）前缀树，每个节点带一个词尾标记 `is_end`。`insert` 沿路建节点并标词尾；`search` 必须走到带词尾标记的节点；`startsWith` 走完前缀就算成功。"
tags:
  - Trie
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 208. 实现 Trie (前缀树)
    url: https://leetcode.cn/problems/implement-trie-prefix-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

设计一个保存单词的数据结构，支持插入完整单词、查询完整单词是否存在，以及查询是否存在具有给定前缀的单词。仅仅是某个已插入单词的前缀，不代表这个短字符串本身已经作为完整单词插入。

### 输入与输出

实现 `Trie()`、`insert(word) -> None`、`search(word) -> bool`、`startsWith(prefix) -> bool`。重复插入同一单词合法。示例按两行列表给出操作名和参数，null 表示构造或无返回值的调用。

### 约束

- `1 <= len(word), len(prefix) <= 2000`。
- word 与 prefix 只包含小写英文字母。
- 三种操作的总调用次数至多为 `3 * 10^4`。

### 示例

```text
输入：["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]
输出：[null, null, true, false, true, null, true]
```

[LeetCode 原题](https://leetcode.com/problems/implement-trie-prefix-tree/description/)

## 解题思路与参考答案

## 题意

实现 `Trie`：`insert(word)`、`search(word)`（整词是否插入过）、`startsWith(prefix)`（是否存在以该前缀开头的已插入词）。字符为小写字母。

## 思路

我会用前缀树，每个节点挂一排孩子（长度 $26$ 的数组或哈希）和一个布尔 `is_end`。插入时沿字符往下走，缺了就新建，最后一个节点标 `is_end=True`。查整词要走完并且 `is_end` 为真；查前缀只要能走完，不必是词尾。

讲的时候我会先画一条链，再讲分叉。比如只插了 `apple`，`search("app")` 能走完三个字符，但停下的节点 `is_end` 是假，返回假；`startsWith("app")` 走完就算，返回真。再 `insert("app")` 以后，那个节点被标成词尾，`search("app")` 才变成真。`app` 和 `apple` 能共存就靠 `is_end`。「走到空孩子」和「走到了但不是词尾」是两种情况，别混在一起。

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
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
t = Trie()
t.insert("apple")
assert t.search("apple") is True
assert t.search("app") is False
assert t.startsWith("app") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

设词长 $L$。三次操作都是 $O(L)$。空间与插入过的字符节点数成正比。

## 边界

空前缀时 `_walk("")` 停在根，`startsWith` 为真，因为任何词都以空串为前缀。

短词是长词前缀的情况，上面 `app` 和 `apple` 已经走过了。判断词尾只看 `is_end`，用「有没有孩子」判断会出错：只插过 `apple` 时，`app` 那个节点有孩子，却不是一个词。

## 追问

**怎么删除单词？**
用递归，不能整条链砍掉，因为这个词可能是别的词的前缀。走到词尾时，如果节点不是 `is_end`，说明词不存在；否则把 `is_end` 置假。回溯的时候，孩子节点既不是词尾、又没有孩子，就从父节点删掉。允许同一个词插入多次时，改用 `end_cnt` 或经过计数，减到 $0$ 才清词尾。

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

**带 `'.'` 通配的搜词呢？**
普通字母照样走固定边；遇到 `'.'` 就对当前节点的所有孩子 DFS，走到串尾看 `is_end`，最坏 $26^L$。这就是 LC 211，独立卡 `lc-211-design-add-and-search-words-data-structure`。在网格里一次搜多个词是 LC 212，独立卡 `lc-212-word-search-ii`。

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
