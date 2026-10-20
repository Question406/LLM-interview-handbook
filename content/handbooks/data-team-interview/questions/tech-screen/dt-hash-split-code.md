---
id: dt-hash-split-code
section: tech-screen
order: 25
level: A
title: CoderPad：训练 / 开发 / 门禁怎么稳定切开，怎样才不会泄漏？
quick: "使用稳定 group_id 哈希划分，同一仓库、书、线程或近重复簇不跨训练和评测。记录种子与规范化版本，让重跑结果稳定。哈希不能解决时间泄漏或生成 prompt 带评测题，还要单独检查这两类污染。"
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

按稳定文档 id 或规范化 URL 哈希，取模划分。更重要的是，同一仓库、书、对话线程或近重复簇要整组进入同一侧。随机 `shuffle` 切 90/10，可能把同一转载拆到训练与评测，让记忆看起来像泛化。固定组键和种子后，新增文档、重跑流程仍能保持划分；单次 `random.random() < 0.1` 做不到这一点。

## 哈希组，不要打散近邻

键用已经规范化的 URL 或稳定 `doc_id`，见 `dt-url-canon-code`。同一 `group_id`（仓库、ISBN、thread_id）先映射到组键，再哈希。组内文档跟着组走。

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

### 可执行测试

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

`seed` 写进 dataset card。改种子等于换了一套门禁，旧数字不能比。Holdout 比例按题量定，不是按 token 体积；网页 token 的 2% 可能是几亿文档，评测用不完，也浪费。监督微调（SFT） / 人标集 holdout 按条，预训练污染扫描按冻结题，见 `dt-ngram-contam-code`。

## 三种泄漏

1. 近重复跨切。先聚类，见 `dt-lsh-cluster-code`，簇的代表 id 当 `group_id`。
2. 时间泄漏。代码题用截止日后的新题当门禁，LiveCodeBench 那套。哈希切解决不了「训练之后才出现的题」。
3. 合成自污染。教师用门禁题当 few-shot 再生成训练集。哈希划分发现不了生成 prompt 中贴入的评测题，要另查，见 `dt-self-improve`。

开发集可以跟着模型长。门禁冻结。`dev` 和 `holdout` 不要共用哈希区间。

## 追问

- **按语言分层切？** 可以：先语言桶，桶内再哈希，保证低资源也有门禁条。全局一刀会让稀有语全进 train。
- **用户 id 当组？** 苹果基础模型默认不用用户对话。研究集若有会话，按 thread 切，不要按轮次切。
- **重跑 pipeline 数字漂了？** 先对 `seed` 和规范化版本。lineage 对不上，见 `dt-repro-lineage`。
