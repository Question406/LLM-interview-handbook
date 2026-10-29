---
id: meta-shortest-unique-prefix-trie
section: meta
order: 925
level: A
title: "Meta：用 trie 找每个 word 的 shortest unique prefix"
quick: "我会先确认是否允许结束标记。这题不允许，所以 a 和 ab 同时出现时，a 没有可用的唯一 prefix，返回 None 比随便返回 a 更准确。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta：用 trie 找每个 word 的 shortest unique prefix"
    url: "https://landthelab.com/companies/meta"
    type: secondary
---

## 题目描述

来源：Land the Lab 的 Meta 目录列出 shortest unique prefix。下面明确 prefix-of-another-word 的处理与输出规则。

### 输入、接口与规则

实现 `unique_prefixes(words) -> list[str | None]`。输入是互不相同的非空 lowercase ASCII words，最多 100000 个，字符总量不超过 1000000。对每个 word，找一个最短的非空字符串 p，要求 p 是这个 word 的 prefix，而且不是其他任意输入 word 的 prefix。

按输入顺序返回结果；若不存在这样的 p，返回 None。特别地，word="a" 而另一个 word="ab" 时，"a" 的结果为 None；不允许自动追加结束标记。空输入返回空列表，不修改输入。请避免对每对 words 逐一比较，说明如何通过经过 trie node 的 word 数量确定 prefix 唯一性。

### 输入输出示例

```text
words=["dog","dove","duck","a","ab"]
返回 ["dog","dov","du",None,"ab"]。
words=["apple"] -> ["a"]。
```

## 回答思路

> **Situation / Task：** Prefix 必须与所有其他 words 区分；短 word 可能没有答案。  
> **Approach / Why：** Trie node 记录经过的 word 数，首次 count=1 就是最短唯一 prefix。  
> **Result / Check：** 检查 word 是另一个 word 的 prefix、空输入与单 word。

## 解题思路与参考答案

我会先确认是否允许结束标记。这题不允许，所以 a 和 ab 同时出现时，a 没有可用的唯一 prefix，返回 None 比随便返回 a 更准确。

建 trie 时对每个经过的 node 加一；查询时从头走，第一次 count=1 就停止。因为更短的节点 count 都大于一，所以这个 prefix 一定最短。

### 完整参考实现

```python
def unique_prefixes(words):
    children = [{}]
    counts = [0]
    for word in words:
        node = 0
        for char in word:
            if char not in children[node]:
                children[node][char] = len(children)
                children.append({})
                counts.append(0)
            node = children[node][char]
            counts[node] += 1
    result = []
    for word in words:
        node = 0
        answer = None
        for i, char in enumerate(word):
            node = children[node][char]
            if counts[node] == 1:
                answer = word[: i + 1]
                break
        result.append(answer)
    return result
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert unique_prefixes(['dog', 'dove', 'duck', 'a', 'ab']) == [
    'dog',
    'dov',
    'du',
    None,
    'ab',
]
assert unique_prefixes(['apple']) == ['a']
assert unique_prefixes([]) == []
from itertools import product

words = [''.join(chars) for n in range(1, 5) for chars in product('ab', repeat=n)]
for subset in [words, words[::2], words[5:20]]:
    expected = []
    for word in subset:
        candidates = [
            word[:i]
            for i in range(1, len(word) + 1)
            if sum(v.startswith(word[:i]) for v in subset) == 1
        ]
        expected.append(candidates[0] if candidates else None)
    assert unique_prefixes(subset) == expected
print('unique prefix tests passed')
```

## 复杂度与追问

设输入字符总数 L，建树和查询均为 `O(L)`；trie 空间 `O(L)`，生成输出字符串也不超过这个量级。追问重复输入应先决定按 distinct words 还是按记录区分。
