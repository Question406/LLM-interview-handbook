---
id: p3a-perplexity-stream-deduplication-with-near-duplicate-detection
section: design
order: 607
level: A
title: "Perplexity：流式去重：精确与近似重复"
quick: "精确去重用集合记录见过的字符串；近似去重先定义规范化和相似度，只和已保留的代表比较，因为相似关系不传递，处理顺序会影响结果。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · stream-deduplication-with-near-duplicate-detection"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/stream-deduplication-with-near-duplicate-detection
    type: secondary
---

## 题目

处理一个字符串流，每个字符串只保留第一次出现的那一份。进一步扩展到近似重复：和之前保留的某个字符串足够相似（相似度超过阈值）就丢掉。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

精确去重用一个集合记下见过的字符串就够了。近似去重要先定两件事：相似度怎么算，以及比较前做什么规范化（大小写、空白、标点）。这份练习用小写后按空白分词的词集合，计算 Jaccard 相似度 $|A \cap B| / |A \cup B|$。

近似相似不具有传递性。比如 `"a"` 和 `"a b"` 相似度 0.5，`"a b"` 和 `"b"` 也是 0.5，但 `"a"` 和 `"b"` 是 0。所以处理顺序会影响结果，必须先约定规则：这里只和已经保留下来的代表比较，被丢弃的字符串不会再去挡别人。用并查集把所有相似的串合并成一组，得到的是另一种语义，不能混用。

逐个和所有代表比较是 $O(N^2)$。数据量大时要用候选索引减少比较，比如按词建倒排索引，或者用 MinHash + LSH 只比较落在同一个桶里的候选。

无限流加有限内存时，不可能永远记住所有代表，只能用时间窗口或近似结构（布隆过滤器、定长 MinHash 签名）。要明确告诉面试官会漏掉哪些重复，不能承诺永不遗忘。

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
