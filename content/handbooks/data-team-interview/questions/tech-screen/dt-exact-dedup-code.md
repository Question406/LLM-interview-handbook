---
id: dt-exact-dedup-code
section: tech-screen
order: 4
level: A
title: CoderPad：exact deduplication 怎么写，Bloom 和哈希表怎么选？
quick: >-
  先规范化正文再生成指纹，内存够时用 set 判断见没见过。十亿级时用 Bloom 先筛出「可能见过」的文档，再查落盘的精确记录复核，免得误删。exact
  deduplication 只管规范化后相同的内容，near-duplicates 另用 MinHash；opt-out 撤回要用精确墓碑表，因为
  Bloom 不支持删除。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
  - title: 'Mining of Massive Datasets, Ch.4 (Mining Data Streams)'
    url: 'http://infolab.stanford.edu/~ullman/mmds/ch4.pdf'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现文本 exact deduplication 器和一个仅作预筛的 Bloom 过滤器。文本的大小写与空白差异视为相同，标点差异仍视为不同。

### 输入与接口

- `normalize(text)` 进行本题规范化；`fingerprint(text)` 返回规范化文本的 16 字节 BLAKE2b 指纹。
- `ExactDeduper().keep(text)` 逐条接收文本并记录已经出现的指纹。练习将 128 位指纹碰撞视为可忽略。
- `Bloom(n_expected,fp_rate=0.01)` 接受预期条数和 `(0,1)` 的目标假阳性率；`add(key)`、`maybe_seen(key)` 接受字节串 key。

### 输出与约束

`normalize` 转小写、把连续空白压为一个空格并去掉首尾空白。`keep` 在第一次出现时返回 True，以后返回 False。`maybe_seen` 表示“可能见过”，不能把 True 当成精确重复结论。

Bloom 不支持删除，插入过的 key 不得出现假阴性；未插入的 key 允许以设计假阳性率被 false positive。结构应根据预期条数与假阳性率确定容量；默认千条、1% 配置的哈希个数为 7。

### 示例

```text
d=ExactDeduper()
d.keep("Hello   World\n") -> True
d.keep("hello world") -> False
d.keep("hello world!") -> True
len(fingerprint("abc")) -> 16
b=Bloom(1000); b.add(b"doc-a"); b.maybe_seen(b"doc-a") -> True
```

## 解题思路与参考答案

我会先规范化正文，再对规范化结果算 128-bit 指纹，内存够就用 `set` 记见过的指纹；到十亿级换成 Bloom 先筛，Bloom 说「可能见过」的再查落盘的精确记录，因为 Bloom 会 false positive。

最关键的一步是规范化。比如同一篇文章，一份是「Hello World\n」，转载的一份是「hello world」，直接 `hash(text)` 两个指纹不一样，就漏掉了。转载最常见的差别是多一个页脚，所以先做便宜的规范化：小写、压缩空白、丢掉 HTML、切掉前后 200 字符的导航。规范化过度又会把两篇正当的短文变成一样，所以规则要按域开关。之后对规范化正文生成 128-bit 指纹，用 blake2 或 sha1 截断都行。

要做 deduplication，是因为 Lee et al. 2021 指出，training set 里的复制既浪费算力，也会让评测里的「新文档」变得眼熟。exact deduplication 是第一刀，规范化后完全相同的内容在这里处理，near-duplicates 留给第二刀 MinHash，见 `dt-minhash-code`。

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

内存要算一下：$N=10^8$、16 字节指纹时，`set` 光 key 就约 1.6 GB，还没算 Python 对象开销。网页级规模要用外部 KV，或者排序 deduplication，指纹排序后相邻相同就丢。

## Bloom 省内存，但会 false rejection

Bloom 用 $m$ bit 和 $k$ 个哈希函数，插入 $n$ 条后假阳性率约为 $(1-e^{-kn/m})^k$，最优 $k=(m/n)\ln 2$。它只能回答「可能见过」，假阳性会 false rejection 从没出现过的文档，所以高价值的域（许可书、验证过的数学）被判为见过之后，要再查一次精确指纹才能丢。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert deduper.keep("Hello   World\n")` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**按行 deduplication 还是按文档？**
pre-training 常按段落，SFT 按整条 `(prompt, completion)`。代码仓库按文件 deduplication，会把正当重复的 license 头全删掉，所以 license 要放白名单。

**和评测隔离谁先做？**
先对冻结 evaluation set 建指纹，训练文档命中就进 quarantine，别等 training set 内部 deduplication 做完再查。

**1% 的假阳性能接受吗？**
看桶。bulk crawl 可以接受，验证过的数学和许可书不行。

**opt-out 撤回怎么处理？**
Bloom 删不掉，所以用精确指纹的墓碑表，每一轮构建先查它。

相关：`dt-minhash-code`、`dt-legal-capability`
