---
id: ml101-ngram-generation
section: probability
order: 14
level: A
title: 实现 N-gram 的训练和文本生成，怎样处理句界、sampling 与未见上下文？
quick: >-
  训练时统计最近 N−1 个词到下一词的条件计数，生成时按对应计数分布
  sampling，再滚动更新上下文。句首和句尾标记要在训练与生成时一致。参考练习在上下文未见时逐级缩短历史，直到
  unigram；这种回退规则是手册约定，不能直接当成平滑后的标准语言模型。
companies:
  - google
tags:
  - Probability
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: Google 候选人面经：N-gram 训练与生成两个函数
    url: 'https://www.1point3acres.com/interview/thread/1094501'
    type: secondary
  - title: 'Jurafsky and Martin, N-gram Language Models'
    url: 'https://web.stanford.edu/~jurafsky/slp3/3.pdf'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

训练一个最高阶为 n 的计数语言模型，并从给定前缀的上下文继续随机生成 token；高阶上下文未出现时回退到较低阶。

### 输入与接口

实现 NGramLM(n)，提供 fit(sentences)、`next_counts`(history)、generate(*,`max_tokens`=30,seed=0,prefix=())。n 为正整数；sentences 是句子 token 列表，token 为普通字符串，不能等于保留标记 `<BOS>` / `<EOS>`；语料至少包含一个句子。`max_tokens` 为非负整数。

### 输出与约束

fit 清空旧模型并训练，返回 self；每句前加 n-1 个 BOS、末尾加一个 EOS，对每个实际词和 EOS 统计长度0到 n-1的上下文计数。`next_counts` 从 history 最长后缀（最多 n-1词）开始查，逐级缩短，返回第一个有观测的后继计数字典；0阶为全局后继计数。

generate 用 n-1 个 BOS 与 prefix 组成初始历史，只返回新生成 token，不含 prefix 和保留标记。每步根据 `next_counts` 的计数比例抽样，遇 EOS 即停，最多生成 `max_tokens` 个普通 token。使用 random.Random(seed) 的 randrange(总计数)，按后继字符串排序分配整数票区间；相同模型、prefix 和 seed 须可复现。不添加平滑，不因未知 prefix 而停止。

### 示例

```text
model=NGramLM(3).fit([["i","like","tea"],["i","like","tea"],["i","like","coffee"]])
model.next_counts(["i","like"]) -> {"tea":2,"coffee":1}
model.next_counts(["unknown","like"]) -> {"tea":2,"coffee":1}
model.generate(max_tokens=0) -> []
NGramLM(2).fit([["a"]]).generate(seed=0) -> ["a"]
```

## 解题思路与参考答案

N-gram 训练保存“历史片段后面出现过哪些词、各出现多少次”，生成时根据当前历史抽一个后继。它与只返回最高频后继的 bigram API 不同，生成结果可以保留训练分布中的多种后继。

原帖要求训练与生成两个函数，另问优化，没有给完整接口。这里约定 N 为正整数，输入已分词的句子；逐句加 N−1 个句首标记和一个句尾标记；训练同时保存从零长度到 N−1 长度历史的计数。生成遇到未见历史时，删除最左边的历史词继续查找；按整数频次 sampling，遇到句尾或长度上限停止。空句会贡献一个句尾，空语料无法生成。特殊标记不能出现在输入中。

```python
from collections import Counter, defaultdict
import random


class NGramLM:
    BOS = "<BOS>"
    EOS = "<EOS>"

    def __init__(self, n):
        if type(n) is not int or n < 1:
            raise ValueError("n must be a positive integer")
        self.n = n
        self.tables = [defaultdict(Counter) for _ in range(n)]

    def fit(self, sentences):
        self.tables = [defaultdict(Counter) for _ in range(self.n)]
        for sentence in sentences:
            sentence = list(sentence)
            if any(
                not isinstance(w, str) or w in (self.BOS, self.EOS) for w in sentence
            ):
                raise ValueError("tokens must be strings without reserved markers")
            tokens = [self.BOS] * (self.n - 1) + sentence + [self.EOS]
            for i in range(self.n - 1, len(tokens)):
                for length in range(self.n):
                    context = tuple(tokens[i - length : i]) if length else ()
                    self.tables[length][context][tokens[i]] += 1
        return self

    def next_counts(self, history):
        history = tuple(history)
        for length in range(min(len(history), self.n - 1), -1, -1):
            context = history[-length:] if length else ()
            counts = self.tables[length].get(context)
            if counts:
                return dict(counts)
        raise ValueError("model has no observed transitions")

    def generate(self, *, max_tokens=30, seed=0, prefix=()):
        if type(max_tokens) is not int or max_tokens < 0:
            raise ValueError("max_tokens must be a nonnegative integer")
        prefix = list(prefix)
        if any(not isinstance(w, str) or w in (self.BOS, self.EOS) for w in prefix):
            raise ValueError("prefix must contain ordinary string tokens")
        if not self.tables[0]:
            raise ValueError("fit a nonempty corpus first")
        history = [self.BOS] * (self.n - 1) + prefix
        generated = []
        rng = random.Random(seed)
        for _ in range(max_tokens):
            counts = self.next_counts(history)
            ticket = rng.randrange(sum(counts.values()))
            for word, count in sorted(counts.items()):
                if ticket < count:
                    break
                ticket -= count
            if word == self.EOS:
                break
            generated.append(word)
            history.append(word)
        return generated
```

例子有两句 ["i","like","tea"] 和一句 ["i","like","coffee"]。当历史是 i、like，后继 tea 的计数是 2，coffee 为 1，因此 sampling 概率分别是 2/3、1/3。若历史是 unknown、like，三元历史没有记录，可以回退到 like 的后继分布。返回值只含新生成 token，不重复 prefix，也不包含句尾标记。

加句首标记使开头也能使用固定长度历史，逐句统计避免把上一句末词和下一句首词接起来。句尾是一个可被 sampling 的事件；只有长度上限而没有句尾的模型，无法从数据里学到何时结束。

设 T 为包含句尾的训练位置总数。参考实现为每个位置保存 N 种长度的 tuple，考虑复制与哈希历史的成本，训练最坏约为 $O(TN^2)$；N 固定时随语料长度线性增长。计数表存储量按不同历史及后继增长。单次生成还会复制计数字典、排序后继并累加，不能把这版实现说成每个词 $O(1)$；可以缓存 sampling 表来优化。

**回退和插值有什么区别？**
本题只在完整历史完全未见时回退；已见历史里没出现过的后继仍然得到零概率。插值会按权重组合不同阶的分布，平滑也可以给未见后继保留质量，需要另外定义公式和 vocabulary。

**怎样测 sampling 代码？**
先验证计数和句界，再用固定种子保证复现；对一个已知 3:1 的后继分布重复抽样，检查频率接近 3/4。不能只检查一次生成结果是否刚好等于某句话。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用三元模型的已知上下文检查计数，再让缺失的长上下文回退到 like。生成使用固定种子，零长度限制应立即返回空列表。

```python
model = NGramLM(3).fit([["i", "like", "tea"]] * 2 + [["i", "like", "coffee"]])
assert model.next_counts(["i", "like"]) == {"tea": 2, "coffee": 1}
assert model.next_counts(["unknown", "like"]) == {"tea": 2, "coffee": 1}
assert model.generate(seed=7) == model.generate(seed=7)
assert model.generate(max_tokens=0) == []
print("simple tests passed")
```
