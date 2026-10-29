---
id: p3a-perplexity-stream-deduplication-with-near-duplicate-detection
section: design
order: 607
level: A
title: Perplexity：流式去重：精确与近似重复
quick: >-
  精确去重用集合记录已见字符串；近似去重先约定规范化与相似度，再只和已保留的代表比较。相似关系不传递，代表选择会受处理顺序影响，不能直接用并查集当作同一种语义。
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: >-
      1Point3Acres · Perplexity ·
      stream-deduplication-with-near-duplicate-detection
    url: >-
      https://www.1point3acres.com/interview/problems/company/perplexity/stream-deduplication-with-near-duplicate-detection
    type: secondary
---

## 题目描述

实现按到达顺序进行的字符串流去重。一个字符串只有在与所有已保留代表都不够相似时才能被保留；被丢弃的字符串不能再作为代表阻挡后续输入。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `dedup(stream, threshold=1.0)`：生成器，按顺序产出要保留的字符串，原样输出不做修改。
- 把字符串小写后按空白分词得到词集合，与任何一个已保留代表的 Jaccard 相似度（交集大小除以并集大小）$\ge$ `threshold` 就丢弃。两个空集合的相似度定为 1。
- `threshold` 必须在 $(0, 1]$ 内。
- 字符串总数不超过 5000。

### 示例

```text
dedup(["a b", "b a", "a c"], threshold=1)   -> ["a b", "a c"]
dedup(["", "  ", "x"], threshold=0.8)       -> ["", "x"]
dedup(["a", "a b", "b"], threshold=0.5)     -> ["a", "b"]
```

## 解题思路与参考答案

## 题目

处理一个字符串流，每个字符串只保留第一次出现的那一份。进一步扩展到近似重复：和之前保留的某个字符串足够相似（相似度超过阈值）就丢掉。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

精确去重用集合记住已见字符串，第一次出现才输出。近似去重先约定大小写、空白、标点等如何规范化，以及相似度怎么算。这份练习把文本小写后按空白分词，形成词集合，再算 Jaccard：$|A \cap B| / |A \cup B|$。

相似关系不传递。例如 `"a"` 与 `"a b"` 的相似度是 0.5，`"a b"` 与 `"b"` 也是 0.5，`"a"` 与 `"b"` 却是 0。这里按先到先保留的规则，只和已保留代表比较，被丢弃的字符串不再影响后续输入。因此处理顺序会改变结果；并查集合并相似串，得到的会是另一种语义。

逐一比较所有代表需要 $O(N^2)$ 次量级的比较。数据更大时，用词倒排索引，或 MinHash + LSH 先召回候选再比。无限流配有限内存，则要设时间窗口，或用布隆过滤器、定长 MinHash 签名等近似结构，并说明窗口外或近似处理会漏掉哪些重复。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `dedup(stream, threshold=1.0)`：生成器，按顺序产出要保留的字符串，原样输出不做修改。
- 把字符串小写后按空白分词得到词集合，与任何一个已保留代表的 Jaccard 相似度 $\ge$ `threshold` 就丢弃。两个空集合的相似度定为 1。
- `threshold` 必须在 $(0, 1]$ 内，否则抛 `ValueError`。因为是生成器，错误在开始迭代时才抛出。
- 字符串总数不超过 5000。

### 输入输出示例

```text
dedup(["a b", "b a", "a c"], threshold=1)   -> ["a b", "a c"]
dedup(["", "  ", "x"], threshold=0.8)       -> ["", "x"]
dedup(["a", "a b", "b"], threshold=0.5)     -> ["a", "b"]
```

最后一个例子里，`"a b"` 被 `"a"` 挡掉，没有成为代表，所以 `"b"` 能保留下来。

### 解题思路与正确性

每个新字符串只和此前已保留的代表比较，符合「先到先保留」的在线语义：一个字符串是否保留，只取决于它之前的输入，后面的输入不会改变已经产出的结果。

Jaccard 阈值关系不是等价关系，不能先把所有字符串分组再挑代表，那样得到的结果和这份契约不同。

### 完整参考实现（Python 3）

```python
def tokenize(text):
    return set(text.lower().split())


def jaccard(left, right):
    union = left | right
    if not union:
        return 1.0  # 两个空集合视为完全相同
    return len(left & right) / len(union)


def dedup(stream, threshold=1.0):
    """流式去重：按出现顺序产出字符串，与已保留的某个代表的 Jaccard 相似度 >= threshold 就丢弃。

    只和已保留的代表比较；被丢弃的字符串不会成为新代表。
    """
    if not 0 < threshold <= 1:
        raise ValueError(f"threshold must be in (0, 1], got {threshold}")

    representatives = []
    for text in stream:
        tokens = tokenize(text)
        if any(jaccard(tokens, kept) >= threshold for kept in representatives):
            continue
        representatives.append(tokens)
        yield text
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert list(dedup(["a b", "b a", "a c"], 1)) == ["a b", "a c"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        list(fn(*args))
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# threshold = 1：词集合完全相同才算重复，忽略词序
assert list(dedup(["a b", "b a", "a c"], 1)) == ["a b", "a c"]

# 空白字符串的词集合都是空集，彼此相似度为 1
assert list(dedup(["", "  ", "x"], 0.8)) == ["", "x"]

# 相似关系不传递："a b" 被 "a" 挡掉，不能再拿它去挡 "b"
assert list(dedup(["a", "a b", "b"], 0.5)) == ["a", "b"]

# 大小写不敏感
assert list(dedup(["Hello World", "hello world"])) == ["Hello World"]

expect_value_error(dedup, ["a"], 0)
expect_value_error(dedup, ["a"], 1.5)
```

### 复杂度与追问

设字符串数为 N、平均词数为 L。最坏情况每个字符串都要和所有代表比较，时间 $O(N^2 L)$，代表占 $O(NL)$ 空间。

如果追问怎么加速：建倒排索引，只和至少共享一个词的代表比较；阈值为 $t$ 时还可以用前缀过滤进一步剪枝。规模更大时用 MinHash + LSH，但它是近似方法，可能漏掉部分真正相似的对，需要报告召回率，不能承诺和精确版结果完全一致。

如果追问流是无限的：给代表设过期时间，或只保留最近一个窗口内的代表，并说明窗口外的重复不会被发现。
