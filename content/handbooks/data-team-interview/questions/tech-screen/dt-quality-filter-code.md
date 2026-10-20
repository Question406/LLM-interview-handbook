---
id: dt-quality-filter-code
section: tech-screen
order: 3
level: A
title: CoderPad：质量过滤怎么写，启发式和模型分怎么叠？
quick: "先做便宜的语言、长度、PII 和重复字符检查，再用按语言校准的质量模型评分，最后按阈值和配额选择。全局 top-$k$ 容易丢掉低资源语言。AFM 2025 的公开经验是过强启发式会误删有价值的数据，因此要检查误杀，并分别校准语言阈值。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Data Quality
  - Filtering
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Textbooks Are All You Need
    url: https://arxiv.org/abs/2306.11644
    type: primary
---

过滤分三步：先做成本低的确定性检查，再用按语言校准的质量模型评分，最后结合阈值与配额选择。堆 20 条正则然后 `if any(bad): drop`，可能误删有用数据；只依赖模型分，也需要检查校准和误杀。

AFM 2025：过猛启发式会扔掉高价值 文本处理单位（token），所以减弱规则、加入按语言调过的模型过滤。FineWeb-Edu / Phi 同构：分类器给「教育价值」或「教科书味」，再按分抽样，而不是只留 Common Crawl 的头域。

## 两层门，一层配额

现场我把过滤写成三步，每步可关：

1. 硬门。空文档、语言识别失败、PII 正则（信用卡、身份证号）、极端重复字符。过不了的进 quarantine，留 lineage，方便审计误杀。
2. 模型分。一个小分类器打 0 到 1。阈值按语言、按域分开。英语 0.6 和某低资源语言 0.6 的通过率可以差很多。
3. 配额。每个域先保证最低 token，再在域内按分加权。避免「全世界只剩英语维基」。

```python
import re
from dataclasses import dataclass

CARD_LIKE = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")  # 粗信用卡，生产用专用检测器
REPEATED_CHAR = re.compile(r"(.)\1{20,}")


@dataclass
class FilterDecision:
    keep: bool
    reason: str
    quality: float


def hard_gate(text, lang, allowed_langs=("en", "zh", "es", "ja"), min_chars=200):
    """便宜的确定性检查。过不了的文档带原因返回，交给 quarantine。"""
    if len(text) < min_chars:
        return FilterDecision(False, "too_short", 0.0)
    if lang not in allowed_langs:
        return FilterDecision(False, "lang", 0.0)
    if CARD_LIKE.search(text):
        return FilterDecision(False, "pii", 0.0)
    if REPEATED_CHAR.search(text):
        return FilterDecision(False, "boilerplate", 0.0)
    return FilterDecision(True, "hard_ok", 0.0)


def filter_doc(text, lang, score_fn, thresholds, rng_u=0.0, band=0.1):
    """score_fn(text, lang) -> [0, 1]；thresholds[lang] 是该语言的保留阈值。

    软门：q >= t 必留；q < t - band 必扔；中间按线性概率留，rng_u ~ U(0, 1)。
    """
    hard = hard_gate(text, lang)
    if not hard.keep:
        return hard
    q = float(score_fn(text, lang))
    t = thresholds.get(lang, 0.5)
    if q >= t:
        return FilterDecision(True, "model_keep", q)
    if q < t - band:
        return FilterDecision(False, "model_drop", q)
    keep = rng_u < (q - (t - band)) / band
    return FilterDecision(keep, "model_band", q)
```

### 可执行测试

```python
good_text = "A clear explanation of photosynthesis in plants and algae. " * 5


def fixed_score(value):
    """测试桩：总是返回固定分数的质量模型。"""
    return lambda text, lang: value


# 硬门：太短、语言不在白名单、疑似卡号、长串重复字符
assert hard_gate("short", "en").reason == "too_short"
assert hard_gate(good_text, "xx").reason == "lang"
assert hard_gate(good_text + " card 4111 1111 1111 1111", "en").reason == "pii"
assert hard_gate(good_text + "!" * 30, "en").reason == "boilerplate"
assert hard_gate(good_text, "en").keep

# 硬门失败时不调用模型
assert filter_doc("short", "en", fixed_score(1.0), {}).reason == "too_short"

# 模型分高于阈值必留，远低于阈值必扔
decision = filter_doc(good_text, "en", fixed_score(0.7), {"en": 0.6})
assert decision == FilterDecision(True, "model_keep", 0.7)
assert filter_doc(good_text, "en", fixed_score(0.4), {"en": 0.6}).reason == "model_drop"

# 阈值附近按概率保留：q=0.55、t=0.6 时保留概率约 0.5
assert filter_doc(good_text, "en", fixed_score(0.55), {"en": 0.6}, rng_u=0.2).keep
assert not filter_doc(good_text, "en", fixed_score(0.55), {"en": 0.6}, rng_u=0.8).keep

# 不同语言用各自阈值：同样 0.45 分，zh 阈值 0.4 时保留，en 阈值 0.6 时扔掉
thresholds = {"en": 0.6, "zh": 0.4}
assert filter_doc(good_text, "zh", fixed_score(0.45), thresholds).keep
assert not filter_doc(good_text, "en", fixed_score(0.45), thresholds).keep
```

`score_fn` 在 CoderPad 里可以是假分类器或线性特征（停用词比、平均词长、符号比）。口播补一句：生产是蒸馏过的小编码器，离线打分，热路径不跑 70B。

## 口播要对上的失败模式

启发式误杀。代码、公式、对话记录的「停用词比」很低，会被「像自然语言」规则扔掉。这就是 AFM 说的 over-aggressive heuristics。代码 / 数学走单独桶，不用通用网页门。

模型分偏置。分类器在英语教科书上训，会把非英语、非正式但有用的论坛答疑打低。按语言标数据，按语言报通过率和下游 $\Delta$。

PII。公开网页上也有社保号和卡号。Apple 支持页写了会滤这类标识，并避开大规模汇聚个人信息的站。正则是第一刀，不是最后一刀。

阈值扫描。留 5% / 15% / 40% 三档，用小模型看知识 / 推理切片。只报「我们滤得很狠」没有对照。

和 mix 的接口：过滤输出是带 `quality` 和 `reason` 的文档，`dt-pipeline-talk` 的配额采样吃这两个字段。reason 进 dataset card，下周改阈值才能归因。

## 追问

- **质量模型用 LLM-as-judge 行吗？** 可以标种子，不要在 10B 文档上同步打。蒸馏成小模型，定期用新人工集校准。
- **「教科书味」会不会滤掉工具轨迹？** 会。监督微调（SFT） / 工具数据不用预训练网页分类器。分组统计，分门。
- **软阈值为什么比硬切好？** 硬切在分值校正漂一点时，通过率能跳一截。软阈值能通过实验调整，也避免仅因 0.599 和 0.601 的微小差别就完全改变保留结果。
