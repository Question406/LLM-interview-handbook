---
id: dt-temp-mix-code
section: tech-screen
order: 7
level: A
title: CoderPad：域配额加温度采样怎么写，低资源语言怎么避免过拟合？
quick: "先按能力分配 token 预算，再用 $p_i\\propto n_i^{\\alpha}$ 平衡组内来源：$\\alpha=1$ 按体积，趋近 0 时更均匀。低资源数据重复过多会过拟合，要配合课程与英语锚点。实际数据不足或为空时必须报告。"
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
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
  - title: "Gopher: Scaling Language Models"
    url: https://arxiv.org/abs/2112.11446
    type: primary
---

采样分两层：先按能力需求给各分组 token 配额，再在组内用 $p_i\propto n_i^{\alpha}$ 调整采样。$\alpha=1$ 按原始体积抽，$\alpha\to 0$ 趋向均匀。配额对应的组为空时要报告，不能静默少抽。`dt-pipeline-talk` 写过按配额抽文档。语言 40 个、体积差 100 倍，别 `concat` 再 shuffle，也不能默认每种语言各占 $1/L$，导致英语预算不足。

AFM 2025：文本 continued PT 把多语总权重从 8% 提到 30%，桶内对语言做温度采样，平衡低资源欠拟合和过拟合。课程比一上来 30% 更能护住英语。

## 两层：桶间配额，桶内温度

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

### 可执行测试

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

$\alpha$ 现场给一个数并解释：0.3 到 0.5 常见，抬长尾；低资源文档少，再低的 $\alpha$ 会把那 200 篇书读到过拟合。AFM 的处理是温度采样加上课程：先不要把 30% 打满。

英语锚点不在这个函数里。多语抬权时，外面还要留英语高质桶，否则可能产生负迁移，见 `dt-neg-transfer`。

## 规模怎么报

语言数多时不要 `choices` 循环。预计算每个语言的累计 token，用水库抽样或按分片加权。CoderPad 写清合同即可。空语言打印出来：配额表和真实 pool 对不上，是数据事故，不是采样噪声。

## 追问

- **$\alpha$ 和配额谁先定？** 先定桶间配额（能力预算），再定桶内 $\alpha$（该桶内部的长尾）。两个旋钮一次只转一个。
- **机翻算该语言吗？** AFM 在 mid 用过验证过的机翻。要单独记来源，评测用母语者题，见 `dt-locale-data`。
- **为什么不用 Data Mixing Law 直接求 $r$？** 定律拟合的是预训练域损失，监督微调（SFT） / 多语人评不能直接套。小规模 sweep 仍要做，见 `dt-data-mix-quota`。
