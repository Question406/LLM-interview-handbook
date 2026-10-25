---
id: dt-length-bucket-code
section: tech-screen
order: 28
level: A
title: CoderPad：按长度分层抽样怎么写，短模板淹没长文档怎么避免？
quick: "按 token 数把文档分进长度桶（2k / 8k / 32k），每桶单独设 token 配额，再从桶里按文档抽。文档是抽样单位，token 是预算单位。只按文档数随机打乱的话，海量短网页会占满名额，书和长文档被抽得太少。"
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

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

按文档长度进行分桶抽样，使短网页和长文档分别使用自己的 token 配额，不能让一个桶悄悄占用另一个桶的配额。

### 输入与接口

- `length_bucket(n_tokens)` 接受非负文档长度。
- `sample_by_length(docs,token_quota,rng)` 接受带 `n_tokens` 属性的文档列表、`桶名 -> 目标token数` 字典，以及支持 `shuffle` 的随机数生成器。
- 桶边界为 xs:[0,512)、s:[512,2048)、m:[2048,8192)、l:[8192,32768)、xl:[32768,正无穷)。

### 输出与约束

返回 `(picked,empty_buckets)`：picked 是抽中的原文档对象，`empty_buckets` 按配额字典的顺序报告没有任何文档的目标桶。只从配额中列出的桶抽样。

每个桶内无放回抽取，到 token 总数达到配额时停止，最后一篇允许超额；桶内不足配额时取完所有文档。不修改调用方 docs 的顺序，相同输入与相同 RNG 状态应得到相同结果。

### 示例

```text
length_bucket(2047) -> "s"；length_bucket(2048) -> "m"
docs=[Doc("web",100),Doc("book",10000)]
sample_by_length(docs,{"xs":50,"l":10000,"xl":1},Random(0))
-> ([web,book],["xl"])
```

## 解题思路与参考答案

我会按 token 数把文档分进长度桶（2k / 8k / 32k），每桶单独设 token 配额，抽的时候以文档为单位、预算按 token 计。全库只做 `shuffle` 的话，大量短网页会占掉多数名额，长上下文材料和书被抽得太少。

举个例子，10 条 100-token 的网页对 1 条 10k 的书，按条数算网页赢；按 token 配额算，结果正好反过来。`dt-temp-mix-code` 按语言和域切配比，长度是另一条轴：短模板、中等网页、书、长对话。

## 桶的边界先写死

边界左闭右开，每个桶洗牌后抽到 token 数够配额为止，最后一篇可能略超；桶里文档不够就整桶全取，没有文档的桶单独报出来。

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

测试覆盖边界、按 token 配额、空桶和可复现：

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

分桶一遍线性扫，每桶洗牌一次，整体 $O(N)$。空桶要明确报告：设了 32k 配额、语料里却没有对应文档时，要不要合成或拼接是另一个决定，见 `dt-longctx-data`。如果这里悄悄少抽，后面可能用短文档补齐，表面上占用率很高，实际的长度配比已经变了。

## 和 pack 的先后

先按域、语言、长度抽样，再做 `dt-pretrain-pack-code`。pack 之后再按长度补齐，会破坏配额。超长文档切块时，每块继承原文档的域和污染标记，别切完当新文档重新哈希进 train/holdout。短桶的质量往往更差，菜单、标签云多，所以短桶的质量阈值可以更严，见 `dt-quality-filter-code`。长上下文也不必在预训练早期就用短页硬撑到 32k，可以放到 continued PT 阶段再加，AFM 2025 报告就是这样安排的。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert length_bucket(100) == "xs"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**长桶是不是越多越好？**
不是。全是书的话，指令跟随和短答能力会掉，见 `dt-neg-transfer`。长上下文能力要用专门的针和文档 QA 来评，别拿短题平均分代替。

**很长的多轮对话怎么计？**
按整段的 token 数算，不按轮数。工具返回也算进长度，但 loss 仍然 mask 掉，见 `dt-packed-sft-code`。

**边界 2048 和 2049 差一个 token，就分进两个桶？**
边界附近可以软一点，让少量文档随机进相邻的桶，免得门槛两侧被当成两种数据。

**桶里文档不够配额怎么办？**
整桶全取，并且把它报出来。悄悄用短文档补齐，长度配比就变了。

相关：`dt-temp-mix-code`、`dt-longctx-data`、`dt-pretrain-pack-code`、`dt-quality-filter-code`、`dt-neg-transfer`、`dt-packed-sft-code`
