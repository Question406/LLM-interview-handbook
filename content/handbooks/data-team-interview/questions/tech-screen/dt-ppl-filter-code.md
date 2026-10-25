---
id: dt-ppl-filter-code
section: tech-screen
order: 20
level: A
title: CoderPad：KenLM / 困惑度质量门怎么写，阈值按语言怎么切？
quick: "用小语言模型算文档的平均交叉熵或困惑度，可以当质量的间接信号，但它只说明文本像不像参考语料。阈值要按语言和数据域取分位数，代码、公式和论坛要各设阈值，维基的阈值套不上。合成数据要用独立验证器，筛得好不好靠下游对照判断。"
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

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

实现一个简化字符语言模型和按语言保留低困惑度文档的接口。参考语料由调用者提供；本题只验证模型评分与分组过滤，不需要下载外部模型。

### 输入与接口

- `CharLM(n=3).fit(texts)` 接受参考文本列表，可累计训练；每个预测上下文长度为 n-1，句首用空格补齐。
- `logp(text)` 返回逐字符平均自然对数概率，`ppl(lm,text)` 返回该分数对应的困惑度。
- `keep_by_quantile(docs,score_fn,keep_frac=0.3)` 接受具有 lang 属性的文档对象及返回“越小越好”分数的函数。

### 输出与约束

字符条件概率采用加一平滑，分母为该上下文总计数加 256。空文本的平均 logp 为 0。`keep_by_quantile` 按语言分别保留分数最低的 `max(1,int(m*keep_frac))` 条，返回原文档对象列表。

分数相同时保持该语言文档在输入中的顺序，语言分组按首次出现顺序输出。`keep_frac` 位于 `(0,1]`。没有训练过的上下文使用均匀概率 1/256。

### 示例

```text
ppl(CharLM(n=3),"abc") -> 256.0
docs=[Doc("e1","en",""),Doc("e2","en",""),Doc("z1","zh","")]
对应 score 为 3、1、9，keep_frac=0.5
keep_by_quantile(...) -> [e2,z1]
```

## 解题思路与参考答案

我会用小语言模型算每篇文档的平均交叉熵，换算成 ppl，再按语言和数据域分别取分位数当阈值。它能当质量的间接信号，但它衡量的只是文本像不像参考语料。

比如一段 Python 代码，或者一段论坛对话，拿维基训的模型去打，ppl 天然就高，这不代表它们质量低。所以代码和对话要分开设阈值，KenLM 分数也不能单独决定去留。这个做法来自 CCNet，用 Wikipedia 训的 KenLM 打 perplexity，按分位数保留网页；后来 FineWeb 发现太猛的启发式会丢掉有用的 token，AFM 2025 报告也减弱了规则，并把模型分按语言校准。

## 先算交叉熵，再换算 ppl

$$
\mathrm{ppl}=\exp\bigl(-\tfrac1N\sum_t \log p(x_t\mid x_{\lt t})\bigr)
$$

现场没有 KenLM，我就用字符 trigram 顶上，接口和真模型一样：`score(text, lang) -> float`，值越大越不像参考语料。

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

测试覆盖正常句子和乱码、没见过的上下文、按语言分组取分位数：

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

打分是每个字符一次查表，线性；分位数每个语言排一次序。参考模型必须按语言各训一个，用英语维基训的 LM 去打正常中文，ppl 会高到离谱；低资源语言没有维基时，用该语言的许可书或人工页面，别借英语模型。

阈值用分位数比绝对值稳。KenLM 换版本后绝对 ppl 会漂，「每种语言保留前 30%」这种设定还能前后比较。我会扫 10% / 30% / 50% 三档，用小模型看知识切片的效果，每一档都要有下游对照。

## 会错在哪

代码、公式、对话和表格的 ppl 可能偏高，只是因为它们不符合参考模型的分布，所以要按域分开：网页用 ppl 信号，代码用专门的启发式或编译验证。「像维基」还会滤掉论坛里有用的答疑，这和 `dt-quality-filter-code` 里教科书分类器的偏见是同一个，SFT 的桶也别复用预训练的 ppl 阈值。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert ppl(lm, "the cat sat on the log.") < ppl(lm, "zq#xv! 9@kw$")` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**和分类器质量分怎么叠？**
把 ppl 当一维特征，或者先用 ppl 粗切再跑分类器。两套硬门各砍一刀会误杀太多。

**合成数据能用 ppl 筛吗？**
不行。教师模型自己续写的文本 ppl 很低，会全部留下。合成数据要用任务 verifier，见 `dt-rejection-sample-code`。

**文档太长怎么办？**
随机抽 2k 字符打分，或者按段打分再取中位数。整本小说的 ppl 会被开头的目录带偏。

**为什么用分位数，不用绝对阈值？**
KenLM 换版本后绝对 ppl 会漂，按语言取分位数前后还能比较。

相关：`dt-quality-filter-code`、`dt-rejection-sample-code`
