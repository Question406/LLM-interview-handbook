---
id: p3a-xai-common-ngrams
section: xai
order: 750
level: S
title: "xAI：高频 N-grams：边界、计数与确定性排序"
quick: "对每篇文档滑动长度为 n 的窗口、用 tuple 计数后取前 k 个；原题只有标题线索，按字节还是按词、能否跨文档都要先问清楚。"
companies:
  - xai
tags:
  - xAI
  - Coding
  - Frontier-2026-10
  - 完整编程练习
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: 1Point3Acres xAI source
    url: https://www.1point3acres.com/interview/problems/4ccdfde5-3895-413d-afaf-05181effd6aa
    type: secondary
---

## 题目

这道题只有目录里的一个标题线索：统计文本中出现最多的 n-gram。原题按字节还是按单词切分、是否涉及多篇文档，都没有确认。

> 来源：一亩三分地 xAI 题目条目。手册只根据已有目录里的标题重构，没有题面细节，也未核实原题；下面的接口、约束和测试全是手册补的练习约定，不是已确认的面试事实。

## 思路

n-gram 就是长度为 n 的连续 token 窗口。做法很直接：对每篇文档滑动一个长度为 n 的窗口，把窗口内容变成 tuple 当作计数的键，最后按次数排序取前 k 个。

因为原题条件不明，面试时要先问清楚这几件事：

- token 的单位是字节、字符还是分好的词，要不要做大小写归一；
- 窗口能不能跨文档边界（一般不能，否则会凭空造出不存在的 n-gram）；
- 次数相同时怎么排序，k 比不同 n-gram 总数还大时返回什么。

窗口是重叠的，比如 `a b a b` 里 `(a, b)` 出现两次。并列时显式按 tuple 字典序排，输出就不会依赖哈希表的遍历顺序。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `top_ngrams(documents, n, k)`：`documents` 是若干篇已分词的文档，每篇是字符串列表。返回最多 k 个 `(ngram_tuple, count)`，按次数降序，次数相同按 tuple 字典序升序。
- 窗口只在单篇文档内滑动，不跨文档；不做大小写归一；重叠窗口分别计数。
- $n \ge 1$、$k \ge 0$，否则抛 `ValueError`。token 总数不超过 $10^5$，$n \le 10$。

### 输入输出示例

```text
top_ngrams([["a", "b", "a", "b"], ["a", "b"]], n=2, k=2) -> [(("a", "b"), 3), (("b", "a"), 1)]
top_ngrams([["a"], ["b"]], n=2, k=5)                      -> []
```

第一个例子里，第一篇贡献两次 `(a, b)`、一次 `(b, a)`，第二篇再贡献一次 `(a, b)`。两篇之间的 `(b, a)` 不算，因为窗口不跨文档。

### 解题思路与正确性

每篇长度为 L 的文档只有 $L - n + 1$ 个合法起点（L 小于 n 时一个都没有），每个起点对应一次出现，`Counter` 恰好把每次出现记一次。排序键是 `(-次数, tuple)`，并列情况有确定的顺序，输出可以复现。

### 完整参考实现（Python 3）

```python
from collections import Counter


def top_ngrams(documents, n, k):
    """统计所有文档里长度为 n 的 token 窗口，返回出现次数最多的 k 个。

    结果是 [(ngram_tuple, count), ...]，按次数降序，次数相同按 tuple 字典序升序。
    """
    if n < 1:
        raise ValueError(f"n must be at least 1: {n}")
    if k < 0:
        raise ValueError(f"k must be non-negative: {k}")
    counts = Counter()
    for tokens in documents:
        # 窗口只在单个文档内滑动，不跨文档拼接
        for start in range(len(tokens) - n + 1):
            counts[tuple(tokens[start:start + n])] += 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:k]
```

### 可执行测试

```python
# 重叠窗口分别计数，且不跨文档
documents = [["a", "b", "a", "b"], ["a", "b"]]
assert top_ngrams(documents, 2, 2) == [(("a", "b"), 3), (("b", "a"), 1)]

# 文档比 n 短，没有任何窗口
assert top_ngrams([["a"], ["b"]], 2, 5) == []

# 次数相同按字典序
assert top_ngrams([["b", "a"]], 1, 2) == [(("a",), 1), (("b",), 1)]

# k = 0
assert top_ngrams([["a"]], 1, 0) == []

# 大小写不归一
assert top_ngrams([["A", "a"]], 1, 5) == [(("A",), 1), (("a",), 1)]
```

### 复杂度与追问

设 token 总数为 T、不同 n-gram 数为 U。计数要切 T 个长度为 n 的窗口，O(Tn)；排序 O(U log U) 次比较，每次比较 tuple 最坏 O(n)；空间 O(Un)。

- 只要 top-k，不想全排序怎么办？用 `heapq.nlargest` 或者维护一个大小为 k 的堆，排序部分降到 O(U log k)。
- 数据大到单机放不下呢？分布式时先按 n-gram 的哈希把计数分到不同机器，每台机器汇总出自己负责的那部分 n-gram 的完整次数，取本地 top-k，最后再合并各机器的 top-k。各机器只拿本地文档算 top-k 再合并是错的，因为一个 n-gram 的次数可能分散在很多机器上。
