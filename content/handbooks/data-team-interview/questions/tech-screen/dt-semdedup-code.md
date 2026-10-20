---
id: dt-semdedup-code
section: tech-screen
order: 13
level: A
title: CoderPad：embedding 近邻去语义重复，什么子集才值得上？
quick: "对已经过精确哈希和 MinHash 的高价值子集，再用 embedding 查找释义重复：ANN 取 top-$k$，余弦相似度超过阈值的归入同簇，保留质量最高的一条。适合许可书、SFT 和通过 verifier 的合成数据；十亿级网页不宜直接全量使用。"
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

先做精确哈希和 MinHash，再对高价值子集计算 embedding。用 ANN 取 top-$k$ 近邻，将余弦相似度超过阈值的文档归入同簇，保留质量最高的一条。十亿级网页不适合直接全量使用，更不能用 `for i in docs: for j in docs` 两两比较。MinHash 难以发现换说法的重复，这一层用来补充。

SemDeDup 在 C4 / 网页上证明语义近邻浪费算力。成本比 LSH 高两个数量级。CoderPad 里 ANN 用暴力余弦顶上；口播生产是 Faiss IVF / HNSW，向量离线打。

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

贪心按质量留，只和已留的比余弦，避免簇里留下 boilerplate。生产把内层换成 ANN top-k。

## 阈值和误杀

0.9 对释义紧，对同一主题的不同证明会误杀。数学 / 代码阈值更高，论坛答疑更低。按域扫，抽 100 对看：正当不同解答 vs 改写题。

翻译对是语义近邻。多语桶不要和英语混着 SemDeDup，否则会把母语页当成英语页的重复扔掉，会损害 `dt-locale-data` 讨论的母语覆盖。

合成数据：同一输入提示 的 $k$ 条 completion 余弦会很高，该由 `dt-rejection-sample-code` 的 验证器（verifier） 留对的，不能只按语义相似度留一条，否则会丢掉不同的正确解法。

## 追问

- **为什么不替代 MinHash？** 嵌入模型自己会偏英语、偏新闻。词面转载 MinHash 更稳、更便宜。两层叠，不互相替代。
- **簇里留中心还是留质量最高？** 留质量最高。中心可能是一篇平庸转载。
- **10B 网页呢？** 先 MinHash 砍到高价值 1%，再 embed。全量 embed 不是这轮 CoderPad 的答案。
