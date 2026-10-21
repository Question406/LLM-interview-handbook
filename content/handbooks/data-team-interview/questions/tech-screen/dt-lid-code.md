---
id: dt-lid-code
section: tech-screen
order: 17
level: A
title: CoderPad：语言识别怎么写，文档级和段落级差在哪？
quick: "现场可以写一个字符 3-gram 朴素贝叶斯来识别语言。先剥掉代码块，再按段落分别识别，否则英语页里的中文段会被一起标成英语。分数低于阈值时输出 `und`，表示无法可靠判断，不要硬猜。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Language ID
  - Multilingual
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Bag of Tricks for Efficient Text Classification (fastText)"
    url: https://arxiv.org/abs/1607.01759
    type: primary
  - title: "fastText language identification"
    url: https://fasttext.cc/docs/en/language-identification.html
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

现场可以写一个字符 3-gram 朴素贝叶斯。要讲清的是两点：整页只给一个语言标签，会漏掉英语页里的中文段落，所以混排内容要先剥掉代码、再分段识别；无法可靠判断时输出 `und`。后面的质量过滤、语言配额和 PII 检查都依赖这个标签，所以分类器输出什么、失败时怎么处理，都要说清楚。

## 用字符 n-gram

用字符 n-gram，是因为词表 LID 在低资源语言和拼写噪声上会失效。fastText 也用字符 n-gram，公开的 lid.176 是生产里常见的组件。现场写 3-gram 加对数计数：

```python
import math
import re
from collections import Counter, defaultdict

CODE = re.compile(r"```.*?```", re.S)  # 识别前先用 CODE.sub(" ", text) 剥掉代码块


def char_ngrams(text, n=3):
    s = " ".join(text.lower().split())
    if len(s) < n:
        return [s] if s else []
    return [s[i:i + n] for i in range(len(s) - n + 1)]


class Lid:
    """字符 3-gram 朴素贝叶斯语言识别。分数是每个 gram 的平均对数概率。"""

    def __init__(self):
        self.gram_counts = defaultdict(Counter)  # lang -> gram -> 次数
        self.lang_totals = Counter()  # lang -> gram 总数

    def fit(self, pairs):
        """pairs: iterable[(lang, text)]。"""
        for lang, text in pairs:
            grams = char_ngrams(text)
            self.lang_totals[lang] += len(grams)
            self.gram_counts[lang].update(grams)

    def predict(self, text, min_log=None):
        """返回 (lang, score)。没有 gram 或分数低于 min_log 时返回 "und"。"""
        if not self.lang_totals:
            raise ValueError("call fit() before predict()")
        grams = char_ngrams(text)
        if not grams:
            return "und", 0.0
        scores = {}
        for lang, total in self.lang_totals.items():
            log_score = math.log(total + 1)  # 粗略的语言先验
            denominator = total + 1e6  # 平滑，未见 gram 也有小概率
            for gram in grams:
                log_score += math.log(self.gram_counts[lang][gram] + 0.1) - math.log(denominator)
            scores[lang] = log_score / len(grams)
        best = max(scores, key=scores.get)
        if min_log is not None and scores[best] < min_log:
            return "und", scores[best]
        return best, scores[best]
```

### 可执行测试

```python
lid = Lid()
lid.fit([
    ("en", "the quick brown fox jumps over the lazy dog and the cat sat on the mat"),
    ("en", "this is an english sentence about language identification and data"),
    ("zh", "今天天气很好，我们一起去公园散步吧。语言识别是数据处理的第一步。"),
    ("zh", "这是一个中文句子，用来训练字符级的语言识别模型。"),
])

# 训练过的两种语言各自识别正确
assert lid.predict("the dog and the cat")[0] == "en"
assert lid.predict("我们去公园散步")[0] == "zh"

# 空文本没有 gram，输出 und
assert lid.predict("   ") == ("und", 0.0)

# 分数低于 min_log 时宁可输出 und，也不硬塞进某个语言
lang, score = lid.predict("zxqv wkjp", min_log=-5.0)
assert lang == "und"
assert score < -5.0

# 识别前先剥代码块
mixed = "这是正文。```print('hello world')``` 还是正文。"
assert "print" not in CODE.sub(" ", mixed)

# 未训练就预测是调用错误
try:
    Lid().predict("hello")
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

`und` 是合法输出。把它硬塞进 `en`，会污染英语的质量分类器。

## 先切块，再识别

先剥掉代码块（`CODE.sub(" ", text)`），代码走代码桶，不用网页 LID。剩下的按空行切段，段长超过 40 字符才打标签。文档的主语言是覆盖文本处理单位（token）最多的那个语言；少数语言的段落进对应的语言桶，或者进 `und`。

整页一个标签会吃掉很多常见页面：维基的中英对照、英文摘要加中文正文的论文、英语题面加代码的 Stack Overflow。混排页要拆开，每段各打各的标签；AFM 2025 报告也是按语言挑选训练文档和标签的。

n 的取值也有讲究。中日韩这类文字，3-gram 就够用；拉丁语族之间要用 4-gram 或词特征，否则西语和葡语会混。生产上仍然蒸馏 fastText，现场这份代码的作用是把输入输出的约定写清楚。

## 追问

- **机翻页被 LID 识别成目标语言，能算进该语言的配额吗？** 来源要另外记录。评测用母语者写的题，见 `dt-locale-data`。
- **短标题怎么处理？** 对 10 个字符做文档级 LID 没有意义。短字段跟随页面的主语言，或者标 `und`。
- **质量模型和 LID 谁先跑？** 先 LID，再用按语言设定的质量阈值，见 `dt-quality-filter-code`。
