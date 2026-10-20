---
id: dt-exact-dedup-code
section: tech-screen
order: 4
level: A
title: CoderPad：精确去重怎么写，Bloom 和哈希表怎么选？
quick: "规范化后生成指纹，用 set 或外部存储检查精确重复。大规模时 Bloom 只筛「可能见过」，还要精确复核，避免误删。近重复另用 MinHash；opt-out 撤回用精确墓碑表，不能靠不支持删除的 Bloom。"
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

先规范化正文，再生成指纹。内存足够时，用 `set` 保存已见指纹；$N$ 达到十亿时，可用 Bloom 筛可能重复的文档，再查询落盘的精确记录。精确去重主要处理规范化后相同的内容，近重复还需要 MinHash。要解释误报和漏报：直接对原文 `hash(text)` 会受空白、页脚变化影响；Bloom 则可能误报重复。

Lee et al. 2021：训练里的复制浪费算力，也会让评测里的「新文档」变熟。精确去重是第一刀，MinHash 是第二刀，见 `dt-minhash-code`。

## 规范化比哈希重要

转载常见差一个页脚。先做便宜规范化：小写、压缩空白、丢掉 HTML、切掉前后 200 字符的导航。规范化过度会把两篇正当短文打成一样，所以规则按域开。然后对规范化正文做 128-bit 指纹（blake2 / sha1 截断）。

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

还要估算内存：`set` 在 $N=10^8$、16 字节指纹时大约 1.6 GB 只算 key，再加上 Python 对象开销。网页级用外部 KV 或排序去重（指纹排序，相邻相同则丢）。

## Bloom：省内存，承认误杀

Bloom 使用 $m$ bit 和 $k$ 个哈希函数，插入 $n$ 条后假阳性约 $(1-e^{-kn/m})^k$。最优 $k=(m/n)\ln 2$。它只回答「可能见过」。假阳性会误杀从未出现的文档，所以高价值域（许可书、验证数学）不要只靠 Bloom 丢掉，要再查精确指纹。

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

### 可执行测试

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

口播：Bloom 不支持删除。文档要撤回（opt-out URL）时，用精确指纹的墓碑表，不能指望改 Bloom。Applebot opt-out 是真实约束，见 `dt-legal-capability`。

## 追问

- **按行去重还是按文档？** 预训练常按段落；监督微调（SFT） 按整条 `(prompt, completion)`。代码仓库按文件会把正当的重复 license 头杀光，license 要白名单。
- **和评测隔离谁先？** 先对冻结评测建指纹，训练文档命中就进 quarantine，不要等训练内部去重做完。
- **假阳性 1% 能接受吗？** 看桶。bulk crawl 可以；验证数学和许可书不行。
