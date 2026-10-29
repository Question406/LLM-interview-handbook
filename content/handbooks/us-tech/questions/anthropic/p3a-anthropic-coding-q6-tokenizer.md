---
id: p3a-anthropic-coding-q6-tokenizer
section: anthropic
order: 608
level: A
title: Anthropic：最长匹配 Tokenizer：UNK 合并与 trie
quick: >-
  我会把 vocabulary 建成 trie，每次从当前位置向下匹配，并记住最后一个完整 token。走不通就输出它；完全匹配不上时输出 UNK
  并前进一个字符，连续 UNK 只合并输出，不影响后面的有效 token。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Anthropic · coding-q6-tokenizer
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q6-tokenizer
    type: secondary
---

## 题目描述

实现一个确定性的 vocabulary tokenizer。给定 Unicode 文本和 token 到整数 id 的 vocabulary，从文本开头依次识别 token，输出 token id 列表；不能匹配 vocabulary 的字符按指定的未知 token 规则处理。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `tokenize(text, vocab, unk=-1, merge_unk=True) -> list[int]`：按 Unicode 字符处理，每一步取当前位置最长的 vocabulary token，输出它的 id。
- 没有任何 token 能匹配时输出 `unk`，并恰好消耗一个字符。`merge_unk=True` 时，连续的未知字符只输出一个 `unk`；已知 token 会打断这段连续。
- vocabulary 不能含空串，也不能有 token 的 id 等于 `unk`。
- vocabulary 最多 $10^4$ 个 token，文本最多 $10^5$ 个字符。

### 示例

```text
vocab = {"ab": 1, "a": 2}
tokenize("ab??a?", vocab)                   -> [1, -1, 2, -1]
tokenize("ab??", vocab, merge_unk=False)    -> [1, -1, -1]
tokenize("abc", {"a": 1, "abcd": 2})        -> [1, -1]
```

## 解题思路与参考答案

## 题目

给一个 vocabulary（字符串到 token id 的映射），把输入文本切成 token id 序列。每一步都取当前位置能匹配到的最长 vocabulary token。遇到 vocabulary 里没有的字符输出 UNK，并支持把连续的未知字符合并成一个 UNK。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会用 trie 做最长匹配，并在搜索时记下最后一个完整 token。具体说，从当前位置沿 trie 往下走，每遇到完整 token 的节点就更新它的位置和 id；路径走不通后，回到最后记住的位置，输出那个 token，再继续处理剩下的文本。

这里有一个容易错的地方：走得最远的路径不一定是完整 token。比如 vocabulary 有 `a` 和 `abcd`，文本是 `abc`，trie 能走到 `abc`，但 `abc` 不是 token，正确输出是 `a`，然后从 `b` 继续。所以必须记住「最后一个完整 token」，而不是停在哪里就输出哪里。

如果当前位置一个 token 都匹配不上，就输出 UNK，并且按题目约定前进一个字符（或一个字节）。UNK 合并只影响输出：连续的未知字符只输出一个 UNK，但后面一旦能匹配到有效 token，照常输出，不能被合并吞掉。

要和面试官确认的是：按字符还是按字节处理，以及 vocabulary 里有没有 id 和 UNK 冲突。

注意最长匹配和 BPE 不是一回事：BPE 是按合并规则反复合并相邻的 token 对，结果可能和最长匹配不同。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `tokenize(text, vocab, unk=-1, merge_unk=True) -> list[int]`：按 Unicode 字符处理，每一步取当前位置最长的 vocabulary token，输出它的 id。
- 没有任何 token 能匹配时输出 `unk`，并恰好消耗一个字符。`merge_unk=True` 时，连续的未知字符只输出一个 `unk`；已知 token 会打断这段连续。
- vocabulary 不能含空串，也不能有 token 的 id 等于 `unk`，否则抛 `ValueError`。id 等于 `unk` 时，无法区分输出里的 `unk` 是已知 token 还是未知字符。
- vocabulary 最多 $10^4$ 个 token，文本最多 $10^5$ 个字符。

### 输入输出示例

```text
vocab = {"ab": 1, "a": 2}
tokenize("ab??a?", vocab)                   -> [1, -1, 2, -1]
tokenize("ab??", vocab, merge_unk=False)    -> [1, -1, -1]
tokenize("abc", {"a": 1, "abcd": 2})        -> [1, -1]
```

