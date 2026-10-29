---
id: lc-1268-search-suggestions-system
section: trie
order: 2
level: A
title: LC 1268 · 搜索推荐系统
quick: >-
  先把 `products` 排序，前缀相同的词会连成一段，每输入一个字符就用二分找第一个 $\ge$ 前缀的位置，往后取最多 $3$
  个以前缀开头的词。前缀只会变长，下界单调右移，可以接着上次的位置二分。时间 $O(n \log n \cdot L + m \log n \cdot
  L)$。
tags:
  - Trie
  - Binary Search
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 1268. Search Suggestions System
    url: 'https://leetcode.com/problems/search-suggestions-system/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定互不相同的产品名称列表 products 和待输入的单词 searchWord。用户从左到右逐个输入 searchWord 的字符，每输入一个字符，就从所有以当前已输入前缀开头的产品中推荐最多三个名称；候选超过三个时，取字典序最小的三个。

### 输入与输出

实现 `suggestedProducts(products: List[str], searchWord: str) -> List[List[str]]`。外层结果长度必须等于 searchWord 的长度，第 i 项对应前 i+1 个字符形成的前缀。每项按字典序排列；候选不足三个时全部返回，没有候选时返回空列表。

### 约束

- `1 <= len(products) <= 1000`，产品名互不相同。
- 每个产品名长度为 1 到 3000，所有产品名总长度不超过 `2 * 10^4`。
- `1 <= len(searchWord) <= 1000`，所有名称与 searchWord 只含小写英文字母。

### 示例

```text
输入：products = ["mobile","mouse","moneypot","monitor","mousepad"], searchWord = "mouse"
输出：[["mobile","moneypot","monitor"],["mobile","moneypot","monitor"],["mouse","mousepad"],["mouse","mousepad"],["mouse","mousepad"]]
```

输入前缀 m、mo 时各有至少三个候选；前缀变成 mou、mous、mouse 后，只剩 mouse 和 mousepad。

## 解题思路与参考答案

## 题意

给字符串数组 `products` 和 `searchWord`。每输入 `searchWord` 的一个字符，就返回最多 $3$ 个以当前前缀开头的产品名，多于 $3$ 个时取字典序最小的 $3$ 个。返回长度为 `len(searchWord)` 的列表的列表。字符都是小写字母，产品名互不相同。

## 思路

我会先排序再二分。排序后，所有以 `prefix` 开头的词在数组里是连续的一段，段首就是第一个字典序 $\ge$ `prefix` 的位置。所以每个前缀用 `bisect_left` 找段首，取 `products[lo:lo+3]` 里以 `prefix` 开头的就行；段内已按字典序排好，前 $3$ 个就是答案。前缀每次只加一个字符，新段首不会比旧段首靠前，二分的下界可以沿用上次的 `lo`。

拿示例走一遍。排序后是 `mobile`、`moneypot`、`monitor`、`mouse`、`mousepad`。前缀 `m` 和 `mo` 的段首都是下标 0，取 `mobile`、`moneypot`、`monitor`。前缀 `mou` 的段首跳到下标 3，只剩 `mouse`、`mousepad` 两个匹配，`mous`、`mouse` 也一样。

Trie 也能做。每个节点缓存经过它的字典序最小的 $3$ 个词，插入时按排序后的顺序插入，节点列表不满 $3$ 就追加；查询沿 `searchWord` 走，走空之后的前缀都返回空列表。两种都行，排序加二分代码短、不容易写错，我会先写它，再说 Trie 版在产品列表固定、查询很多时更合适。

## 参考代码

```python
from bisect import bisect_left
from typing import List


def suggestedProducts(products: List[str], searchWord: str) -> List[List[str]]:
    products = sorted(products)
    ans: List[List[str]] = []
    lo = 0
    prefix = ""
    for ch in searchWord:
        prefix += ch
        lo = bisect_left(products, prefix, lo)
        ans.append([w for w in products[lo : lo + 3] if w.startswith(prefix)])
    return ans


if __name__ == "__main__":
    products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
    assert suggestedProducts(products, "mouse") == [
        ["mobile", "moneypot", "monitor"],
        ["mobile", "moneypot", "monitor"],
        ["mouse", "mousepad"],
        ["mouse", "mousepad"],
        ["mouse", "mousepad"],
    ]
    assert suggestedProducts(["havana"], "havana") == [["havana"]] * 6
    assert suggestedProducts(
        ["bags", "baggage", "banner", "box", "cloths"], "bags"
    ) == [
        ["baggage", "bags", "banner"],
        ["baggage", "bags", "banner"],
        ["baggage", "bags"],
        ["bags"],
    ]
    assert suggestedProducts(["havana"], "tatiana") == [[]] * 7
    assert suggestedProducts(["abc", "ab"], "abcd") == [
        ["ab", "abc"],
        ["ab", "abc"],
        ["abc"],
        [],
    ]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
assert suggestedProducts(products, "mouse") == [
    ["mobile", "moneypot", "monitor"],
    ["mobile", "moneypot", "monitor"],
    ["mouse", "mousepad"],
    ["mouse", "mousepad"],
    ["mouse", "mousepad"],
]
assert suggestedProducts(["havana"], "havana") == [["havana"]] * 6
assert suggestedProducts(["bags", "baggage", "banner", "box", "cloths"], "bags") == [
    ["baggage", "bags", "banner"],
    ["baggage", "bags", "banner"],
    ["baggage", "bags"],
    ["bags"],
]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

设产品数 $n$，词长上限 $L$，`searchWord` 长 $m$。排序 $O(n \log n \cdot L)$；每个前缀二分 $O(\log n \cdot L)$，再检查至多 $3$ 个词。额外空间 $O(n)$ 用于排序副本，不计答案。

## Edge Cases

某个前缀已经没有匹配时，之后所有前缀都返回空列表；二分落在段外，`startswith` 会过滤掉。

产品本身是另一个产品的前缀时，比如 `"ab"` 和 `"abc"`，短的排在前面，两个都能被选中。

匹配数不足 $3$ 时切片后过滤，只返回实际匹配的。

## 追问

**Trie 版怎么写？**
排序后按序插入，每个节点的 `top` 只保留前 $3$ 个，天然就是字典序最小的。查询沿字符走，走丢后剩下的位置补空列表。建树 $O(\sum L)$，查询 $O(m)$。

```python
def suggestedProductsTrie(products, searchWord):
    root = {}
    for w in sorted(products):
        node = root
        for ch in w:
            node = node.setdefault(ch, {"#": []})
            if len(node["#"]) < 3:
                node["#"].append(w)
    ans, node = [], root
    for ch in searchWord:
        node = node.get(ch) if node else None
        ans.append(node["#"] if node else [])
    return ans
```

**不用二分，双指针能做吗？**
可以。排序后维护 `[l, r]` 区间，每读入第 $i$ 个字符，`l` 右移跳过长度不够或第 $i$ 位小于该字符的词，`r` 左移跳过第 $i$ 位大于该字符的词。区间只会收缩，总移动 $O(n)$，每步比较 $O(1)$。Trie 基础结构见 `lc-208-implement-trie-prefix-tree`。
