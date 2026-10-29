---
id: anthropic-bpe-tokenizer
section: anthropic
order: 2
level: A
title: Anthropic：手写 BPE Tokenizer，encode / decode 要对齐什么不变量？
quick: >-
  训练时反复合并最高频相邻 pair，保存有序 merge 表；encode 按这张表的优先级合并，不能重新按当前频次选 pair。字节级 BPE 从
  UTF-8 字节出发，decode 拼回字节，保持 decode(encode(s)) == s。
tags:
  - 完整编程练习
  - Anthropic
  - Tokenizer
  - BPE
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Anthropic Coding Interview Questions (LinkJob)
    url: 'https://www.linkjob.ai/interview-questions/anthropic-coding-interview/'
    type: secondary
  - title: Neural Machine Translation of Rare Words with Subword Units (BPE)
    url: 'https://arxiv.org/abs/1508.07909'
    type: primary
  - title: tiktoken
    url: 'https://github.com/openai/tiktoken'
    type: primary
---

## 题目描述

实现一个 UTF-8 字节级 BPE tokenizer，使文本可以编码成 bytes token 并无损 decoding；另外完成有 sampling 预算的 token 数估计接口。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `encode(text, merges) -> list[bytes]`：byte-level BPE。先把 `text` 按 UTF-8 编码，每个字节是一个初始 token。`merges` 是按优先级排好的 `(左 bytes, 右 bytes)` 列表，下标越小优先级越高，不能有重复或空 bytes。每一轮在所有相邻 pair 里找优先级最高的那个（同优先级取最左边），只合并这一对，然后重新找，直到没有可合并的 pair。
- `decode(tokens) -> str`：把 bytes token 拼起来，按严格 UTF-8 decoding。
- `estimate(text, merges, budget, rng) -> (估计 token 数, 实际采样字符数)`：附加题；由手册补充。随机取若干个固定长度的字符窗口，用同一个 `encode` 算平均每字符 token 数，再乘总字符数。总 sampling 字符数不超过 `budget`；文本不比预算长时直接全量编码。
- 输入不超过 $10^4$ 个 UTF-8 字节。

### 输入输出示例

```text
merges = [(b"a", b"b"), (b"ab", b"ab")]
encode("abab", merges)          -> [b"abab"]
decode(encode("你好🙂", merges))  -> "你好🙂"
estimate("abab", merges, 4, rng) -> (1.0, 4)   # 文本不超过预算，全量编码
```

## 解题思路与参考答案

Encode 使用训练时冻结的 merge 优先级，每轮合并当前 rank 最小的相邻 pair；字节级表示则保证文本可以原样 decoding 回来。比如 `abab` 先合成两个 ab，再合成 abab，选择顺序由 merge 表决定。实现时先写清楚的慢参考，再用链表和堆优化。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。题型来源见后面的「真题记录」。Python 3 标准库即可运行。

### 题面、接口与约束

- `encode(text, merges) -> list[bytes]`：byte-level BPE。先把 `text` 按 UTF-8 编码，每个字节是一个初始 token。`merges` 是按优先级排好的 `(左 bytes, 右 bytes)` 列表，下标越小优先级越高，不能有重复或空 bytes。每一轮在所有相邻 pair 里找优先级最高的那个（同优先级取最左边），只合并这一对，然后重新找，直到没有可合并的 pair。
- `decode(tokens) -> str`：把 bytes token 拼起来，按严格 UTF-8 decoding。
- `estimate(text, merges, budget, rng) -> (估计 token 数, 实际采样字符数)`：附加题；由手册补充。随机取若干个固定长度的字符窗口，用同一个 `encode` 算平均每字符 token 数，再乘总字符数。总 sampling 字符数不超过 `budget`；文本不比预算长时直接全量编码。
- 输入不超过 $10^4$ 个 UTF-8 字节。

### 输入输出示例

```text
merges = [(b"a", b"b"), (b"ab", b"ab")]
encode("abab", merges)          -> [b"abab"]
decode(encode("你好🙂", merges))  -> "你好🙂"
estimate("abab", merges, 4, rng) -> (1.0, 4)   # 文本不超过预算，全量编码
```

### 解题思路与正确性

参考实现直接按定义来：每一轮扫一遍所有相邻 pair，取 rank 最小的那个合并，然后从头再找。它慢，但语义清楚，适合作为后续优化版本的对照答案。优化版要用双向链表加堆，并给每个 pair 记一个位置版本号，合并后已经失效的旧 pair 不能再被弹出来合并。

