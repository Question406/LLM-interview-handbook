---
id: dt-lsh-cluster-code
section: tech-screen
order: 18
level: A
title: CoderPad：LSH 候选对怎么并成 near-duplicates cluster，cluster 里留哪一条？
quick: >-
  对 LSH 候选对先算精确 Jaccard，只给达到阈值的文档对连边，再用并查集求连通分量，得到 near-duplicates cluster。每个
  cluster 保留质量最高的一条，缺质量分时才看长度。异常大的 cluster 多半是公共模板造成的误连，要剥掉模板、分域后重新聚类。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: 'Mining of Massive Datasets, Ch.3'
    url: 'http://infolab.stanford.edu/~ullman/mmds/ch3n.pdf'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

将 near-duplicates 候选对变成 document cluster，并为每个 cluster 选一个质量代表。候选对只是待复核关系，不能因为进入候选列表就认定两篇相似。

### 输入与接口

- `clusters(pairs,jaccard_fn,threshold=0.8)` 接受文档 ID 对列表和精确相似度回调 `jaccard_fn(a,b)`。
- `pick(groups,quality,max_cluster_size=50000)` 接受 document cluster、`doc_id -> 质量分` 字典和允许的最大 cluster 大小。ID 保证可排序。

### 输出与约束

`clusters` 返回通过阈值的关系形成的连通 document cluster，候选中出现但没有通过任何边的文档也返回单元素 cluster。`pick` 返回 `(kept,dropped)`，dropped 中每项是 `(被移除ID,保留代表ID)` 或 `(ID,"huge_component")`。

相似度大于等于阈值才确认关系，关系具有传递闭包。普通 cluster 保留质量最高者，质量缺失按 0；同分取 ID 最小者。大于 `max_cluster_size` 的 cluster 全部标为 `huge_component`，不保留代表。

### 示例

```text
pairs=[(1,2),(2,3)]，两对相似度都为0.9
clusters(pairs,score_fn,0.8) -> [[1,2,3]]（cluster 之间及各 cluster 内部的顺序不限）
pick([[1,2,3]],{1:0.2,2:0.9,3:0.5}) -> ([2],[(1,2),(3,2)])
```

## 解题思路与参考答案

我会对 LSH 候选对先算精确 Jaccard，过阈值的才连边，再用并查集求连通分量，每个 cluster 留质量最高的一条。`dt-minhash-code` 停在候选对这一步，这题接着把成对关系形成 clusters。

要形成 clusters，是因为一对一对地扔扔不干净。比如一篇文章被转载成 A、B、C 三份，A-B 像、B-C 像，一对一对地扔，很容易三份里还留着两份。连通分量把整个转载家族归到一起，只留一个代表。

边只连复核过的对。LSH 的粗候选有假阳性，并查集会把这些错误传递下去，最后把无关文档焊成一个 800 万的分量。复核过也不够保险，版权声明这类公共模板照样会造成误连，所以异常大的分量要按域拆分，或者去掉模板后重新聚类。

## 并查集，再按 cluster 挑

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
    """quality: doc_id -> float。每个 cluster 留最高分，同分留 id 小的，保证结果稳定。

    返回 (kept, dropped)，dropped 是 (doc_id, 保留的代表或 "huge_component")。
    """
    kept = []
    dropped = []
    for group in groups:
        if len(group) > max_cluster_size:
            # 异常大的分量多半是模板误连，整个 cluster 回炉，不按质量留一条
            dropped.extend((x, "huge_component") for x in group)
            continue
        ranked = sorted(group, key=lambda x: (-quality.get(x, 0.0), x))
        kept.append(ranked[0])
        dropped.extend((x, ranked[0]) for x in ranked[1:])
    return kept, dropped
```

测试覆盖传递闭包、按质量挑代表、同分稳定、超大分量和长链：

```python
similar = {frozenset(p) for p in [(1, 2), (2, 3), (10, 11)]}


def fake_jaccard(a, b):
    """测试桩：给定的对相似度 0.9，其余 0.1。"""
    return 0.9 if frozenset((a, b)) in similar else 0.1


# 传递闭包：1-2、2-3 相似，三者进同一个 cluster；未过阈值的候选对不连边
candidate_pairs = [(1, 2), (2, 3), (10, 11), (3, 10), (20, 21)]
groups = sorted(sorted(g) for g in clusters(candidate_pairs, fake_jaccard))
assert groups == [[1, 2, 3], [10, 11], [20], [21]]

# 每个 cluster 留质量最高的一条，其余记下代表
kept, dropped = pick([[1, 2, 3]], quality={1: 0.2, 2: 0.9, 3: 0.5})
assert kept == [2]
assert sorted(dropped) == [(1, 2), (3, 2)]

# 同分时留 id 小的，结果稳定
assert pick([[7, 5]], quality={5: 0.5, 7: 0.5})[0] == [5]

# 超大分量整个 cluster 标记，不留代表
kept, dropped = pick([[1, 2, 3]], quality={}, max_cluster_size=2)
assert kept == []
assert dropped == [(1, "huge_component"), (2, "huge_component"), (3, "huge_component")]

# 长链合并后 find 仍指向同一个根
dsu = DSU()
for i in range(1000):
    dsu.union(i, i + 1)
assert len({dsu.find(i) for i in range(1001)}) == 1
```

`huge_component` 通常来自版权声明、cookie 文案和许可证头。这种 cluster 要回炉，剥掉 boilerplate 再跑一遍，见 `dt-boilerplate-code`；直接按质量留一条的话，留下的会是一篇「最像许可证」的网页。

## 规模

并查集带路径减半和按秩合并，每次操作接近常数。$N=10^9$ 时，DSU 用整数 doc_id，边只有通过 LSH 和复核的那一小部分，别对全部文档 `add`。单机内存扛不住就按域分片聚类，跨域的转载靠 URL 规范化之后再建一张小图，见 `dt-url-canon-code`。

聚类范围也要定。FineWeb 讨论过 global deduplication 和快照内 deduplication 的区别：在快照内聚类还是跨 crawl 聚类，会决定「反复出现的好页面」会不会被 false rejection，见 `dt-global-dedup`。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert groups == [[1, 2, 3], [10, 11], [20], [21]]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**留最长的还是质量最高的？**
默认留质量最高的。最长的往往是带导航的镜像，缺质量分时才退回按长度选。

**cluster 里两条是同一本许可书的不同章节？**
Jaccard 高，但它们不是转载。按域提高阈值，或者禁止跨「书 id」合并。

**并查集的路径压缩要写吗？**
要。面试官看的就是你会不会把树退化成 $O(N)$ 深的链。

**为什么候选对不能直接连边？**
LSH 候选有假阳性，并查集会把错误传递开，最后焊出一个几百万的分量，所以先用精确 Jaccard 复核。

相关：`dt-minhash-code`、`dt-boilerplate-code`、`dt-url-canon-code`、`dt-global-dedup`
