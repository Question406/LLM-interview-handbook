---
id: dt-length-bucket-code
section: tech-screen
order: 28
level: A
title: CoderPad：按长度分层抽样怎么写，短模板淹没长文档怎么避免？
quick: "按 token 数划分长度桶（2k / 8k / 32k），分别设置 token 配额，再从每桶抽取文档。文档是抽样单位，token 是预算单位。只按文档数随机打乱时，大量短网页可能挤掉书和长文档。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Sampling
  - Long Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "Gopher: Scaling Language Models"
    url: https://arxiv.org/abs/2112.11446
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
---

按 token 数划分长度桶（2k / 8k / 32k），每桶单独设置配额。抽取时以文档为单位，预算按 token 计算。全库只做 `shuffle` 时，大量短网页可能占据多数文档名额，长上下文材料和书被抽得太少。`dt-temp-mix-code` 按语言 / 域切；长度是另一轴：短模板、中等网页、书、长对话。

AFM 的长上下文放在 continued PT，不是预训练早期用短页硬撑到 32k。

## 桶的边界先写死

```python
from collections import defaultdict

EDGES = [0, 512, 2048, 8192, 32768, 10**9]
BUCKETS = ["xs", "s", "m", "l", "xl"]


def length_bucket(n_tokens):
    for name, lo, hi in zip(BUCKETS, EDGES, EDGES[1:]):
        if lo <= n_tokens < hi:
            return name
    return BUCKETS[-1]


def sample_by_length(docs, token_quota, rng):
    """token_quota: bucket -> 目标 token 数。docs 需有 n_tokens 属性。

    返回 (抽中的文档, 空桶列表)。每桶抽到 token 数达到配额为止，
    最后一篇可能略超配额；桶里文档不够时整桶全取。
    """
    pools = defaultdict(list)
    for doc in docs:
        pools[length_bucket(doc.n_tokens)].append(doc)
    picked = []
    empty_buckets = []
    for bucket_name, need in token_quota.items():
        pool = list(pools.get(bucket_name, []))
        if not pool:
            # 空桶必须报出来，不能悄悄少抽
            empty_buckets.append(bucket_name)
            continue
        rng.shuffle(pool)
        used = 0
        for doc in pool:
            if used >= need:
                break
            picked.append(doc)
            used += doc.n_tokens
    return picked, empty_buckets
```

### 可执行测试

```python
import random
from dataclasses import dataclass


@dataclass
class Doc:
    doc_id: str
    n_tokens: int


# 边界左闭右开：2047 在 s 桶，2048 在 m 桶
assert length_bucket(100) == "xs"
assert length_bucket(2047) == "s"
assert length_bucket(2048) == "m"
assert length_bucket(10**10) == "xl"

# 按 token 配额而非条数：1 本书就能填满 l 桶的配额，网页不会挤占它
docs = [Doc(f"web-{i}", 100) for i in range(50)] + [Doc("book", 10_000)]
picked, empty = sample_by_length(docs, {"xs": 1000, "l": 10_000, "xl": 50_000}, random.Random(0))
assert sum(d.n_tokens for d in picked if d.doc_id.startswith("web")) == 1000
assert [d.doc_id for d in picked if d.n_tokens == 10_000] == ["book"]

# 设置了配额但没有对应文档的桶，作为空桶返回
assert empty == ["xl"]

# 同一个种子结果可复现，且不会打乱调用方的列表
before = [d.doc_id for d in docs]
again, _ = sample_by_length(docs, {"xs": 1000, "l": 10_000, "xl": 50_000}, random.Random(0))
assert again == picked
assert [d.doc_id for d in docs] == before
```

空桶要明确报告。设置了 32k 配额，语料却没有对应文档时，是否合成或拼接需要另作决定，见 `dt-longctx-data`。如果这里悄悄少抽，后面可能用短文档补齐，表面占用率很高，实际长度配比却变了。

按条 shuffle 的常见误区是：10 条 100-token 网页对上 1 条 10k 的书，条数上网页赢。token 配额把这件事翻过来。

## 和 pack 的顺序

先抽（域 × 语言 × 长度），再 `dt-pretrain-pack-code`。pack 之后再按长度补齐，会破坏配额。超长文档切块时，块继承原文档的域和污染标记，不要切完当新文档重新哈希进 train/holdout。

短桶质量往往更差（菜单、标签云）。短桶的质量阈值可以更严，见 `dt-quality-filter-code`。

## 追问

- **长桶是不是越多越好？** 不是。全是书，指令跟随和短答会掉，见 `dt-neg-transfer`。长上下文能力用专门的针和文档 QA 评，不要用短题平均分代替。
- **对话 round 很长怎么计？** 按整段 token，不要按轮数。工具返回算进长度，损失（loss） 仍 mask，见 `dt-packed-sft-code`。
- **边界 2048 和 2049？** 边界附近软一点（少量随机进邻桶），避免门槛两侧被当成两种数据。
