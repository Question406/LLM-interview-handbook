---
id: dt-countmin-code
section: tech-screen
order: 29
level: A
title: CoderPad：十亿文档里找高频样板 n-gram，Count-Min 怎么写？
quick: "用 $d$ 行 $w$ 列计数器，每个 n-gram 经 $d$ 个哈希分别计数，查询时取最小值估计频率。版权声明、导航和 cookie 提示等高频片段，可以在复核后剥除。哈希碰撞只会抬高估计值，因此阈值要留余量，并抽查超阈值候选。"
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

我会先写 $d$ 行 $w$ 列的 Count-Min：每个 gram 用 $d$ 个哈希各加一，估计取 $d$ 行最小值。对超过频率阈值的版权声明、导航和 cookie 提示做抽查，再从正文中剥除。估计值可能因哈希碰撞偏高，因此阈值要留余量。精确计数要一张十亿级哈希表，sketch 用固定内存估频率。MinHash 去近重复文档；同一句版权声明嵌在无数不相关页里，文档级 Jaccard 并不高，要找跨文档高频片段。

误差大约 $O(N/w)$，$N$ 是总增量次数。$d=\lceil\ln(1/\delta)\rceil$ 行控制失败概率。现场 $w=2^{20}$、$d=4$ 量级够讲。

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

第一遍：每个文档的 8-gram 加一（文档内先去重，避免一篇长文把自己的句子打成「全球高频」）。第二遍：估计过阈值的 gram 当样板，从正文里剥或整篇 quarantine。

文档内去重：

```python
def grams(text, n=8):
    tokens = text.lower().split()
    return {" ".join(tokens[i:i + n]) for i in range(max(len(tokens) - n + 1, 0))}


def add_doc(sketch, text):
    """每篇文档里的同一个 gram 只计一次，sketch 统计的是文档频率。"""
    for gram in grams(text):
        sketch.add(gram)
```

### 可执行测试

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

## 失败模式

高估：两个无关稀有 gram 撞同一格子，估计偏高。所以过阈值的要抽查，或第二层精确计数只对候选 gram。Count-Min 不低估，漏报少、误报靠复核。

正当高频：`the united states of america`、公式、`for i in range`。按域分 sketch，代码桶和网页桶分开。许可证白名单。

和 `dt-boilerplate-code` 的分工：密度法看 DOM 结构；Count-Min 看跨页重复字符串。JS 渲染后的站点两层都要。

内存账：$d\cdot w$ 个整型。$d=4$、$w=2^{20}$ 大约几十 MB。比存全部 gram 计数小几个数量级。

## 追问

- **为什么不用 HyperLogLog？** HLL 估的是基数（有多少不同 gram），不估某一个 gram 出现几次。高频检测用 Count-Min。
- **能减计数吗？** 标准 Count-Min 不支持删除。opt-out 撤回用精确墓碑，见 `dt-exact-dedup-code`。
- **阈值怎么定？** 按「出现在多少文档」而不是多少次 文本处理单位（token）。扫文档频率的分位数，人工看 top 100 gram。
