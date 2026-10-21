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

MinHash 看的是词面，换了说法的重复它抓不到，语义去重补的就是这一层。做法是在精确哈希和 MinHash 之后，只对高价值子集算 embedding，用 ANN 取 top-$k$ 近邻，余弦相似度超过阈值的归入同簇，每簇保留质量最高的一条。十亿级网页不适合直接全量跑，更不能写 `for i in docs: for j in docs` 两两比较。

SemDeDup 在 C4 和网页上证明了语义近邻会浪费算力，但它的成本比 LSH 高两个数量级。CoderPad 里用暴力余弦代替 ANN；要说明生产上用 Faiss IVF / HNSW，向量离线算好。

## 合同：先桶，再 ANN，再留一条

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

### 可执行测试

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

实现是贪心的：按质量从高到低处理，每条只和已经留下的比余弦，这样簇里不会留下 boilerplate。生产上把内层循环换成 ANN top-k。

## 阈值和误杀

阈值 0.9 对释义来说比较紧，但对同一主题的不同证明会误杀。数学和代码的阈值要更高，论坛答疑可以更低。按域扫，抽 100 对来看，区分正当的不同解答和改写过的题。

翻译对也是语义近邻。多语言桶不要和英语混在一起做 SemDeDup，否则母语页会被当成英语页的重复扔掉，伤到 `dt-locale-data` 讨论的母语覆盖。

合成数据同理：同一个输入提示的 $k$ 条 completion 余弦会很高。这些应该由 `dt-rejection-sample-code` 的验证器（verifier）留下做对的。只按语义相似度留一条，会丢掉不同的正确解法。

## 追问

- **为什么不用它替代 MinHash？** 嵌入模型本身偏英语、偏新闻。词面转载用 MinHash 更稳也更便宜。所以两层叠加使用。
- **簇里留中心还是质量最高的？** 留质量最高的，中心可能只是一篇平庸的转载。
- **10B 网页怎么办？** 先用 MinHash 砍到高价值的 1%，再做 embedding。全量 embedding 不是这轮 CoderPad 要的答案。
