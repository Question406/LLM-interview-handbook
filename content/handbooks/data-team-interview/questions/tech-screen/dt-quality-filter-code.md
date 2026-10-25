---
id: dt-quality-filter-code
section: tech-screen
order: 3
level: A
title: CoderPad：质量过滤怎么写，启发式和模型分怎么叠？
quick: "过滤分三步：先做便宜的语言、长度、PII 和重复字符检查，再用按语言校准的质量模型打分，最后按阈值和配额选。全局取 top-$k$ 容易把低资源语言整个丢掉。AFM 2025 公开的经验是过强的启发式会误删有价值的数据，所以要查误杀，并按语言分别校准阈值。"
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

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

实现训练文档质量过滤接口，先执行确定性规则，再依据语言对应的模型阈值作保留决定。每次决定都需要返回原因，便于统计失败来源。

### 输入与接口

- `hard_gate(text,lang,allowed_langs=("en","zh","es","ja"),min_chars=200)` 返回 `FilterDecision(keep,reason,quality)`。
- `filter_doc(text,lang,score_fn,thresholds,rng_u=0.0,band=0.1)` 接受模型打分回调 `score_fn(text,lang)`、语言阈值字典、给定的 `[0,1)` 随机数和正宽度 band。

### 输出与约束

硬规则按顺序拒绝：字符数不足为 `too_short`；语言不在白名单为 lang；含卡号形状正则 `\b\d(?:[ -]?\d){12,18}\b` 的匹配为 pii（仅形状检测，不做 Luhn）；同一字符连续出现至少 21 次为 boilerplate；通过为 `hard_ok`，quality 均为 0。

硬规则拒绝时不调用模型。模型分 q 至少为语言阈值 t 时必留，原因 `model_keep`；q 小于 t-band 时必丢，原因 `model_drop`；中间以 `(q-(t-band))/band` 为保留概率，判断 `rng_u` 是否严格小于该值，原因 `model_band`。缺少语言阈值时 t=0.5，模型路径返回的 quality 为 q。

### 示例

```text
hard_gate("short","en") -> FilterDecision(False,"too_short",0.0)
text="A clear explanation of photosynthesis in plants and algae. " 重复5次
score_fn 恒返回0.55，thresholds={"en":0.6}，band=0.1
filter_doc(text,"en",score_fn,thresholds,rng_u=0.2).keep -> True
同一输入 rng_u=0.8 时 keep -> False
```

## 解题思路与参考答案

我会把过滤写成三步，每一步都能单独关掉：先做成本低的确定性检查，再用按语言校准的质量模型打分，最后结合阈值和配额来选。

这样分是因为堆 20 条正则再 `if any(bad): drop`，很可能误删有用数据，比如一段代码的停用词比很低，就会被「像自然语言」的规则扔掉。只靠模型分也不保险，要查校准和误杀。AFM 2025 写到过猛的启发式会扔掉高价值的 token，所以他们减弱了规则，加入按语言调过的模型过滤。FineWeb-Edu 和 Phi 的思路相同，分类器给出「教育价值」或「教科书味」的分数再按分抽样，看的是文本内容本身，Common Crawl 的头部域名之外也能选出好数据。

## 两层门，一层配额

硬门查空文档、语言识别失败、PII 正则（信用卡、身份证号）、极端重复字符，没过的进 quarantine 并留 lineage，方便审计误杀。模型分是一个小分类器打 0 到 1 的分，阈值按语言、按域分开，英语的 0.6 和某个低资源语言的 0.6，通过率可能差很多。配额是每个域先保证最低 token 数，再在域内按分加权，免得「全世界只剩英语维基」。阈值附近我用一个软门，分数在阈值下方一个 band 内按线性概率保留。

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

测试覆盖四种硬门、硬门短路、必留必扔、软门概率和按语言阈值：

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

`score_fn` 在 CoderPad 里可以是假分类器，或者几个线性特征（停用词比、平均词长、符号比）。要补一句：生产上用的是蒸馏过的小编码器，离线打分，热路径上不会跑 70B。过滤的输出是带 `quality` 和 `reason` 字段的文档，`dt-pipeline-talk` 里的配额采样就吃这两个字段；`reason` 要写进 dataset card，下周改阈值时才能归因。

## 会错在哪

启发式会误杀：代码、公式、对话记录的停用词比很低，会被「像自然语言」的规则扔掉，这就是上面说的 over-aggressive heuristics，所以代码和数学走单独的桶，不用通用网页门。模型分有偏置：在英语教科书上训的分类器，会把非英语、非正式但有用的论坛答疑打低分，所以要按语言标数据，按语言报通过率和下游 $\Delta$。PII 方面，公开网页上也有社保号和卡号，正则只是第一刀，命中后还要校验。

阈值要扫一下，保留 5% / 15% / 40% 三档，用小模型看知识和推理切片的变化。只报「我们滤得很狠」，等于没有对照。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert hard_gate("short", "en").reason == "too_short"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**质量模型能用 LLM-as-judge 吗？**
可以用来标种子数据，但别在 10B 文档上同步打分。蒸馏成小模型，定期用新的人工集校准。

**「教科书味」会不会把工具轨迹滤掉？**
会。SFT 和工具数据不用预训练的网页分类器，分组统计、分开设门。

**软阈值为什么比硬切好？**
硬切时分值校准稍微漂一点，通过率就会跳一截。软阈值可以通过实验调整，也不会因为 0.599 和 0.601 这种微小差别就完全改变去留。

**为什么不全局取 top-$k$？**
低资源语言的分数整体偏低，全局一刀容易整个丢掉。阈值按语言分开，配额再给每个域保底。

相关：`dt-pipeline-talk`
