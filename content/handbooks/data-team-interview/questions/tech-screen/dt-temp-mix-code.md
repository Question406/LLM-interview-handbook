---
id: dt-temp-mix-code
section: tech-screen
order: 7
level: A
title: CoderPad：域配额加 temperature sampling 怎么写，low-resource 语言怎么避免 overfitting？
quick: >-
  sampling 分两层：先按能力需求给各分组分配 token 预算，再在组内用 $p_i\propto n_i^{\alpha}$
  平衡来源，$\alpha=1$ 是按体积抽，趋近 0 时更均匀。low-resource 数据重复太多会出现 overfitting，所以要配合课程和
  English regression data。实际数据不足或某组为空时必须报告。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Data Mix
  - Multilingual
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Data Mixing Laws
    url: 'https://arxiv.org/abs/2403.16952'
    type: primary
  - title: 'Gopher: Scaling Language Models'
    url: 'https://arxiv.org/abs/2112.11446'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

按语言 token 配额从不同语言的文档池中 sampling，并用温度指数调整文档长度带来的 sampling 偏好。

### 输入与接口

实现 `temperature_weights`(counts,alpha) 与 `sample_mix`(`docs_by_lang`,`token_budget`,`lang_quota`,alpha=0.5,rng=None)。counts 为语言到正 token 数的有序映射；alpha 为非负数。文档含唯一 `doc_id` 和正整数 `n_tokens`；`docs_by_lang` 为语言到文档列表的映射；`lang_quota` 是非负份额且总和为1；`token_budget` 为非负整数。

### 输出与约束

weights 返回 (语言列表,概率列表)，语言顺序与 counts 一致，概率与 `count^alpha` 成正比。`sample_mix` 返回 (picked,`empty_langs`)，picked 包含选中文档原对象，`empty_langs` 列出配额语言中没有文档的语言；按 `lang_quota` 的语言顺序分组处理。不得修改输入池。

每语言目标为 int(`token_budget` × quota)。该语言内部无放回 sampling，单篇概率权重为 `max(n_tokens,1)^alpha`，累计 token 达到目标即停，最后一篇允许超额；池不足则全部用完。零目标不选文档。rng=None 使用固定 seed0；提供相同 rng 初始状态时结果可复现。

### 示例

```text
 temperature_weights({"en":100,"sw":1},0.5)
-> (["en","sw"],[10/11,1/11])
docs_by_lang={"en":[Doc("a",100)],"ja":[Doc("b",100)]}
token_budget=100，lang_quota={"en":0.5,"ja":0.5}
picked 的 doc_id -> ["a","b"]，empty_langs -> []
两种语言各需要50 token，整篇选入后总计200 token
```

## 解题思路与参考答案

我会分两层 sampling：先按能力需求给各语言分配 token 配额，再在语言内部用 $p_i\propto n_i^{\alpha}$ 调整，$\alpha=1$ 是按原始体积抽，$\alpha\to 0$ 趋向均匀。配额对应的组为空时要报出来，别静默少抽。

比如 40 种语言、体积相差 100 倍，直接 `concat` 再 shuffle，体积大的语言会吃掉预算；每种语言各占 $1/L$，英语预算又不够。公开参照是 AFM 2025，文本 continued PT 把 multilingual 的总权重从 8% 提到 30%，桶内对各语言做 temperature sampling，在 low-resource 语言的 underfitting 和 overfitting 之间找平衡；比起一上来就给 30%，配合课程更能护住英语。按配额抽文档的写法见 `dt-pipeline-talk`。

## 桶间配额，桶内温度

