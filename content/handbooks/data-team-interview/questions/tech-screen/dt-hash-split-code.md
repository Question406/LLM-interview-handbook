---
id: dt-hash-split-code
section: tech-screen
order: 25
level: A
title: CoderPad：训练 / 开发 / 门禁怎么稳定切开，怎样才不会泄漏？
quick: "对稳定的 group_id 做哈希再取模，让同一仓库、书、线程或近重复簇整组落在训练或评测的同一侧。随机 shuffle 会把同一篇转载拆到两边，让记忆看起来像泛化。种子和规范化版本要记录，重跑才稳定；时间泄漏和生成 prompt 里混入评测题，哈希解决不了，要单独查。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Evaluation
  - Split
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: Datasheets for Datasets
    url: https://arxiv.org/abs/1803.09010
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
---

我会对稳定的组键做哈希再取模，决定一条数据进 train、dev 还是 holdout。用组键是为了让同一仓库、同一本书、同一个对话线程或同一个近重复簇整组落在同一侧。

比如一篇博客被转载了三次，随机 `shuffle` 切 90/10，很可能两份进训练、一份进评测，模型背下来的东西在评测上看起来就像泛化。固定组键和种子之后，新增文档或者重跑流程，已有文档的划分都不变；单次 `random.random() < 0.1` 做不到这一点。

键用已经规范化的 URL 或稳定的 `doc_id`，规范化见 `dt-url-canon-code`。有 `group_id`（仓库、ISBN、thread_id）的文档先映射到组键，再对组键哈希，组内文档跟着组走。

```python
import hashlib


def bucket(key, n_buckets=1000, seed="split-v3"):
    """把 key 稳定映射到 [0, n_buckets)。同一 seed 下结果不随运行变化。"""
    digest = hashlib.blake2b(f"{seed}:{key}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "little") % n_buckets


def split_of(group_id, holdout_frac=0.02, dev_frac=0.03, n_buckets=1000, seed="split-v3"):
    """按组键划分 holdout / dev / train，同组文档总落在同一侧。"""
    if holdout_frac < 0 or dev_frac < 0 or holdout_frac + dev_frac > 1:
        raise ValueError("fractions must be non-negative and sum to at most 1")
    b = bucket(group_id, n_buckets, seed)
    # 用 round 而不是 int：int(0.58 * 100) 会因浮点误差变成 57
    n_holdout = round(holdout_frac * n_buckets)
    n_dev = round(dev_frac * n_buckets)
    if b < n_holdout:
        return "holdout"
    if b < n_holdout + n_dev:
        return "dev"
    return "train"
```

测试覆盖可复现、换种子、比例和浮点边界：

```python
from collections import Counter

# 同一组键、同一 seed，重跑结果完全一致
assert split_of("repo:torvalds/linux") == split_of("repo:torvalds/linux")
assert bucket("isbn:123", seed="split-v3") == bucket("isbn:123", seed="split-v3")

# 换 seed 等于换一套划分
keys = [f"doc-{i}" for i in range(200)]
assert [bucket(k, seed="a") for k in keys] != [bucket(k, seed="b") for k in keys]

# 比例大致对得上：2% holdout、3% dev
counts = Counter(split_of(f"group-{i}") for i in range(100_000))
assert 1_700 < counts["holdout"] < 2_300
assert 2_600 < counts["dev"] < 3_400

# 浮点比例按 round 取整：落在第 57 号桶的组属于 58% 的 holdout
edge_key = next(f"k{i}" for i in range(10_000) if bucket(f"k{i}", n_buckets=100, seed="s") == 57)
assert split_of(edge_key, holdout_frac=0.58, dev_frac=0.0, n_buckets=100, seed="s") == "holdout"

# 比例之和超过 1 是配置错误
try:
    split_of("x", holdout_frac=0.6, dev_frac=0.5)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

每条数据一次哈希，线性扫一遍就完，不需要全局 shuffle，所以分布式跑也没问题。`seed` 要写进 dataset card，改种子等于换了一套门禁，新旧数字不能比。holdout 比例按题量定，别按 token 体积：网页 token 的 2% 可能就是几亿文档，评测用不完，也浪费。SFT 和人标集的 holdout 按条切；预训练的污染扫描针对冻结题，见 `dt-ngram-contam-code`。

## 哈希防不住的泄漏

哈希只认 id，两篇近重复文档 id 不同就可能分到两边，所以要先聚类（`dt-lsh-cluster-code`），用簇的代表 id 当 `group_id`。时间泄漏它也管不了，训练之后才出现的题，代码题要用截止日之后的新题做门禁，也就是 LiveCodeBench 那套。还有合成自污染：教师模型把门禁题当 few-shot 来生成训练集，生成 prompt 里贴进去的评测题哈希划分发现不了，要另外查，见 `dt-self-improve`。

开发集可以跟着模型一起长，门禁集要冻结，`dev` 和 `holdout` 别共用哈希区间。

## 追问

**要不要按语言分层切？**
可以。先分语言桶，桶内再哈希，保证低资源语言也有门禁条目；全局切一刀，稀有语言可能全进 train。

**会话数据按什么分组？**
按 thread 切。按轮次切，同一段对话会被拆到训练和评测两边。

**重跑 pipeline 数字漂了？**
先核对 `seed` 和规范化版本，lineage 对不上的情况见 `dt-repro-lineage`。

**比例为什么用 round 算桶数？**
`int(0.58 * 100)` 会因为浮点误差变成 57，边界上的组就被分错了，测试里专门有一条覆盖这个。

相关：`dt-url-canon-code`、`dt-ngram-contam-code`、`dt-lsh-cluster-code`、`dt-self-improve`、`dt-repro-lineage`
