---
id: dt-lid-code
section: tech-screen
order: 17
level: A
title: CoderPad：语言识别怎么写，文档级和段落级差在哪？
quick: >-
  现场写一个字符 3-gram 朴素贝叶斯来识别语言。先剥掉代码块，再按段落分别识别，否则英语页里的中文段会被一起标成英语。分数低于阈值时输出
  `und`，表示判断不了，别硬猜。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Bag of Tricks for Efficient Text Classification (fastText)
    url: 'https://arxiv.org/abs/1607.01759'
    type: primary
  - title: fastText language identification
    url: 'https://fasttext.cc/docs/en/language-identification.html'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现一个用于数据分桶的简化语言识别器，接受带语言标签的训练文本，预测新文本的语言；证据不足时允许输出 `und`，而不是强行指定一种语言。

### 输入与接口

- `char_ngrams(text,n=3)` 将文本转小写并合并空白，返回连续字符 n-gram 列表；非空短文本整体作为一个 gram。
- `Lid().fit(pairs)` 接受 `(lang,text)` 序列，可累计训练计数。
- `predict(text,min_log=None)` 在训练后调用，返回语言标签和分数。

### 输出与约束

分数是本题字符 3-gram 模型的平均对数分数：语言先验项为 `log(total+1)`，每个 gram 使用分子 `count+0.1`、分母 `total+10**6`，最后除以 gram 数。选择分数最大的语言；低于 `min_log` 时标签为 und，仍返回该最佳分数。

空文本没有 gram，返回 `("und",0.0)`。并列语言按训练中首次出现顺序选择。predict 不额外删除代码块；如需预处理，调用者可先把三反引号包围的代码块替换为空格，再传入字符串。

### 示例

```text
char_ngrams("Hello",3) -> ["hel","ell","llo"]
lid=Lid(); lid.fit([("en","the cat"),("zh","今天天气很好")])
lid.predict("   ") -> ("und",0.0)
lid.predict("the cat")[0] -> "en"
```

## 解题思路与参考答案

我会现场写一个字符 3-gram 朴素贝叶斯，先剥掉代码块、再按段落分别识别，判断不了就输出 `und`。后面的质量过滤、语言配额和 PII 检查都依赖这个标签，所以输出什么、失败时怎么处理要先讲清楚。

比如一篇论文，英文摘要加中文正文，整页只打一个 `en`，中文那几段就跟着进了英语桶。维基的中英对照、英语题面加代码的 Stack Overflow 也是一样，所以混排页要拆开，每段各打各的标签。

用字符 n-gram，是因为 vocabulary LID 在 low-resource 语言和拼写噪声上会失效。fastText 也用字符 n-gram，公开的 lid.176 是生产里常见的组件。现场写 3-gram 加对数计数：

```python
import math
import re
from collections import Counter, defaultdict

CODE = re.compile(r"```.*?```", re.S)  # 识别前先用 CODE.sub(" ", text) 剥掉代码块


def char_ngrams(text, n=3):
    s = " ".join(text.lower().split())
    if len(s) < n:
        return [s] if s else []
    return [s[i : i + n] for i in range(len(s) - n + 1)]


class Lid:
    """字符 3-gram 朴素贝叶斯语言识别。分数是每个 gram 的平均 log probability。"""

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
                log_score += math.log(self.gram_counts[lang][gram] + 0.1) - math.log(
                    denominator
                )
            scores[lang] = log_score / len(grams)
        best = max(scores, key=scores.get)
        if min_log is not None and scores[best] < min_log:
            return "und", scores[best]
        return best, scores[best]
```

测试覆盖两种语言、空文本、低分输出 `und`、剥代码块和未训练调用：

```python
lid = Lid()
lid.fit(
    [
        (
            "en",
            "the quick brown fox jumps over the lazy dog and the cat sat on the mat",
        ),
        ("en", "this is an english sentence about language identification and data"),
        ("zh", "今天天气很好，我们一起去公园散步吧。语言识别是数据处理的第一步。"),
        ("zh", "这是一个中文句子，用来训练字符级的语言识别模型。"),
    ]
)

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

预测时每个语言扫一遍 gram，成本是 gram 数乘语言数。`und` 是合法输出，把它硬塞进 `en`，会 contamination 英语的质量分类器。

## 先切块，再识别

先剥掉代码块（`CODE.sub(" ", text)`），代码走代码桶，不用网页 LID。剩下的按空行切段，段长超过 40 字符才打标签。文档的主语言是覆盖 token 最多的那个语言，少数语言的段落进对应的语言桶，或者进 `und`。AFM 2025 报告也是按语言挑选训练文档和标签的。

n 取多少也有讲究。中日韩这类文字 3-gram 就够用；拉丁语族之间要用 4-gram 或词特征，不然西语和葡语会混。生产上仍然 distillation fastText，现场这份代码的作用是把输入输出的约定写清楚。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert lid.predict("the dog and the cat")[0] == "en"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**机翻页被 LID 识别成目标语言，能算进该语言的配额吗？**
来源要另外记录。评测用母语者写的题，见 `dt-locale-data`。

**短标题怎么处理？**
对 10 个字符做文档级 LID 没有意义。短字段跟随页面的主语言，或者标 `und`。

**质量模型和 LID 谁先跑？**
先 LID，再用按语言设定的质量阈值，见 `dt-quality-filter-code`。

**西语和葡语老混怎么办？**
3-gram 分不开拉丁语族之间的细差别，换 4-gram 或者加词特征。

相关：`dt-locale-data`、`dt-quality-filter-code`
