---
id: xai-offline-autocomplete-trie
section: xai
order: 900
level: A
title: "xAI：Offline autocomplete 的 prefix top-K index"
quick: "我会把 UI 的输入处理与本地 prefix index 分开。Index 用 trie 找 prefix，每个节点缓存少量最高分候选，查询就不需要扫描全部单词。"
companies:
  - xai
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "候选人报告的二手题型：offline autocomplete"
    url: "https://aceoffer.app/interviews/xai_autocomplete_input_box"
    type: interview
---

## 题目描述

来源：AceOffer 的候选人题型目录列出 Autocomplete Input Box (Local Data, Offline-Safe)。下面实现其本地索引部分，ranking、更新和容量规则由手册设定。

### 输入、接口与规则

实现 `Autocomplete(limit=3)`。`add(word,score)` 接收非空字符串和非负整数分数；重复添加保留该 word 的最大分数，不累加、不降分。大小写敏感，按 Python 字符顺序处理，无网络请求。limit 是正整数。

`suggest(prefix,k=3)` 返回最多 k 个 `(word,score)`，word 以 prefix 开头，按 score 降序、同分 word 升序；空 prefix 查询全词典，未知 prefix 返回空列表。k 为 0..limit，越界抛 ValueError；limit 小于 3 时调用者应显式传入合法 k。不要求删除、降分、fuzzy match、UI debounce 或请求取消。

构建 trie，并在每个 prefix 节点维护最多 limit 个候选，让查询不扫描整个词典。更新后必须立即得到最新 ranking。接口返回新列表，调用者不得修改对象内部状态。

### 输入输出示例

```text
add("car",3), add("cat",5), add("cab",5)
suggest("ca") -> [("cab",5),("cat",5),("car",3)]
再 add("car",8)，suggest("ca",2) -> [("car",8),("cab",5)]。
```

## 回答思路

> **输入与任务：** 补全来自本地词典，先定义大小写、同分与更新规则。  
> **做法与原因：** 沿 word 路径更新 prefix 的 top-K 缓存，查询直接走 trie。  
> **正确性检查：** 把每次更新后的结果与全词典扫描排序作对照。

## 解题思路与参考答案

我会把 UI 的输入处理与本地 prefix index 分开。Index 用 trie 找 prefix，每个节点缓存少量最高分候选，查询就不需要扫描全部单词。

更新一个 word 时，只需修它经过的各个 prefix。这里分数只会上升，所以旧 top-K 加上这个 word 就足够重新排序；允许降分或删除时，这个维护方式需要改变。

### 完整参考实现

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.best = []


class Autocomplete:
    def __init__(self, limit=3):
        if type(limit) is not int or limit < 1:
            raise ValueError("limit must be positive")
        self.limit = limit
        self.root = TrieNode()
        self.scores = {}

    def add(self, word, score):
        if not isinstance(word, str) or not word or type(score) is not int or score < 0:
            raise ValueError("expected nonempty string and nonnegative integer")
        self.scores[word] = max(self.scores.get(word, 0), score)
        node = self.root
        path = [node]
        for char in word:
            node = node.children.setdefault(char, TrieNode())
            path.append(node)
        for node in path:
            candidates = set(node.best)
            candidates.add(word)
            node.best = sorted(candidates, key=lambda w: (-self.scores[w], w))[
                : self.limit
            ]

    def suggest(self, prefix, k=3):
        if type(k) is not int or not 0 <= k <= self.limit:
            raise ValueError("k must be between 0 and limit")
        node = self.root
        for char in prefix:
            node = node.children.get(char)
            if node is None:
                return []
        return [(word, self.scores[word]) for word in node.best[:k]]
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
index = Autocomplete(limit=3)
for word, score in [("car", 3), ("cat", 5), ("cab", 5), ("dog", 10)]:
    index.add(word, score)
assert index.suggest("ca") == [("cab", 5), ("cat", 5), ("car", 3)]
assert index.suggest("", 2) == [("dog", 10), ("cab", 5)]
assert index.suggest("missing") == [] and index.suggest("ca", 0) == []
index.add("car", 8)
index.add("car", 1)
assert index.suggest("ca") == [("car", 8), ("cab", 5), ("cat", 5)]
# Compare cached prefix results with a complete dictionary scan after updates.
import random

rng = random.Random(8)
for _ in range(150):
    word = "".join(rng.choices("abcd", k=rng.randint(1, 5)))
    index.add(word, rng.randrange(20))
    prefix = word[: rng.randrange(len(word) + 1)]
    expected = sorted(
        [(w, s) for w, s in index.scores.items() if w.startswith(prefix)],
        key=lambda item: (-item[1], item[0]),
    )[:3]
    assert index.suggest(prefix) == expected
print("xAI offline autocomplete: passed")
```

## 复杂度与追问

查询约 `O(len(prefix)+k)`；单次更新长度 L 时约 `O(L*limit*log(limit))`。缓存空间约 `O(节点数*limit)`。完整前端的 stale response、debounce 和取消见现有 `p3a-xai-input-field-review`。
