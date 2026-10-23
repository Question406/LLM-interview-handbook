---
id: dt-countmin-code
section: tech-screen
order: 29
level: A
title: CoderPad：十亿文档里找高频样板 n-gram，Count-Min 怎么写？
quick: "要找的是跨文档反复出现的片段，比如版权声明、导航和 cookie 提示。精确计数要一张十亿级哈希表，所以用 Count-Min sketch：$d$ 行 $w$ 列计数器，每个 n-gram 经 $d$ 个哈希各加一，查询取 $d$ 行最小值。碰撞只会让估计偏高，阈值留余量，超阈值的候选抽查复核后再剥除。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Sketch
  - Boilerplate
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "An Improved Data Stream Summary: The Count-Min Sketch"
    url: https://www.eecs.harvard.edu/~michaelm/CS222/countmin.pdf
    type: primary
  - title: "Mining of Massive Datasets, Ch.4"
    url: http://infolab.stanford.edu/~ullman/mmds/ch4.pdf
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
---

我会用 Count-Min sketch，用固定内存估计每个 8-gram 在多少篇文档里出现过，过阈值的抽查后从正文里剥掉。精确计数要一张十亿级的哈希表，放不下。

比如「all rights reserved by example corp since the year 2001」这句页脚，嵌在成千上万篇毫不相关的新闻里。每篇文档整体的 Jaccard 都不高，MinHash 去近重复文档抓不到它，只能直接统计这个片段出现在多少篇文档里。

Count-Min 是 $d$ 行 $w$ 列计数器：每个 gram 用 $d$ 个哈希各在一行加一，查询时取 $d$ 行里的最小值当估计。误差大约是 $O(N/w)$，$N$ 是总增量次数；行数 $d=\lceil\ln(1/\delta)\rceil$ 控制失败概率。现场讲 $w=2^{20}$、$d=4$ 这个量级就够了。

## 最小值那一行才是估计

```python
import hashlib


class CountMin:
    """d 行 w 列的 Count-Min sketch。估计值只会偏高，不会偏低。"""

    def __init__(self, w=1 << 20, d=4):
        if w <= 0 or d <= 0:
            raise ValueError("w and d must be positive")
        self.w = w
        self.d = d
        self.table = [[0] * w for _ in range(d)]

    def _index(self, key, row):
        digest = hashlib.blake2b(f"{row}:{key}".encode(), digest_size=8).digest()
        return int.from_bytes(digest, "little") % self.w

    def add(self, key, count=1):
        if count < 0:
            raise ValueError("Count-Min does not support decrements")
        for row in range(self.d):
            self.table[row][self._index(key, row)] += count

    def estimate(self, key):
        return min(self.table[row][self._index(key, row)] for row in range(self.d))
```

整个流程跑两遍。第一遍对每个文档的 8-gram 加一，加之前先在文档内去重，不然一篇长文会把自己反复出现的句子刷成「全球高频」。第二遍查估计值，过阈值的 gram 当样板，从正文里剥掉，或者把整篇 quarantine。文档内去重这样写：

```python
def grams(text, n=8):
    tokens = text.lower().split()
    return {" ".join(tokens[i:i + n]) for i in range(max(len(tokens) - n + 1, 0))}


def add_doc(sketch, text):
    """每篇文档里的同一个 gram 只计一次，sketch 统计的是文档频率。"""
    for gram in grams(text):
        sketch.add(gram)
```

测试覆盖无碰撞时精确、窄表只会高估、不支持减计数、文档内去重：

```python
# 宽表上没有碰撞时，估计值等于真实计数
sketch = CountMin(w=1 << 12, d=4)
sketch.add("cookie notice", 3)
sketch.add("privacy policy")
assert sketch.estimate("cookie notice") == 3
assert sketch.estimate("privacy policy") == 1
assert sketch.estimate("never seen") == 0

# 极窄的表必然碰撞：估计只会偏高，不会低于真实计数
narrow = CountMin(w=2, d=2)
for i in range(20):
    narrow.add(f"key-{i}")
assert all(narrow.estimate(f"key-{i}") >= 1 for i in range(20))

# 标准 Count-Min 不支持减计数
try:
    sketch.add("cookie notice", -1)
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# 文档内去重：一篇文档重复同一句话，也只给每个 8-gram 加一
footer = "all rights reserved by example corp since the year 2001"
doc_sketch = CountMin(w=1 << 12, d=4)
add_doc(doc_sketch, footer + " " + footer)
add_doc(doc_sketch, "news story text " + footer)
assert doc_sketch.estimate("all rights reserved by example corp since the") == 2

# 短于 n 个词的文本没有 gram
assert grams("too short", n=8) == set()
```

内存总共 $d\cdot w$ 个整型，$d=4$、$w=2^{20}$ 大约几十 MB，比存全部 gram 的计数小几个数量级。每次加和查都是 $d$ 次哈希。

## 会错在哪

一种是高估：两个无关的稀有 gram 撞到同一个格子，估计就偏高。Count-Min 不会低估，所以漏报少，误报靠复核，过阈值的 gram 抽查，或者只对候选 gram 再做一层精确计数。另一种是正当的高频片段，比如 `the united states of america`、公式、`for i in range`，办法是按域分 sketch，代码桶和网页桶分开，许可证文本放白名单。

它和 `dt-boilerplate-code` 是分工关系：密度法看 DOM 结构，Count-Min 看跨页重复的字符串，JS 渲染的站点两层都要用。

## 追问

**为什么不用 HyperLogLog？**
HLL 估的是基数，也就是有多少种不同的 gram，估不了某一个 gram 出现几次。高频检测要用 Count-Min。

**能减计数吗？**
标准 Count-Min 不支持删除。opt-out 撤回要用精确墓碑表，见 `dt-exact-dedup-code`。

**阈值怎么定？**
按「出现在多少个文档里」定，别按出现了多少个 token 定。扫文档频率的分位数，再人工看前 100 个 gram。

**估计偏高怎么兜底？**
过阈值的候选抽查，或者只对这批候选再精确计一遍数。因为它只会高估，漏报很少，复核只用管误报。

相关：`dt-boilerplate-code`、`dt-exact-dedup-code`
