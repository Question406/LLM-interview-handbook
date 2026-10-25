---
id: lc-211-design-add-and-search-words-data-structure
section: trie
order: 2
level: A
title: LC 211 · 添加与搜索单词 - 数据结构设计
quick: "底层还是 Trie，`addWord` 和普通插入一样。`search` 改成 DFS：普通字符走固定边，遇到 `'.'` 表示任意字母，就对当前节点所有孩子分叉。全是 `'.'` 时最坏 $O(26^L)$。"
tags:
  - Trie
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 211. 添加与搜索单词 - 数据结构设计
    url: https://leetcode.cn/problems/design-add-and-search-words-data-structure/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

设计一个单词容器，支持添加单词和按模式查询。查询模式中的普通字母必须与对应位置的字母相同，`.` 可以匹配恰好一个任意小写字母；必须匹配某个已添加单词的全部字符，不能只匹配前缀或子串。

### 输入与输出

实现 `WordDictionary`：构造器创建空容器；`addWord(word: str) -> None` 添加一个单词；`search(word: str) -> bool` 判断是否至少存在一个已添加单词与查询模式完整匹配。

### 约束

- 单词或查询模式长度为 1 到 25。
- 添加的单词仅含小写英文字母；查询仅含小写字母或 `.`，且最多含两个点。
- 添加与查询合计最多调用 `10^4` 次。

### 示例

```text
输入：["WordDictionary","addWord","addWord","addWord","search","search","search","search"]
[[],["bad"],["dad"],["mad"],["pad"],["bad"],[".ad"],["b.."]]
输出：[null,null,null,null,false,true,true,true]
```

构造器和 addWord 的输出在操作序列中记为 null。添加 bad、dad、mad 后，`.ad` 与 `b..` 均有完整匹配，pad 没有。

## 解题思路与参考答案

## 题意

实现 `WordDictionary`：`addWord(word)` 加词；`search(word)` 判断是否匹配任一已加词。模式串里 `'.'` 可匹配任意一个字母。

## 思路

底层还是前缀树，`addWord` 和 LC 208 的 `insert` 一样，要改的只有 `search`。我会把它写成 DFS：普通字母只走对应的孩子，遇到 `'.'` 就枚举当前节点的全部孩子，走到串尾看 `is_end`。通配只在当前这一层分叉，用不着把整棵树展成正则去扫。最坏是全是 `'.'` 的情况，要走 $26^L$，这个我会主动提。

拿样例看。加了 `bad`、`dad`、`mad` 以后，搜 `pad`，根下面没有 `p`，直接返回假。搜 `.ad`，第一层的 `'.'` 分别试 `b`、`d`、`m`，走 `b` 那条就能接上 `a`、`d`，而且是词尾，返回真。`b..` 先走固定的 `b`，后面两层各自枚举，也能命中 `bad`。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
d = WordDictionary()
d.addWord("bad")
d.addWord("dad")
d.addWord("mad")
assert d.search("pad") is False
assert d.search("bad") is True
assert d.search(".ad") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`addWord` $O(L)$。`search` 无通配 $O(L)$，全是 `'.'` 时最坏 $O(26^L)$。空间同插入节点数。

## 边界

搜一个没加过的词，要么普通路径中途走丢，要么走到尾但 `is_end` 为假，都返回假。

模式全是点、长度又刚好时，每层枚举全部孩子，相当于问「有没有这个长度的词」。

模式比已加的词短或长都不算命中。长度必须一致，这里没有 `startsWith`，前缀不算。无通配的整词、前缀查询见 LC 208，独立卡 `lc-208-implement-trie-prefix-tree`。

## 追问

**`'*'` 匹配任意长度（含空）怎么做？**
比 `'.'` 多一个「吃几个字符」的选择。当前节点遇到 `'*'` 有两条路：一条是匹配空串，跳过 `'*'`，继续看 `word[i+1]`；另一条是吃掉一个孩子字母，但**仍停在同一个 `'*'`** 上，这样还能继续往下吃。它可以和 `'.'` 并存。这是 glob 语义，和正则里「前面那个字符重复」的 `*` 不一样。最坏是指数级，可以用 `(id(node), i)` 做记忆化。

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

**网格上一次搜很多词呢？**
方向换过来了。通配是模式在 Trie 上分叉；多词搜索是在棋盘上 DFS，同时沿 Trie 往下走。把 `words` 建成 Trie，从每个格子出发，字母不在当前节点的孩子里就剪掉。这就是 LC 212，独立卡 `lc-212-word-search-ii`。只搜一个词就退回 LC 79，独立卡 `lc-79-word-search`。
