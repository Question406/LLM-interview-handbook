---
id: dt-clip-filter-code
section: tech-screen
order: 27
level: A
title: CoderPad：图文对 CLIP 分怎么滤，合成 caption 要不要同一阈值？
quick: "图像和文本分别生成向量，用余弦衡量匹配程度，按语言与来源校准阈值。网页 alt-text 和合成 caption 分开处理，后者分数可能虚高。CLIP 不检查重复或安全，还需要对应检查器，并用下游对照验证误删。"
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

先把图像和文本转成向量，计算余弦相似度，再按语言和来源确定阈值或保留分位数。合成 caption 的 CLIP 分可能偏高，应与网页 alt-text 分开校准。面试重点是说明输入、筛选条件和输出，不要推测内部阈值。

DataComp / LAION 的 CLIP score 是公开锚点。AFM 公开写了去重后超 100 亿图文对、合成 caption 超 50 亿对。

## 计算余弦，再按语言和来源筛选

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

`bucket` 先按语言，再按来源（网页 alt / OCR / 合成）。LAION-2B 公开用过 B/32 约 0.28 的硬阈值；DataComp 更好的基线是 L/14 头 30%。现场口播分位数，不要背 0.28 当苹果的数。

还需独立检查过小图片、纯单色图片、仅含文件名 `DSC0001.jpg` 的 caption，以及色情 / CSAM。CLIP 分不能替代安全检查。

## 合成 caption 虚高

用强模型给图写 caption，再拿 CLIP 打分，分数会靠近教师自己的分布。网页 alt-text 的 0.3 分位数套过去，合成几乎全留。合成桶：人工抽查、和独立 captioner 的一致性、以及是否含评测题面（图文泄漏）。多模态合成管线见 `dt-synth-tool-mm`、`dt-multimodal-data`。

非英语：CLIP 偏英语。低资源语言用该语言分位数，或先过 `dt-lid-code` 再滤。机翻 caption 要记来源。

## 追问

- **只留高分会不会只剩英文库存图？** 会。所以按语言配额，不要全局 top 30%。
- **图近重复？** CLIP 分不管复制图。图像侧 pHash / embedding 去重，文本侧 SimHash，见 `dt-simhash-code`。
- **阈值扫什么指标？** 小模型的检索召回和分类 zero-shot，外加人工看误杀的图表、截图、UI。只报平均 CLIP 分没有对照。
