---
id: dt-clip-filter-code
section: tech-screen
order: 27
level: A
title: CoderPad：image-text pairs CLIP 分怎么滤，合成 caption 要不要同一阈值？
quick: >-
  图像和文本各自编码成向量，用余弦相似度当图文匹配分，再按语言和来源分桶，每桶取分位数当阈值。合成 caption 的 CLIP 分会向 teacher
  model 的分布靠拢而虚高，所以要和网页 alt-text 分开设阈值。重复和安全 CLIP 分管不到，要用各自的 checker，误删靠下游对照来验证。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Learning Transferable Visual Models From Natural Language Supervision
    url: 'https://arxiv.org/abs/2103.00020'
    type: primary
  - title: 'DataComp: In search of the next generation of multimodal datasets'
    url: 'https://arxiv.org/abs/2304.14108'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

为图文配对实现向量匹配打分、单对过滤及按桶确定保留阈值的接口。图像与文本向量已经给出，不需要加载 CLIP 模型。

### 输入与接口

- `clip_score(image_vec, text_vec)` 接受两个同维实数向量，返回余弦分数；零向量按本题约定返回 0 分。
- `keep_pair(score, threshold, caption_tokens, min_tokens=2, max_tokens=80)` 接受分数、threshold 和 caption 的 token 数。
- `thresholds_by_quantile(rows, keep_frac=0.3)` 接受 `(bucket, score)` 列表和 `(0,1]` 的保留比例。

### 输出与约束

`keep_pair` 返回 `(是否保留, 原因)`，原因依次可能为 `caption_len`、`clip`、`ok`。`thresholds_by_quantile` 返回 `bucket -> 分数阈值` 的字典。

caption token 数必须位于闭区间 `[min_tokens,max_tokens]`；长度合法后，分数达到阈值即保留。每个桶分别确定 threshold：包含 m 个分数时取分数由高到低的第 `max(1,int(m*keep_frac))` 名；与 threshold 同分的样本均可通过，实际保留数可能略多。

### 示例

```text
clip_score([1,0],[3,0]) -> 1.0
keep_pair(0.35,0.3,10) -> (True,"ok")
keep_pair(0.9,0.3,1) -> (False,"caption_len")
thresholds_by_quantile([("web",0.1),("web",0.8),("web",0.9)],0.5) -> {"web":0.9}
```

## 解题思路与参考答案

我会算图像向量和文本向量的余弦相似度当匹配分，按语言和来源分桶，每桶取保留分位数当阈值。合成 caption 单独一个桶，因为它的分数天然偏高。

举个例子，一张猫的照片配网页 alt-text「DSC0001.jpg」，分数会很低，该扔；同一张图配强模型写的「一只橘猫趴在窗台上晒太阳」，分数很高。如果网页桶和合成桶用同一个阈值，synthetic data 几乎全部保留。公开的参照是 DataComp 和 LAION 的 CLIP score 过滤，合成 caption 在实际数据里占比也不小：AFM 2025 报告写了 deduplication 后超过 100 亿 image-text pairs，其中合成 caption 超过 50 亿对。

## 余弦打分和分桶阈值

`clip_score` 先做 L2 normalization，分数只看方向，和向量长度无关，维度不一致直接报错。`keep_pair` 先查 caption 长度，再查分数，返回拒绝原因。`thresholds_by_quantile` 对每个桶单独排序，取第 `keep_frac` 位置的分数当阈值，小桶至少保留一条。

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

测试里能看到合成桶整体分高，阈值也跟着高：

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

`bucket` 先按语言分，再按来源分（网页 alt、OCR、合成）。用分位数是因为 CLIP 分的绝对值随模型和数据分布变化：LAION-2B 公开用过 B/32 约 0.28 的硬阈值，DataComp 更好的 baseline 是 L/14 分数前 30%，0.28 只对那个模型和那批数据有意义，现场讲分位数做法就行。打分是每对一次点积，分位数是每桶一次排序。

## 合成 caption 和非英语

用强模型给图写 caption，再拿 CLIP 打分，分数会靠近 teacher 自己的分布，把网页 alt-text 的 0.3 分位数阈值直接套过去，synthetic data 几乎全留下来。所以合成桶要另外检查：人工抽查、和独立 captioner 的一致性，还有 caption 里有没有评测题面（图文 leakage）。multimodal 合成 pipeline 在 `dt-synth-tool-mm`、`dt-multimodal-data` 里讲。

非英语也要单独处理。CLIP 偏向英语，low-resource 语言用该语言自己的分位数，或者先过 `dt-lid-code` 再筛，机翻的 caption 要记录来源。还有一些东西 CLIP 分完全管不到：过小的图片、纯单色图片、只有文件名的 caption，以及色情和 CSAM，这些都要独立检查，安全检查不能拿 CLIP 分代替。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert math.isclose(clip_score([1.0, 0.0], [3.0, 0.0]), 1.0)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条 assertion 都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**只留高分，会不会只剩英文库存图？**
会，所以要按语言配额，每个语言桶各自取分位数。

**near-duplicates 的图怎么办？**
CLIP 分不管复制图。图像侧用 pHash 或 embedding deduplication，文本侧用 SimHash，见 `dt-simhash-code`。

**扫阈值时看什么指标？**
看 small model 的检索召回和 zero-shot 分类，再人工看被 false rejection 的图表、截图和 UI 图。只报平均 CLIP 分等于没有对照。

**合成桶除了阈值更高，还要查什么？**
人工抽查、和独立 captioner 对一致性，再查 caption 里有没有评测题面，防图文 leakage。

相关：`dt-synth-tool-mm`、`dt-multimodal-data`、`dt-lid-code`、`dt-simhash-code`
