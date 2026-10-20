---
id: dt-lid-code
section: tech-screen
order: 17
level: A
title: CoderPad：语言识别怎么写，文档级和段落级差在哪？
quick: "现场可以用字符 3-gram 朴素贝叶斯识别语言。先去掉代码块，再按段落识别混排文档，避免把英语页中的中文段也归入英语。低于阈值的标为 `und`，表示无法可靠判断，不能硬猜。"
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

可以先写字符 3-gram 朴素贝叶斯。整页只给一个语言标签，会漏掉英语页中的中文段落，所以混排内容和引用要分段识别，代码单独处理。无法可靠判断时输出 `und`。后续质量过滤、配额和 PII 检查都依赖语言分类，因此需要明确分类器的输出与失败处理。

fastText 用字符 n-gram，公开 lid.176 是生产常见件。词表 LID 在低资源语言和拼写噪声上会死。

## 字符 n-gram，不要词表

现场用 3-gram + 对数计数：

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

`und` 是合法输出。硬塞进 `en` 会污染英语质量分类器。

## 切块再识别

先剥代码块（`CODE.sub(" ", text)`），代码走代码桶，不用网页 LID。剩下按空行切段，段长于 40 字符才打标签。文档的主语言 = 覆盖 文本处理单位（token） 最多的语言；少数段进对应语言桶，或进 `und`。

常见误区是：整页一个标签。维基中英对照、论文英文摘要加中文正文、Stack Overflow 英语题面加代码，都会被吃掉。AFM 按语言选训练文档和标签，混排页要拆。

脚本语言（中日韩）3-gram 够用。拉丁语族之间要 4-gram 或词特征，否则西语 / 葡语会混。口播：生产仍蒸馏 fastText，现场这份是合同。

## 追问

- **机翻页 LID 是目标语，能进该语言配额吗？** 来源要另记。评测用母语者题，见 `dt-locale-data`。
- **短标题？** 文档级 LID 对 10 个字符没意义。短字段跟页面主语言，或标 `und`。
- **质量模型和 LID 谁先？** 先 LID，再按语言的质量阈值，见 `dt-quality-filter-code`。
