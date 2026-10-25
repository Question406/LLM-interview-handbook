---
id: dt-semdedup-code
section: tech-screen
order: 13
level: A
title: CoderPad：embedding 近邻去语义重复，什么子集才值得上？
quick: "MinHash 抓不到换了说法的重复，这一层用 embedding 来补：对已经过精确哈希和 MinHash 的高价值子集，用 ANN 取 top-$k$ 近邻，余弦相似度超过阈值的归入同簇，保留质量最高的一条。适合许可书、SFT 和通过 verifier 的合成数据；成本高，十亿级网页不宜直接全量跑。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Dedup
  - Embedding
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "SemDeDup: Data-efficient learning at web-scale through semantic deduplication"
    url: https://arxiv.org/abs/2303.09540
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

依据文档向量的余弦相似度去除语义近重复，并优先保留高质量文档。

### 输入与接口

实现 `l2_norm`(v)、cosine(a,b) 和 semdedup(items, threshold=0.9)。items 中每项为 (`doc_id`,quality,embedding)，`doc_id` 唯一，quality 为有限数，向量是同维有限数序列。threshold 在 [-1,1]。`l2_norm` 返回单位长度向量，零向量保持零；cosine 接收已经归一化的向量并返回点积。

### 输出与约束

semdedup 返回 (kept,dropped)：kept 为 (`doc_id`,quality) 列表；dropped 为 (`doc_id`,`representative_id`) 列表。按 quality 降序处理，质量相同按输入顺序。

某文档与已经保留的任一代表的余弦相似度至少为 threshold 时丢弃，关联到按保留顺序遇到的第一个合格代表；否则成为新代表。两个返回列表都保持处理顺序。该规则只与已经保留的代表比较，不要求计算相似关系的传递闭包。

### 示例

```text
items=[("paraphrase",0.5,[1,0.1,0]),("original",0.9,[1,0,0]),("other",0.4,[0,1,0])]
semdedup(items,0.9)
-> ([("original",0.9),("other",0.4)],[("paraphrase","original")])
```

## 解题思路与参考答案

我会在精确哈希和 MinHash 之后，只对高价值子集算 embedding，用 ANN 取 top-$k$ 近邻，余弦超过阈值的归入同簇，每簇留质量最高的一条。MinHash 看的是词面，换了说法的重复它抓不到，语义去重补的就是这一层。

比如一道题的原文和一份改写，词面几乎不重叠，embedding 却几乎同方向，测试里的 `original` 和 `paraphrase` 余弦约 0.995。SemDeDup 在 C4 和网页上证明了语义近邻会浪费算力，但它的成本比 LSH 高两个数量级，所以十亿级网页别直接全量跑，更别写 `for i in docs: for j in docs` 两两比较。CoderPad 里用暴力余弦代替 ANN，要说明生产上用 Faiss IVF / HNSW，向量离线算好。

## 先桶，再 ANN，再留一条

实现是贪心的：按质量从高到低处理，每条只和已经留下的比余弦，这样簇里留下的总是质量最高的，不会是 boilerplate。

```python
import math


def l2_norm(vector):
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def cosine(a, b):
    """a、b 已经 L2 归一化时，点积就是余弦。"""
    return sum(x * y for x, y in zip(a, b))


def semdedup(items, threshold=0.9):
    """items: list[(doc_id, quality, embedding)]。

    贪心：按质量降序，和已保留样本比余弦，超过阈值就扔。生产把内层循环换成 ANN top-k。
    返回 (kept, dropped)：kept 是 [(doc_id, quality)]，dropped 是 [(doc_id, 与之重复的保留 id)]。
    """
    ranked = sorted(items, key=lambda item: -item[1])
    kept = []
    kept_vecs = []
    dropped = []
    for doc_id, quality, vector in ranked:
        unit = l2_norm(vector)
        duplicate_of = None
        for (kept_id, _), kept_vec in zip(kept, kept_vecs):
            if cosine(unit, kept_vec) >= threshold:
                duplicate_of = kept_id
                break
        if duplicate_of is None:
            kept.append((doc_id, quality))
            kept_vecs.append(unit)
        else:
            dropped.append((doc_id, duplicate_of))
    return kept, dropped
```

测试覆盖留高质量、调阈值、长度无关和零向量：

```python
items = [
    ("paraphrase", 0.5, [1.0, 0.1, 0.0]),
    ("original", 0.9, [1.0, 0.0, 0.0]),
    ("other_topic", 0.4, [0.0, 1.0, 0.0]),
]

# 语义近邻只留质量最高的一条，另一条记下重复对象
kept, dropped = semdedup(items, threshold=0.9)
assert kept == [("original", 0.9), ("other_topic", 0.4)]
assert dropped == [("paraphrase", "original")]

# 阈值调高后，余弦约 0.995 的改写也被保留
kept, dropped = semdedup(items, threshold=0.999)
assert len(kept) == 3
assert dropped == []

# 余弦和向量长度无关
assert math.isclose(cosine(l2_norm([3.0, 4.0]), l2_norm([6.0, 8.0])), 1.0)

# 零向量不除零
assert l2_norm([0.0, 0.0]) == [0.0, 0.0]
```

暴力版是 $O(N\cdot K)$，$K$ 是留下的条数，生产上把内层循环换成 ANN top-k。

## 阈值和误杀

阈值 0.9 对释义来说比较紧，但对同一主题的不同证明会误杀。数学和代码的阈值要更高，论坛答疑可以更低，按域扫，抽 100 对来看，区分正当的不同解答和改写过的题。翻译对也是语义近邻，多语言桶别和英语混在一起做 SemDeDup，不然母语页会被当成英语页的重复扔掉，伤到 `dt-locale-data` 讨论的母语覆盖。合成数据同理，同一个输入提示的 $k$ 条 completion 余弦会很高，这些应该由 `dt-rejection-sample-code` 的 verifier 留下做对的，只按语义相似度留一条，会丢掉不同的正确解法。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert kept == [("original", 0.9), ("other_topic", 0.4)]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**为什么不用它替代 MinHash？**
嵌入模型本身偏英语、偏新闻，词面转载用 MinHash 更稳也更便宜，所以两层叠加使用。

**簇里留中心还是质量最高的？**
留质量最高的，中心可能只是一篇平庸的转载。

**10B 网页怎么办？**
先用 MinHash 砍到高价值的 1%，再做 embedding。全量 embedding 不是这轮 CoderPad 要的答案。

**阈值 0.9 合适吗？**
对释义比较紧，对同一主题的不同证明会误杀。数学和代码调高，论坛答疑可以调低，按域抽 100 对看。

相关：`dt-locale-data`、`dt-rejection-sample-code`
