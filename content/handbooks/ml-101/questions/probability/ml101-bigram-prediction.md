---
id: ml101-bigram-prediction
section: probability
order: 13
level: A
title: 如何用 bigram 频次训练一个下一个词预测 API？
quick: >-
  统计每个词后面紧跟各个词的次数，再用该词的后继总次数
  normalization，得到条件概率。输入词后返回计数最大的后继即可；同一上下文的分母相同，所以求最大值无需先算概率。sentence
  boundaries、未见词和平票都要提前约定，训练时不能把不相邻的句子误接成 bigram。
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
  - title: Google L5 MLE 候选人面经：bigram word predictor API
    url: 'https://www.1point3acres.com/interview/thread/1116207'
    type: secondary
  - title: 'Jurafsky and Martin, N-gram Language Models'
    url: 'https://web.stanford.edu/~jurafsky/slp3/3.pdf'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

给定已经分词的句子语料，统计句内相邻词，预测给定词后最可能出现的一个词，并查询条件概率。

### 输入与接口

实现 BigramPredictor(sentences)，提供 predict(word) 与 probability(previous,following)。sentences 是字符串 token 列表的列表；单个句子可以为空或只有一个词。大小写和标点 token 都按原值区分。

### 输出与约束

predict 返回该词后出现次数最多的后继字符串；次数平票按字符串字典序取较小者。若该词没有观察到任何后继，返回 None。probability 返回该后继次数/该前词所有后继次数；前词有后继但指定后继未出现时返回0.0，无任何后继时返回 None。

只统计每个句子内部的相邻词，不跨句连接，不自动添加 BOS/EOS，不平滑，不 random sampling。构造完成后查询不能改变计数。句尾词若在其他位置出现过，仍可以具有后继。

### 示例

```text
sentences=[["i","like","tea"],["i","like","tea"],["i","like","coffee"]]
model.predict("like") -> "tea"
model.probability("like","tea") -> 2/3
model.probability("like","water") -> 0.0
model.predict("tea") -> None
model.predict("unknown") -> None
```

## 解题思路与参考答案

Bigram 模型根据前一个词预测下一个词。训练时统计相邻词对，查询时在当前词的后继里选频次最高的词。

对前词 u 和后继 v，记 $C(u,v)$ 为这对词在训练语料中的相邻次数。当前词存在后继记录时，maximum likelihood estimation 是

$$
\hat P(v\mid u)=\frac{C(u,v)}{\sum_w C(u,w)}.
$$

分母统计 u 出现在有后继位置时的次数。若没有结束标记，句末 u 不贡献一条转移，不能把句末次数也放入这个分母。例子中有两句“i like tea”和一句“i like coffee”，则 like 后接 tea 的概率为 2/3，接 coffee 的概率为 1/3，应预测 tea。

原帖要求基于训练文本的 bigram frequency 实现输入词到下一词的 API。以下接口、句界、分词与平票规则是手册重构约定：输入已经分词的句子列表；保留大小写；逐句统计；没有后继返回 None；计数平票按词的字典序返回；不添加 BOS/EOS，也不做平滑。空句和单词句没有转移。训练完成后缓存每个前词的最佳后继，供重复查询使用。

```python
from collections import Counter, defaultdict


class BigramPredictor:
    def __init__(self, sentences):
        self.counts = defaultdict(Counter)
        for sentence in sentences:
            for previous, following in zip(sentence, sentence[1:]):
                self.counts[previous][following] += 1
        self.best = {
            previous: min(counts, key=lambda word: (-counts[word], word))
            for previous, counts in self.counts.items()
        }

    def predict(self, word):
        return self.best.get(word)

    def probability(self, previous, following):
        counts = self.counts.get(previous)
        if not counts:
            return None
        return counts.get(following, 0) / sum(counts.values())
```

`predict` 只查询训练时算好的结果；`probability` 便于解释频次与条件概率，没有为每次查询缓存分母。后者遇到已知上下文但未见后继时返回 0；没有上下文记录时返回 None，表示本练习没有定义该条件分布。

设训练语料有 T 个 token、B 个不同 bigram。按常见哈希表均摊分析，计数和预计算最佳后继耗时 $O(T+B)$，存储 $O(B)$；`predict` 的字典查询均摊为 $O(1)$。这些复杂度把单个 token 的哈希与比较视为常数；非常长的字符串还要计入字符串处理成本。`probability` 对有 r 个不同后继的上下文需要 $O(r)$ 求和。

**如何验证句子没有被接起来？**
用两句 ["a", "b"]、["c", "d"] 训练。应有 a→b 和 c→d，查询 b 得到 None，不能出现 b→c。还要验证空语料、单词句、重复词对、平票和未见词。

**怎样处理未见 bigram？**
可以引入平滑或回退分布，但要重新定义 vocabulary 与概率规则。简单的加一平滑要给固定 vocabulary 里的所有后继留概率质量；若每次只在已见后继上加一，就没有解决未见后继概率为零的问题。

**词频最高的词就是最佳后继吗？**
要看当前上下文的条件计数。一个词在全语料很常见，也可能从未出现在当前词之后。无上下文时的 unigram 回退是另外一种明确的产品规则。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

like 后面出现两次 tea、一次 coffee，概率应分别为 2/3 与 1/3。tea 没有后继，不能跨句连接到下一句开头；未知词也没有预测。

```python
import math

model = BigramPredictor(
    [["i", "like", "tea"], ["i", "like", "tea"], ["i", "like", "coffee"]]
)
assert model.predict("like") == "tea"
assert math.isclose(model.probability("like", "tea"), 2 / 3)
assert model.predict("tea") is None
assert model.predict("unknown") is None
print("simple tests passed")
```