这里合并的是“当前优先级最高的 pair”，不是“当前出现次数最多的 pair”。后者是训练过程，encode 时没有语料频次，只有冻结的 merge 表。

`estimate` 复用 `encode`，不复制任何合并逻辑。但每个窗口单独编码，window boundaries 会切断本来能跨 window boundaries 合并的 pair，所以这个估计是有偏的，要连同 sampling 字符数一起报告，不能说它无偏。

### 完整参考实现（Python 3）

```python
import random


def encode(text, merges):
    """byte-level BPE：按 merges 的优先级反复合并相邻 pair，返回 bytes token 列表。"""
    ranks = {pair: rank for rank, pair in enumerate(merges)}
    if len(ranks) != len(merges):
        raise ValueError("merges contains duplicate pairs")
    if any(not left or not right for left, right in merges):
        raise ValueError("merges contains an empty token")

    tokens = [bytes([byte]) for byte in text.encode("utf-8")]
    while True:
        candidates = [
            (ranks[(tokens[i], tokens[i + 1])], i)
            for i in range(len(tokens) - 1)
            if (tokens[i], tokens[i + 1]) in ranks
        ]
        if not candidates:
            break
        _, i = min(candidates)  # rank 最小；同 rank 取最左
        tokens[i : i + 2] = [tokens[i] + tokens[i + 1]]
    return tokens


def decode(tokens):
    """拼接 bytes token，并按严格 UTF-8 decoding。"""
    return b"".join(tokens).decode("utf-8")


def estimate(text, merges, budget, rng):
    """随机字符窗口估计总 token 数，返回 (估计值, 实际 sampling 字符数)。窗口边界会让估计有偏。"""
    if budget < 1:
        raise ValueError(f"budget must be at least 1, got {budget}")
    if not text:
        return 0.0, 0
    if len(text) <= budget:
        return float(len(encode(text, merges))), len(text)

    window = min(32, budget)
    sampled_chars = 0
    token_count = 0
    while sampled_chars + window <= budget:
        start = rng.randrange(len(text) - window + 1)
        chunk = text[start : start + window]
        token_count += len(encode(chunk, merges))
        sampled_chars += window
    return token_count / sampled_chars * len(text), sampled_chars
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert encode("abab", merges) == [b"abab"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}{args}")


merges = [(b"a", b"b"), (b"ab", b"ab")]

# 按优先级合并：先合出两个 ab，再合成 abab
assert encode("abab", merges) == [b"abab"]

# 同优先级取最左：aba 只能合并左边的 ab
assert encode("aba", merges) == [b"ab", b"a"]

# 空串、ASCII、多字节中文和 emoji 都能原样往返
for text in ("", "hello", "你好🙂", "abab"):
    assert decode(encode(text, merges)) == text

# 没有 merge 时每个 UTF-8 字节是一个 token
assert encode("你", []) == [b"\xe4", b"\xbd", b"\xa0"]

# 非法的 merge 表
expect_value_error(encode, "ab", [(b"a", b"b"), (b"a", b"b")])
expect_value_error(encode, "ab", [(b"", b"b")])

# 文本不超过预算时全量编码
assert estimate("abab", merges, 4, random.Random(1)) == (1.0, 4)

# 长文本只 sampling，sampling 字符数不超过预算
estimated, sampled = estimate("abab" * 100, merges, 100, random.Random(3))
assert estimated > 0
assert sampled <= 100

# 空文本和非法预算
assert estimate("", merges, 10, random.Random(0)) == (0.0, 0)
expect_value_error(estimate, "abab", merges, 0, random.Random(0))
```

### 复杂度与追问

设 $B$ 是输入的 UTF-8 字节数，$M$ 是 merge 数。参考实现每轮扫描 $O(B)$ 个 pair，最多合并 $B-1$ 轮，所以最坏 $O(B^2)$ 次字典查找，每次查找还要付出 bytes 哈希和比较的成本；空间 $O(B+M)$。

- 追问「怎么加速」：双向链表加最小堆，每次合并只更新左右两个新 pair，堆里的旧条目靠版本号判失效。优化版要和慢参考做逐输入的差分测试。生产实现（tiktoken 一类）还会先做预分词，再按块查表。
- 追问「预算按什么算」：这里按字符计预算。如果现场要求按 UTF-8 字节计，就要另外约定切片规则，保证不会切在一个多字节字符中间。

## 真题记录

