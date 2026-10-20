---
id: dt-lsh-cluster-code
section: tech-screen
order: 18
level: A
title: CoderPad：LSH 候选对怎么并成近重复簇，簇里留哪一条？
quick: "先对 LSH 候选计算精确 Jaccard，只连接达到阈值的文档对，再用并查集找连通分量。每簇优先保留质量最高的一条，缺少质量分时才参考长度。异常大簇可能由公共模板误连造成，应剥除模板、分域后重新聚类。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Dedup
  - Union-Find
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: "Mining of Massive Datasets, Ch.3"
    url: http://infolab.stanford.edu/~ullman/mmds/ch3n.pdf
    type: primary
---

先对候选文档对计算精确 Jaccard，相似度超过阈值才连边，再用并查集得到近重复簇。每簇留质量最高的一条。异常大的分量可能来自版权声明等公共模板导致的误连，要按域拆分或去掉模板后重新聚类。`dt-minhash-code` 停在候选对；一对一对扔会把同一转载家族留下多条。

边必须是复核过的对，不是 LSH 粗候选。LSH 假阳性会把无关文档焊成一个 800 万的分量。

## 并查集，再按簇挑

```python
from collections import defaultdict


class DSU:
    """并查集：路径减半 + 按秩合并。"""

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        self.add(x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1


def clusters(pairs, jaccard_fn, threshold=0.8):
    """pairs 是 LSH 候选对；只有精确 Jaccard 复核过阈值的对才连边。"""
    dsu = DSU()
    for a, b in pairs:
        dsu.add(a)
        dsu.add(b)
        if jaccard_fn(a, b) >= threshold:
            dsu.union(a, b)
    groups = defaultdict(list)
    for x in dsu.parent:
        groups[dsu.find(x)].append(x)
    return list(groups.values())


def pick(groups, quality, max_cluster_size=50_000):
    """quality: doc_id -> float。每簇留最高分，同分留 id 小的，保证结果稳定。

    返回 (kept, dropped)，dropped 是 (doc_id, 保留的代表或 "huge_component")。
    """
    kept = []
    dropped = []
    for group in groups:
        if len(group) > max_cluster_size:
            # 异常大的分量多半是模板误连，整簇回炉，不按质量留一条
            dropped.extend((x, "huge_component") for x in group)
            continue
        ranked = sorted(group, key=lambda x: (-quality.get(x, 0.0), x))
        kept.append(ranked[0])
        dropped.extend((x, ranked[0]) for x in ranked[1:])
    return kept, dropped
```

### 可执行测试

```python
similar = {frozenset(p) for p in [(1, 2), (2, 3), (10, 11)]}


def fake_jaccard(a, b):
    """测试桩：给定的对相似度 0.9，其余 0.1。"""
    return 0.9 if frozenset((a, b)) in similar else 0.1


# 传递闭包：1-2、2-3 相似，三者进同一簇；未过阈值的候选对不连边
candidate_pairs = [(1, 2), (2, 3), (10, 11), (3, 10), (20, 21)]
groups = sorted(sorted(g) for g in clusters(candidate_pairs, fake_jaccard))
assert groups == [[1, 2, 3], [10, 11], [20], [21]]

# 每簇留质量最高的一条，其余记下代表
kept, dropped = pick([[1, 2, 3]], quality={1: 0.2, 2: 0.9, 3: 0.5})
assert kept == [2]
assert sorted(dropped) == [(1, 2), (3, 2)]

# 同分时留 id 小的，结果稳定
assert pick([[7, 5]], quality={5: 0.5, 7: 0.5})[0] == [5]

# 超大分量整簇标记，不留代表
kept, dropped = pick([[1, 2, 3]], quality={}, max_cluster_size=2)
assert kept == []
assert dropped == [(1, "huge_component"), (2, "huge_component"), (3, "huge_component")]

# 长链合并后 find 仍指向同一个根
dsu = DSU()
for i in range(1000):
    dsu.union(i, i + 1)
assert len({dsu.find(i) for i in range(1001)}) == 1
```

`huge_component`：版权声明、cookie 文案、许可证头。整簇既不能全留也不能按质量留一条（会留下一篇「最像许可证」的网页）。这种分量回炉：剥 boilerplate 再跑，见 `dt-boilerplate-code`。

## 规模

$N=10^9$ 时 DSU 按整数 doc_id，边是 LSH 过复核的那一小撮。不要对全部文档 `add`。单机内存扛不住就按域分片聚类，跨域转载靠 URL 规范化后再做一次小图，见 `dt-url-canon-code`。

FineWeb 讨论过全局 vs 快照内去重。聚类范围是快照内还是跨 crawl，会改变「反复出现的好页」是否被误杀，见 `dt-global-dedup`。

## 追问

- **留最长还是留最高质量？** 默认质量。最长容易是带导航的镜像。质量分缺失时再退回长度。
- **簇里两条都是许可书不同章？** Jaccard 高但不是转载。按域提高阈值，或禁止跨「书 id」合并。
- **并查集路径压缩要写吗？** 要。面试官看的就是你会不会 $O(N)$ 把树打歪。
