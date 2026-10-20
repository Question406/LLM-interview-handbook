---
id: dt-ppl-filter-code
section: tech-screen
order: 20
level: A
title: CoderPad：KenLM / 困惑度质量门怎么写，阈值按语言怎么切？
quick: "小语言模型的平均交叉熵和困惑度可作质量代理，但只反映文本是否像参考语料。按语言和数据域校准或选择分位数；代码、公式和论坛不能直接用维基阈值。合成数据仍要独立验证，并用下游对照判断筛选是否有效。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Quality
  - Perplexity
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data"
    url: https://arxiv.org/abs/1911.00359
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

用小语言模型计算文档 logprob，转换成平均每词或字符的交叉熵、困惑度（ppl），作为质量的间接信号。再按语言、数据域选择分位数，避免全局同一阈值。代码和对话与维基分布不同，ppl 较高不意味着低质量；KenLM 分数也不能独自决定数据去留。

CCNet 用 Wikipedia 训的 KenLM 打 perplexity，按分位数留网页。FineWeb 后来发现太猛的启发式会丢弃有用 token。AFM 的公开教训同构：规则减弱，模型分按语言校准。

## 交叉熵，不要只报一个「ppl 数」

$$
\mathrm{ppl}=\exp\bigl(-\tfrac1N\sum_t \log p(x_t\mid x_{\lt t})\bigr)
$$

现场没有 KenLM，用一个字符 trigram 顶上，接口和真模型一样：`score(text, lang) -> float`，越大越不像参考语。

```python
import math
from collections import Counter, defaultdict


class CharLM:
    """字符 n-gram 语言模型，加一平滑（假设字符表大小 256）。"""

    def __init__(self, n=3):
        self.n = n
        self.counts = defaultdict(Counter)  # 上下文 -> 下一个字符 -> 次数

    def fit(self, texts):
        for text in texts:
            s = " " * (self.n - 1) + text
            for i in range(self.n - 1, len(s)):
                self.counts[s[i - self.n + 1:i]][s[i]] += 1

    def logp(self, text):
        """每个字符的平均对数概率（自然对数）。"""
        s = " " * (self.n - 1) + text
        total_logp = 0.0
        n_chars = 0
        for i in range(self.n - 1, len(s)):
            context = s[i - self.n + 1:i]
            context_total = sum(self.counts[context].values()) + 256
            total_logp += math.log(self.counts[context][s[i]] + 1) - math.log(context_total)
            n_chars += 1
        return total_logp / max(n_chars, 1)


def ppl(lm, text):
    return math.exp(-lm.logp(text))


def keep_by_quantile(docs, score_fn, keep_frac=0.3):
    """score 越小越好（更像参考语料）。按 doc.lang 分组，每组保留分数最低的 keep_frac。"""
    if not 0 < keep_frac <= 1:
        raise ValueError("keep_frac must be in (0, 1]")
    by_lang = defaultdict(list)
    for doc in docs:
        by_lang[doc.lang].append((score_fn(doc), doc))
    kept = []
    for rows in by_lang.values():
        rows.sort(key=lambda row: row[0])
        k = max(1, int(len(rows) * keep_frac))
        kept.extend(doc for _, doc in rows[:k])
    return kept
```

### 可执行测试

```python
from dataclasses import dataclass


@dataclass
class Doc:
    doc_id: str
    lang: str
    text: str


reference = ["the cat sat on the mat. the dog sat on the log."] * 20
lm = CharLM(n=3)
lm.fit(reference)

# 像参考语料的句子 ppl 低，乱码 ppl 高
assert ppl(lm, "the cat sat on the log.") < ppl(lm, "zq#xv! 9@kw$")

# 完全没见过的上下文退化成均匀分布：ppl = 256
assert math.isclose(ppl(CharLM(n=3), "abc"), 256.0)

# 按语言分组取分位数：每种语言各留自己最好的那部分，而不是全局一刀
docs = [Doc(f"en-{i}", "en", "") for i in range(10)] + [Doc(f"zh-{i}", "zh", "") for i in range(4)]
scores = {doc.doc_id: i for i, doc in enumerate(docs)}  # zh 的分数整体更差
kept = keep_by_quantile(docs, lambda doc: scores[doc.doc_id], keep_frac=0.3)
assert [doc.doc_id for doc in kept] == ["en-0", "en-1", "en-2", "zh-0"]

# 非法比例直接报错
try:
    keep_by_quantile(docs, lambda doc: 0.0, keep_frac=0)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

参考语必须按语言各训一个：英语维基的 LM 会把正常中文打成天文 ppl。低资源没有维基时，用该语言的许可书或人工页，不要借用英语模型。

## 失败模式

代码、公式、对话和表格的 ppl 可能较高，因为它们不符合参考模型的分布。按域分别检查：网页用 ppl 信号，代码使用专门启发式或编译验证。

「像维基」会滤掉论坛里有用的答疑，和 `dt-quality-filter-code` 的教科书分类器是同一偏见。监督微调（SFT） 桶不要复用预训练 ppl。

分位数比绝对阈值稳。KenLM 换版本，绝对 ppl 会漂；留每语言头 30% 还可以比。扫 10% / 30% / 50%，用小模型看知识切片，不要只报「我们滤得很狠」。

## 追问

- **和分类器质量分怎么叠？** ppl 当一维特征，或先 ppl 粗切再跑分类器。不要两套硬门对着砍。
- **合成数据打 ppl？** 教师模型自己的续写 ppl 很低，会全留。合成数据使用任务验证器（verifier），见 `dt-rejection-sample-code`。
- **文档太长？** 随机抽 2k 字符打分，或按段打再取中位数。整本小说的 ppl 会被开头目录带歪。