- 公司：Anthropic
- 岗位：SWE 编码题库里的 Tokenizer 题（公开复盘把它列为题库第六题）
- 来源：LinkJob 对近两年面经的汇总；实现细节以 Sennrich 的 BPE 论文和字节级 BPE 为准

Anthropic 想看的是：merge 表怎么用，空格和字节怎么处理，encode 结果是否稳定。不能直接调库。

## 训练：统计 pair，记下有序 merge 表

先把语料切成符号序列。字符级 BPE 从单个字符出发；GPT-2 式的字节级 BPE 从 0 到 255 这 256 个字节出发，因此不会出现 unk。然后反复执行：

1. 统计所有相邻 pair 的频次；
2. 把频次最高的 pair 合并成一个新符号；
3. 把这次合并追加到 merge 表。

达到目标 vocabulary 大小或 merge 次数时停止。vocabulary 等于基础符号加上所有 merge 产生的符号。merge 的优先级就是它在训练中发生的顺序，不是字母序。

面试时别漏掉一点：同一个 pair 的频次每轮都会变，因为上一轮合并改变了它的邻居。所以每轮都要重新统计，不能拿初始的 pair 计数一路合到底。

## Encode：按 merge 顺序，不是每步找最高频

encode 把 merge 表当成优先级：只应用训练时记录过的 pair，并且按训练顺序优先。上面的参考实现每步取 rank 最小的相邻 pair；另一种等价的朴素写法是按顺序扫 merge 表，能合就合，直到一整轮都没有命中，单个词的代价是 $O(T\cdot M)$（$T$ 是该词的符号数）。生产实现用 trie 或预分词加查表（tiktoken 那类）。白板上先把朴素版写对，再谈加速。

常见误区是在当前序列上每步重新找出现次数最多的 pair。那是训练的逻辑；线上没有语料频次，只有冻结的 merge 表。

空格要作为符号处理：BPE 论文里常用词尾标记（end-of-word），GPT-2 用 `Ġ` 表示前导空格。空格规则必须和 decoding 规则一致，否则 `encode("a b")` 和 `encode("ab")` 会得到同样的结果，信息就丢了。

## Decode 与不变量

decode 把 id 映回 token 字符串再拼接。字节级 BPE 要把 GPT-2 那套可打印的 latin-1 字符映射还原成原始字节，再按 UTF-8 decoding。遇到非法 UTF-8 时要有明确策略，面试中说清是用替换字符还是抛错即可。

要保持的不变量：

- 对训练集字符集内的文本，`decode(encode(s)) == s`；字节级 BPE 对任意 UTF-8 文本都成立；
- 同一张 merge 表下，encode 结果是确定的；
- vocabulary id 稳定：不能每次训练都重新分配 id 却不保存映射。

## 追问

- **WordPiece / Unigram 差在哪？** WordPiece 按似然增益选择合并；Unigram 是子词概率模型，从大 vocabulary 往下删。BPE 是确定性的 merge 序列。Claude / GPT 的 vocabulary 都属于 BPE 家族，不是 WordPiece。
- **为什么用字节级？** 任意 UTF-8 文本都能表示，没有 unk，多语言文本和乱码也不会让编码出错。
- **和 embedding 矩阵是什么关系？** `vocab_size` 必须等于 embedding 的行数。扩 vocabulary 时要同时扩 embedding 和 lm_head，并给新 id 做初始化。见 `arch-tokenizer`。

## 相关题

- [[p3a-perplexity-byte-tokenizer-and-token-count-estimator]]：几乎同一题：字节级 BPE 按 merge 优先级编码、并列取最左、往返不变、按预算 sampling 估 token 数，测试也基本一样；那边多了用链表加堆优化慢参考实现。
- [[coding-bpe-merge]]：只写训练里的一步 merge，带词尾标记，不涉及 encode。
- [[p3a-anthropic-coding-q6-tokenizer]]：Anthropic 的另一道 tokenizer 题，用 trie 做最长匹配，切法和 BPE 不同。
- [[openai-tiktoken]]：口述 tiktoken 和 SentencePiece 的区别，以及特殊 token 和扩 vocabulary。
- [[sys-tokenizer-same]]：rollout 和训练用的 tokenizer 对不上时，RL 训练会坏在哪。
- [[meta-llama3-tokenizer]]：Llama 3 用的就是 tiktoken 风格的字节级 BPE，那张卡讲换 vocabulary 之后压缩率和 id 空间怎么变。
