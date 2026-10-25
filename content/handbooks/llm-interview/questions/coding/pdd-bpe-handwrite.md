---
id: pdd-bpe-handwrite
section: coding
order: 182
level: A
title: 拼多多暑期实习：如何模拟 BPE，暴力实现之后还能怎么优化？
quick: "BPE 训练就是把语料切成字符，反复统计相邻 pair 的频次、合并最高频的一对，直到用完词表预算。暴力版每轮扫全部语料；优化可以用优先队列选 pair，用倒排索引找到要更新的位置，再加上预分词和缓存的 merge 规则。"
tags:
  - PDD
  - BPE
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多暑期实习二面
    url: https://www.nowcoder.com/feed/main/detail/6052afa2fbd54b0f997385e8e0ae4dcc
    type: candidate-first-hand
---

## 题目描述

实现一个字符级BPE训练器，返回按训练轮次选择的符号对。这里规定可重复的语料计数和并列规则，作为手册可运行练习口径。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `bpe_train(words,num_merges)`。words为字符串列表，重复单词按出现次数贡献频数；每个单词初始为字符列表加一个独立末尾符号"EOW"。`num_merges`为非负整数。

### 输出与约束

每轮在所有单词内部统计相邻符号对的出现次数，选择最频繁的一对；频数相同时取Python字符串元组字典序较大的那对。把各词中该对从左到右不重叠地合并为拼接符号。返回所选pair元组列表；最多`num_merges`轮，无相邻pair时提前结束，不跨词合并。

### 示例

```text
words=["aaa","aaa"],num_merges=1 -> [("a","a")]
首轮("a","a")共出现4次，("a","EOW")出现2次。
words=[],num_merges=3 -> []
任意words,num_merges=0 -> []
```

## 解题思路与参考答案

BPE 训练就是反复做一件事：数一遍所有相邻 pair 的频次，把最高频的一对合并成新 token，记进 merge 表，直到 merge 次数或词表预算用完。暴力版每轮都扫一遍整个语料，优化的方向是只更新被这次合并影响到的局部。

这是拼多多算法工程师暑期实习二面的题，来自牛客候选人原帖，可信度 A。面试时间原帖没写，帖子发布于 2026-03-25，原话是**“算法题：模拟BPE的实现。追问有没有优化的方法（我写的太暴力了）。”**，也就是暴力写完以后，面试官明确追问了怎么变快。

BPE 是数据驱动的相邻合并，和语言学切词没关系：训练产出一张有序的 merge 表，编码时套同一张表。比如语料里 `l o w` 和 `l o w e r` 都很常见，假设 `l o` 这一对频次最高，第一轮就合成 `lo`，下一轮 `lo w` 可能又合成 `low`。中英混合的语料先走 byte 级，免得未知字符把序列打散。

## 暴力训练：统计 pair，合并最高频

语料先切成字符（或 byte）序列，词尾可以加一个结束标记 `EOW`，文献里常写成斜杠 w。每轮数相邻 pair，合并全局最高频的那对，更新词表和所有序列，重复到 merge 次数或词表预算用完。频次相同时要定一个固定的选择规则，比如字典序，否则结果没法稳定复现。

```python
from collections import Counter

def bpe_train(words, num_merges):
    corpus = [list(w) + ["EOW"] for w in words]
    merges = []
    for _ in range(num_merges):
        pairs = Counter()
        for seq in corpus:
            pairs.update(zip(seq, seq[1:]))
        if not pairs:
            break
        a, b = max(pairs, key=lambda p: (pairs[p], p))
        merges.append((a, b))
        nxt = []
        for seq in corpus:
            i, out = 0, []
            while i < len(seq):
                if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
                    out.append(a + b)
                    i += 2
                else:
                    out.append(seq[i])
                    i += 1
            nxt.append(out)
        corpus = nxt
    return merges
```

编码时按 merge 学到的顺序对输入反复合并，直到合不动为止。别在每一步重新数全局频次，那是训练做的事。训练的复杂度约 $O(\text{rounds}\times\text{tokens})$。

## 优化：堆、局部更新、rank 扫描

优化的思路是只碰被这次合并影响到的地方。pair 频次放进堆里维护，不用每轮全表 `max`，合并之后只改被触及的相邻 pair。再给每个 pair 建倒排，记它出现在哪些词、哪些下标，只重写受影响的词。词频也能压缩：相同的词只存一份再乘次数，语料去重后能快一个数量级。encode 那边把 merge 做成 rank 数组，对 token 序列线性扫描（类似 HuggingFace tokenizers），不用每步 $O(\text{merges})$ 暴力找。

生产里先按空格预分词再做 BPE。面试时讲清楚怎么用堆选候选、只更新相邻 pair，比单纯说换成 C++ 更能回答复杂度问题。另外顺带区分一下：BPE 和 WordPiece 的「整词表 softmax 切」不同，和 Unigram 的损失最小化也不同。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

单词 aaa 中 (a,a) 出现两次，多于 (a,EOW) 的一次，让最高频 pair 唯一，避免平票规则影响预期值。再检查零轮合并和空语料。

```python
assert bpe_train(["aaa", "aaa"], 1) == [("a", "a")]
assert bpe_train(["ab"], 0) == []
assert bpe_train([], 3) == []
print("simple tests passed")
```

## 追问

**频次并列时选谁？**
必须定一个固定的 tie-break，否则词表不可复现。

**为什么 encode 不用频次？**
频次只决定训练时的合并顺序，推理只是回放这个顺序。

**byte 级解决了什么？**
任意 Unicode 都能切，没有 UNK；中英混合时，不会因为某个字不在词表里就碎成未知。

**和 SentencePiece 什么关系？**
SP 常用 Unigram，BPE 是 merge 过程，两种实现别混。

**堆里的频次过期了怎么办？**
用懒删除：频次变了不立刻从堆里删，弹出时 count 对不上就跳过。这是常见实现。
