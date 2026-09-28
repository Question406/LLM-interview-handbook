---
id: lc-1268-search-suggestions-system
section: trie
order: 2
level: A
title: LC 1268 · 搜索推荐系统
quick: >-
  先把 `products` 排序，前缀相同的词会连成一段。每输入一个字符，用二分找第一个 $\ge$ 前缀的位置，往后取最多
  $3$ 个以前缀开头的词。下界单调右移，可以接着上次的位置二分。时间 $O(n \log n \cdot L + m \log n \cdot L)$。
tags:
  - Trie
  - Binary Search
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1268. Search Suggestions System
    url: https://leetcode.com/problems/search-suggestions-system/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给字符串数组 `products` 和 `searchWord`。每输入 `searchWord` 的一个字符，就返回最多 $3$ 个以当前前缀开头的产品名，多于 $3$ 个时取字典序最小的 $3$ 个。返回长度为 `len(searchWord)` 的列表的列表。字符都是小写字母，产品名互不相同。

## 思路

排序后，所有以 `prefix` 开头的词在数组里是连续的一段，而且段首就是第一个字典序 $\ge$ `prefix` 的位置。所以每个前缀用 `bisect_left` 找段首，取 `products[lo:lo+3]` 中以 `prefix` 开头的即可；段内已按字典序排好，前 $3$ 个就是答案。前缀每次只加一个字符，新段首不会比旧段首靠前，二分的下界可以沿用上次的 `lo`。

Trie 做法：每个节点缓存经过它的字典序最小的 $3$ 个词，插入时按排序后的顺序插入，节点列表不满 $3$ 就追加。查询沿 `searchWord` 走，走空之后的前缀都返回空列表。两种都行，排序加二分代码短、不容易写错，我会先写它，再说 Trie 版在产品列表固定、查询很多时更合适。

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
        ans.append([w for w in products[lo:lo + 3] if w.startswith(prefix)])
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
    assert suggestedProducts(["bags", "baggage", "banner", "box", "cloths"], "bags") == [
        ["baggage", "bags", "banner"],
        ["baggage", "bags", "banner"],
        ["baggage", "bags"],
        ["bags"],
    ]
    assert suggestedProducts(["havana"], "tatiana") == [[]] * 7
    assert suggestedProducts(["abc", "ab"], "abcd") == [["ab", "abc"], ["ab", "abc"], ["abc"], []]
    print("ok")
```

## 复杂度

设产品数 $n$，词长上限 $L$，`searchWord` 长 $m$。排序 $O(n \log n \cdot L)$；每个前缀二分 $O(\log n \cdot L)$，再检查至多 $3$ 个词。额外空间 $O(n)$ 用于排序副本，不计答案。

## 边界

- 某个前缀已无匹配：之后所有前缀都返回空列表，二分落在段外，`startswith` 过滤掉。
- 产品本身是另一个产品的前缀，如 `"ab"` 和 `"abc"`：短的排在前面，都能被选中。
- 匹配数不足 $3$：切片后过滤，只返回实际匹配的。

## 追问

- **Trie 版怎么写？** 排序后按序插入，每个节点的 `top` 只保留前 $3$ 个，天然就是字典序最小的。查询沿字符走，走丢后剩下的位置补空列表。建树 $O(\sum L)$，查询 $O(m)$。

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

- **不用二分，双指针能做吗？** 可以。排序后维护 `[l, r]` 区间，每读入第 $i$ 个字符，`l` 右移跳过长度不够或第 $i$ 位小于该字符的词，`r` 左移跳过第 $i$ 位大于该字符的词。区间只会收缩，总移动 $O(n)$，每步比较 $O(1)$。Trie 基础结构见 `lc-208-implement-trie-prefix-tree`。
