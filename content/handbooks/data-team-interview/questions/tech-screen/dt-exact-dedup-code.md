---
id: dt-exact-dedup-code
section: tech-screen
order: 4
level: A
title: CoderPad：精确去重怎么写，Bloom 和哈希表怎么选？
quick: "先规范化正文再生成指纹，内存够时用 set 判断见没见过。十亿级时用 Bloom 先筛出「可能见过」的文档，再查落盘的精确记录复核，免得误删。精确去重只管规范化后相同的内容，近重复另用 MinHash；opt-out 撤回要用精确墓碑表，因为 Bloom 不支持删除。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Dedup
  - Python
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: "Mining of Massive Datasets, Ch.4 (Mining Data Streams)"
    url: http://infolab.stanford.edu/~ullman/mmds/ch4.pdf
    type: primary
---

我会先规范化正文，再对规范化结果算 128-bit 指纹，内存够就用 `set` 记见过的指纹；到十亿级换成 Bloom 先筛，Bloom 说「可能见过」的再查落盘的精确记录，因为 Bloom 会误报。

最关键的一步是规范化。比如同一篇文章，一份是「Hello   World\n」，转载的一份是「hello world」，直接 `hash(text)` 两个指纹不一样，就漏掉了。转载最常见的差别是多一个页脚，所以先做便宜的规范化：小写、压缩空白、丢掉 HTML、切掉前后 200 字符的导航。规范化过度又会把两篇正当的短文变成一样，所以规则要按域开关。之后对规范化正文生成 128-bit 指纹，用 blake2 或 sha1 截断都行。

要做去重，是因为 Lee et al. 2021 指出，训练集里的复制既浪费算力，也会让评测里的「新文档」变得眼熟。精确去重是第一刀，规范化后完全相同的内容在这里处理，近重复留给第二刀 MinHash，见 `dt-minhash-code`。

## 指纹和 set

```python
import hashlib
import re
from math import log

WHITESPACE = re.compile(r"\s+")


def normalize(text):
    text = text.lower()
    return WHITESPACE.sub(" ", text).strip()


def fingerprint(text):
    """规范化正文的 128-bit 指纹。"""
    return hashlib.blake2b(normalize(text).encode(), digest_size=16).digest()


class ExactDeduper:
    def __init__(self):
        self.seen = set()

    def keep(self, text):
        """第一次见到这份规范化正文返回 True，之后返回 False。"""
        fp = fingerprint(text)
        if fp in self.seen:
            return False
        self.seen.add(fp)
        return True
```

内存要算一下：$N=10^8$、16 字节指纹时，`set` 光 key 就约 1.6 GB，还没算 Python 对象开销。网页级规模要用外部 KV，或者排序去重，指纹排序后相邻相同就丢。

## Bloom 省内存，但会误杀

Bloom 用 $m$ bit 和 $k$ 个哈希函数，插入 $n$ 条后假阳性率约为 $(1-e^{-kn/m})^k$，最优 $k=(m/n)\ln 2$。它只能回答「可能见过」，假阳性会误杀从没出现过的文档，所以高价值的域（许可书、验证过的数学）被判为见过之后，要再查一次精确指纹才能丢。

```python
class Bloom:
    """只回答「可能见过」：没有假阴性，但有约 fp_rate 的假阳性，且不支持删除。"""

    def __init__(self, n_expected, fp_rate=0.01):
        if n_expected <= 0:
            raise ValueError("n_expected must be positive")
        if not 0 < fp_rate < 1:
            raise ValueError("fp_rate must be in (0, 1)")
        self.m = max(8, int(-n_expected * log(fp_rate) / (log(2) ** 2)))
        self.k = max(1, round(self.m / n_expected * log(2)))
        self.bits = bytearray((self.m + 7) // 8)

    def _indices(self, key):
        # 双重哈希：用两个 64-bit 值模拟 k 个独立哈希
        digest = hashlib.blake2b(key, digest_size=16).digest()
        x = int.from_bytes(digest[:8], "little")
        y = int.from_bytes(digest[8:], "little") or 1
        for i in range(self.k):
            yield (x + i * y) % self.m

    def add(self, key):
        for i in self._indices(key):
            self.bits[i // 8] |= 1 << (i % 8)

    def maybe_seen(self, key):
        return all(self.bits[i // 8] & (1 << (i % 8)) for i in self._indices(key))
```

测试覆盖规范化、Bloom 没有假阴性、假阳性率和最优 $k$：

```python
# 大小写和空白差异在规范化后视为同一篇
deduper = ExactDeduper()
assert deduper.keep("Hello   World\n")
assert not deduper.keep("hello world")
assert deduper.keep("hello world!")

# 指纹是 16 字节
assert len(fingerprint("abc")) == 16

# Bloom 没有假阴性：插入过的 key 一定报「可能见过」
bloom = Bloom(n_expected=1000, fp_rate=0.01)
inserted = [fingerprint(f"doc {i}") for i in range(1000)]
for key in inserted:
    bloom.add(key)
assert all(bloom.maybe_seen(key) for key in inserted)

# 假阳性率在设计值附近（这里允许 3 倍余量）
false_hits = sum(bloom.maybe_seen(fingerprint(f"other {i}")) for i in range(10000))
assert false_hits / 10000 < 0.03

# 最优 k = (m/n) ln 2，fp_rate=1% 时约为 7
assert bloom.k == 7

# 参数越界直接报错
try:
    Bloom(n_expected=0)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

Bloom 还有一个限制：不支持删除。文档要撤回时（opt-out URL），用精确指纹的墓碑表记下来，后续每一轮构建都先查这张表，opt-out 的许可背景见 `dt-legal-capability`。

## 追问

**按行去重还是按文档？**
预训练常按段落，SFT 按整条 `(prompt, completion)`。代码仓库按文件去重，会把正当重复的 license 头全删掉，所以 license 要放白名单。

**和评测隔离谁先做？**
先对冻结评测集建指纹，训练文档命中就进 quarantine，别等训练集内部去重做完再查。

**1% 的假阳性能接受吗？**
看桶。bulk crawl 可以接受，验证过的数学和许可书不行。

**opt-out 撤回怎么处理？**
Bloom 删不掉，所以用精确指纹的墓碑表，每一轮构建先查它。

相关：`dt-minhash-code`、`dt-legal-capability`