第一个例子里，两个 `?` 合并成一个 `-1`；中间的 `a` 是已知 token，所以最后一个 `?` 重新输出一个 `-1`。

### 解题思路与正确性

`longest_match` 从起点沿 trie 走，每到一个带 `END` 标记的节点就更新 `best`。走不下去时返回 `best`，它对应的正是从这个起点出发的最长完整 token。

没有匹配时只前进一个字符，循环一定会结束。`in_unknown_run` 只在未知分支置为真、在匹配成功时清零，所以合并只发生在相邻的未知字符之间。

### 完整参考实现（Python 3）

```python
END = object()  # trie 节点里标记「到这里是一个完整 token」的键


def build_trie(vocab, unk):
    """把 vocabulary 建成字符 trie，完整 token 的节点在 END 键下存 token id。"""
    root = {}
    for word, token_id in vocab.items():
        if not word:
            raise ValueError("vocabulary must not contain the empty string")
        if token_id == unk:
            # 否则无法区分已知 token 和 unk，合并规则会出错
            raise ValueError(f"token id {token_id} collides with unk")
        node = root
        for char in word:
            node = node.setdefault(char, {})
        node[END] = token_id
    return root


def longest_match(trie, text, start):
    """从 start 起沿 trie 走，返回最长完整 token 的 (结束位置, id)；没有则 None。"""
    node = trie
    best = None
    position = start
    while position < len(text) and text[position] in node:
        node = node[text[position]]
        position += 1
        if END in node:
            best = (position, node[END])
    return best


def tokenize(text, vocab, unk=-1, merge_unk=True):
    """按 Unicode 字符做最长匹配分词；merge_unk 时连续未知字符只输出一个 unk。"""
    trie = build_trie(vocab, unk)
    output = []
    position = 0
    in_unknown_run = False
    while position < len(text):
        match = longest_match(trie, text, position)
        if match is None:
            if not (merge_unk and in_unknown_run):
                output.append(unk)
            position += 1  # 未知时恰好消耗一个字符，保证前进
            in_unknown_run = True
        else:
            position, token_id = match
            output.append(token_id)
            in_unknown_run = False
    return output
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert tokenize("ab??a?", vocab) == [1, -1, 2, -1]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


vocab = {"ab": 1, "a": 2}

# 最长匹配，连续未知字符合并成一个 unk，已知 token 会打断合并
assert tokenize("ab??a?", vocab) == [1, -1, 2, -1]

# 关闭合并后，每个未知字符各输出一个 unk
assert tokenize("ab??", vocab, merge_unk=False) == [1, -1, -1]

# 空输入
assert tokenize("", vocab) == []

# 多字节字符按 Unicode 字符处理
assert tokenize("你好?", {"你": 1, "你好": 2}) == [2, -1]

# 走得最远的路径不一定是完整 token：要回退到最后一个完整 token
assert tokenize("abc", {"a": 1, "abcd": 2}) == [1, -1]

# 非法 vocabulary
expect_value_error(tokenize, "a", {"": 1})
expect_value_error(tokenize, "a", {"a": -1})
```

### 复杂度与追问

设 vocabulary 总字符数为 V、文本长度为 T、最长 token 长度为 L。建 trie 是 O(V) 时间和空间；扫描时每个起点最多沿 trie 走 L 步，总共 O(T·L)。

- 如果要按字节处理呢？先把文本和 vocabulary 都编码成 UTF-8 字节，trie 的边改成字节值。这样未知时前进一个字节，可能把一个多字节字符拆开，输出语义要和面试官确认。
- 最长匹配和 BPE 的区别是什么？最长匹配是贪心地从左往右切；BPE 从单个字符开始，按训练得到的合并顺序反复合并相邻对。同一个 vocabulary，两种算法切出来的结果可能不同，不能混用。

## 相关题

- [[anthropic-bpe-tokenizer]]：同一家公司的 BPE 题，按 merge 优先级合并；本卡最后一条追问说的区别就是这两题的区别。
- [[coding-bpe-merge]]：BPE 训练的一步 merge，看清 merge 表从哪来。