```python
import math
import random


def temperature_weights(counts, alpha):
    """counts: key -> token 数。返回 (keys, probs)，p_i ∝ n_i ** alpha。

    alpha=1 跟体积走，alpha=0 均匀。
    """
    keys = list(counts)
    raw = [counts[key] ** alpha for key in keys]
    total = sum(raw) or 1.0
    return keys, [x / total for x in raw]


def sample_mix(docs_by_lang, token_budget, lang_quota, alpha=0.5, rng=None):
    """lang_quota: lang -> 该语言占多语桶的目标份额，和为 1；token_budget 是多语桶的总 token。

    每种语言内按 n_tokens ** alpha 加权、无放回抽文档，直到达到该语言的 token 配额。
    返回 (抽中的文档, 没有文档的语言)。
    """
    if not math.isclose(sum(lang_quota.values()), 1.0, abs_tol=1e-6):
        raise ValueError("lang_quota shares must sum to 1")
    rng = rng or random.Random(0)
    picked = []
    empty_langs = []
    for lang, share in lang_quota.items():
        pool = docs_by_lang.get(lang, [])
        need = int(token_budget * share)
        if not pool:
            # 配额表和真实 pool 对不上是数据事故，要报出来
            empty_langs.append(lang)
            continue
        counts = {i: max(doc.n_tokens, 1) for i, doc in enumerate(pool)}
        keys, probs = temperature_weights(counts, alpha)
        used = 0
        seen = set()
        while used < need and len(seen) < len(pool):
            index = rng.choices(keys, weights=probs, k=1)[0]
            if index in seen:
                continue
            seen.add(index)
            picked.append(pool[index])
            used += pool[index].n_tokens
    return picked, empty_langs
```

测试覆盖三种 $\alpha$、各语言配额、空语言、无放回和配置错误：

```python
from dataclasses import dataclass


@dataclass
class Doc:
    doc_id: str
    n_tokens: int


# alpha=1 按体积，alpha=0 均匀，alpha=0.5 介于两者之间
keys, probs = temperature_weights({"en": 100, "sw": 1}, alpha=1.0)
assert keys == ["en", "sw"]
assert math.isclose(probs[0], 100 / 101)
assert temperature_weights({"en": 100, "sw": 1}, alpha=0.0)[1] == [0.5, 0.5]
assert math.isclose(temperature_weights({"en": 100, "sw": 1}, alpha=0.5)[1][1], 1 / 11)

# 每种语言抽到各自的 token 配额；空语言被报出来
docs_by_lang = {
    "en": [Doc(f"en-{i}", 100) for i in range(100)],
    "ja": [Doc(f"ja-{i}", 100) for i in range(100)],
}
picked, empty = sample_mix(docs_by_lang, 10_000, {"en": 0.7, "ja": 0.2, "sw": 0.1})
assert sum(d.n_tokens for d in picked if d.doc_id.startswith("en")) == 7000
assert sum(d.n_tokens for d in picked if d.doc_id.startswith("ja")) == 2000
assert empty == ["sw"]

# 无放回：同一文档不会被抽两次
assert len({d.doc_id for d in picked}) == len(picked)

# 份额之和不为 1 是配置错误
try:
    sample_mix(docs_by_lang, 10_000, {"en": 0.7, "ja": 0.7})
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

$\alpha$ 我会给 0.3 到 0.5，这个范围比较常见，作用是抬高 long-tail。但 low-resource 语言文档本来就少，$\alpha$ 再低，就会把那 200 篇书反复读到 overfitting，所以 temperature sampling 要配合课程使用。English regression data 不在这个函数里，给 multilingual 加权时，外面还要保留一个英语高质量桶，不然可能出现 negative transfer，见 `dt-neg-transfer`。

语言数多时，预计算每种语言的累计 token，用水库 sampling 或者按分片加权，`choices` 循环扛不住。CoderPad 上把输入输出约定写清楚就行。空语言要打印出来，配额表和真实 pool 对不上，要当数据事故处理。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert keys == ["en", "sw"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**$\alpha$ 和配额谁先定？**
先定桶间配额（能力预算），再定桶内 $\alpha$（桶内部的 long-tail）。两个旋钮一次只调一个。

**机翻文本算该语言吗？**
验证过的机翻可以用，AFM 2025 报告在 mid 阶段就用过。来源要单独记录，评测用母语者写的题，见 `dt-locale-data`。

**为什么不用 Data Mixing Law 直接求 data mix $r$？**
这个定律拟合的是 pre-training 的域损失，SFT 和 multilingual human evaluation 不能直接套用，小规模 sweep 仍然要做，见 `dt-data-mix-quota`。

**$\alpha$ 越小越好吗？**
不是。low-resource 语言文档少，$\alpha$ 太低会把同一批书反复读到 overfitting，要配合课程和 English regression data。

相关：`dt-pipeline-talk`、`dt-neg-transfer`、`dt-locale-data`、`dt-data-mix-quota`
