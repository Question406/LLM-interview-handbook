---
id: lc-208-implement-trie-prefix-tree
section: trie
order: 1
level: S
title: LC 208 · 实现 Trie (前缀树)
quick: >-
  用一棵 26 叉（或哈希）前缀树，每个节点存孩子表和词尾标记 `is_end`。`insert` 沿路建节点、最后标词尾，`search` 要走到词尾标记才算，`startsWith` 走完前缀就行。三种操作都是 $O(L)$。
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

## 题目描述

实现保存小写英文单词的前缀树 Trie。它需要区分“完整单词已经插入”和“存在以某前缀开头的单词”，后者为 True 不代表这个前缀本身已作为完整单词插入。

### 接口与输出

提供 `Trie()`、`insert(word: str) -> None`、`search(word: str) -> bool`、`startsWith(prefix: str) -> bool`。insert 加入一个完整单词；search 检查完整匹配；startsWith 检查是否至少有一个已插入单词以 prefix 开头。重复插入合法，不会改变查询含义。

### 合法输入与约束

word 与 prefix 长度均为 1 到 2000，只含小写英文字母。三个方法合计调用不超过 30000 次。示例的操作和参数数组逐项对应；构造器及 insert 的 `null` 输出表示无返回值。

### 示例

```text
输入：["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]
输出：[null, null, true, false, true, null, true]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/implement-trie-prefix-tree/description/)。

## 解题思路与参考答案

## 题意

实现 `Trie`：`insert(word)`、`search(word)`（整词是否插入过）、`startsWith(prefix)`（是否存在以该前缀开头的已插入词）。字符为小写字母，词长 $[1, 2000]$，总调用次数不超过 $3 \times 10^4$。

## 思路

我会用前缀树，每个节点挂一张孩子表（长度 $26$ 的数组或哈希）和一个布尔 `is_end`。选它是因为公共前缀会合并成一条路径，查整词和查前缀都只要沿着字符走一遍，都是 $O(L)$。用哈希集合存所有词也能 $O(L)$ 判整词，可查前缀就得扫全部词。

拿测试里的例子走一遍。插入 `"apple"`，从根出发依次建 a、p、p、l、e 五个节点，最后的 e 节点标 `is_end=True`。这时 `search("app")` 能走完三步，停在第二个 p 上，但那里 `is_end` 是假，所以返回假；`startsWith("app")` 只要求走得完，返回真。再 `insert("app")`，路径已经在了，只把第二个 p 的 `is_end` 置真，`search("app")` 就变成真。`app` 和 `apple` 能共存全靠 `is_end`：走到空孩子说明路径不存在，走到了但不是词尾说明它只是个前缀，这两种情况要分开判断。

所以三个操作共用一个 `_walk`，沿字符往下走，缺孩子就返回 `None`。插入时缺了就新建，最后标词尾；查整词要走完并且 `is_end` 为真；查前缀走完就行。白板上我会先画一条链，再画分叉。

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

设词长 $L$。三次操作都是 $O(L)$。空间与插入过的字符节点数成正比，最坏为所有词长之和乘以每节点的孩子表大小。

## 边界

空前缀时 `_walk("")` 停在根，`startsWith` 返回真，因为任何词都以空串为前缀。

短词是长词前缀的情况就是上面那个例子：只插了 `"apple"` 时 `search("app")` 为假、`startsWith("app")` 为真，再 `insert("app")` 之后短词的 `is_end` 才变真。

同一个词重复插入时路径已经存在，只是再置一次 `is_end`，所以插入是幂等的。

## 追问

**怎么删除单词？**
递归走到词尾把 `is_end` 置假，回溯时再剪掉没用的节点。整条链不能直接砍，因为这个词可能是别的词的前缀。走到词尾时如果该节点不是 `is_end`，说明词不存在；否则把它置假。回溯时，孩子节点如果既不是词尾、又没有孩子，就从父节点删掉。如果允许同一个词插入多次，就改用 `end_cnt` / 经过计数，减到 $0$ 才清词尾。

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

**带 `'.'` 通配符的搜词怎么做（LC 211）？**
普通字母照常走固定边，遇到 `'.'` 就对当前节点的所有孩子做 DFS，走到串尾看 `is_end`。最坏情况是 $26^L$。

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

**前缀树还能用在哪？**
搜索推荐（`lc-1268-search-suggestions-system`）也能用，每个节点缓存前 $3$ 个词。
