---
id: dt-clip-filter-code
section: tech-screen
order: 27
level: A
title: CoderPad：图文对 CLIP 分怎么滤，合成 caption 要不要同一阈值？
quick: "图像和文本各自编码成向量，用余弦相似度衡量图文是否匹配，再按语言和来源分桶取分位数阈值。合成 caption 要和网页 alt-text 分开设阈值，因为它的 CLIP 分会向教师模型的分布靠拢而虚高。CLIP 分也不检查重复和安全，这些要用各自的检查器，误删要靠下游对照来验证。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Multimodal
  - CLIP
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Learning Transferable Visual Models From Natural Language Supervision
    url: https://arxiv.org/abs/2103.00020
    type: primary
  - title: "DataComp: In search of the next generation of multimodal datasets"
    url: https://arxiv.org/abs/2304.14108
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这题要写的是图文对过滤：图像和文本各自编码成向量，算余弦相似度，作为图文是否匹配的分数，再按语言和来源分桶，每桶取保留分位数作为阈值。合成 caption 要单独设阈值，因为它的分数会偏高。面试时讲清输入、筛选条件和输出就够了。

公开的参照是 DataComp 和 LAION 的 CLIP score 过滤。合成 caption 在实际数据里占比不小，AFM 2025 报告写了去重后超过 100 亿图文对，其中合成 caption 超过 50 亿对。

## 计算余弦，再按语言和来源筛选

`clip_score` 先做 L2 归一化，所以分数只看方向、与向量长度无关；维度不一致直接报错。`keep_pair` 先查 caption 长度，再查分数，并返回拒绝原因。`thresholds_by_quantile` 对每个桶单独排序，取第 `keep_frac` 位置的分数当阈值，小桶至少保留一条。

```python
import math
from collections import defaultdict


def l2_norm(vector):
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def clip_score(image_vec, text_vec):
    """图像向量和文本向量的余弦相似度。"""
    if len(image_vec) != len(text_vec):
        raise ValueError("image and text embeddings must have the same dimension")
    a = l2_norm(image_vec)
    b = l2_norm(text_vec)
    return sum(x * y for x, y in zip(a, b))


def keep_pair(score, threshold, caption_tokens, min_tokens=2, max_tokens=80):
    """返回 (是否保留, 原因)。先查 caption 长度，再查 CLIP 分。"""
    if caption_tokens < min_tokens or caption_tokens > max_tokens:
        return False, "caption_len"
    if score < threshold:
        return False, "clip"
    return True, "ok"


def thresholds_by_quantile(rows, keep_frac=0.3):
    """rows: list[(bucket, score)]。返回 bucket -> 阈值，每桶保留分数最高的 keep_frac。"""
    if not 0 < keep_frac <= 1:
        raise ValueError("keep_frac must be in (0, 1]")
    scores_by_bucket = defaultdict(list)
    for bucket, score in rows:
        scores_by_bucket[bucket].append(score)
    thresholds = {}
    for bucket, scores in scores_by_bucket.items():
        scores.sort(reverse=True)
        k = max(1, int(len(scores) * keep_frac))
        thresholds[bucket] = scores[k - 1]
    return thresholds
```

### 可执行测试

```python
# 方向相同的向量余弦为 1，正交为 0，与长度无关
assert math.isclose(clip_score([1.0, 0.0], [3.0, 0.0]), 1.0)
assert math.isclose(clip_score([1.0, 0.0], [0.0, 2.0]), 0.0)

# 维度不一致是调用错误
try:
    clip_score([1.0], [1.0, 0.0])
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# caption 太短或太长先拒绝，再看分数
assert keep_pair(0.9, 0.3, caption_tokens=1) == (False, "caption_len")
assert keep_pair(0.2, 0.3, caption_tokens=10) == (False, "clip")
assert keep_pair(0.35, 0.3, caption_tokens=10) == (True, "ok")

# 每桶单独取分位数：合成桶整体分高，阈值也更高
rows = [("web_en", s) for s in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)]
rows += [("synth_en", s) for s in (0.80, 0.85, 0.90, 0.95)]
thresholds = thresholds_by_quantile(rows, keep_frac=0.3)
assert thresholds["web_en"] == 0.8
assert thresholds["synth_en"] == 0.95

# 小桶至少保留一条
assert thresholds_by_quantile([("tiny", 0.4)], keep_frac=0.3) == {"tiny": 0.4}
```

`bucket` 先按语言分，再按来源分（网页 alt、OCR、合成）。用分位数是因为 CLIP 分的绝对值随模型和数据分布变化。LAION-2B 公开用过 B/32 约 0.28 的硬阈值，DataComp 更好的基线是 L/14 分数前 30%。0.28 只对那个模型和那批数据有意义，现场讲分位数做法就行。

## 合成 caption 为什么会虚高

用强模型给图写 caption，再拿 CLIP 打分，分数会靠近教师自己的分布。如果把网页 alt-text 的 0.3 分位数阈值直接套到合成桶，合成数据几乎全部保留。所以合成桶要单独检查：人工抽查、与独立 captioner 的一致性，以及 caption 里有没有评测题面（图文泄漏）。多模态合成管线见 `dt-synth-tool-mm`、`dt-multimodal-data`。

非英语也要单独处理。CLIP 偏向英语，低资源语言要用该语言自己的分位数，或者先过 `dt-lid-code` 再筛。机翻的 caption 要记录来源。

## CLIP 分管不到的东西

过小的图片、纯单色图片、只有文件名的 caption（比如 `DSC0001.jpg`），以及色情和 CSAM，都要独立检查。CLIP 分不能替代安全检查。

## 追问

- **只留高分，会不会只剩英文库存图？** 会，所以要按语言配额，每个语言桶各自取分位数。
- **近重复的图怎么办？** CLIP 分不管复制图。图像侧用 pHash 或 embedding 去重，文本侧用 SimHash，见 `dt-simhash-code`。
- **扫阈值时看什么指标？** 看小模型的检索召回和 zero-shot 分类，再人工看被误杀的图表、截图和 UI 图。只报平均 CLIP 分等于没有对照。
