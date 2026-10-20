---
id: dt-unicode-canon-code
section: tech-screen
order: 12
level: A
title: CoderPad：精确哈希之前，Unicode / 零宽字符怎么规范化？
quick: "计算精确哈希前，可以用 NFKC 统一兼容字符和全角形式，按场景清除零宽与控制字符，再压缩空白。规范化过度会把不同文本变成一样，因此规则应按数据类型启用；跨文字体系的相似字符映射，只用于需要复核的高价值数据。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Dedup
  - Unicode
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Unicode Standard Annex #15 (Unicode Normalization Forms)
    url: https://unicode.org/reports/tr15/
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: Confusable Detection (Unicode TR39)
    url: https://unicode.org/reports/tr39/
    type: primary
---

在精确哈希之前，先用 NFKC 统一兼容字符和全角形式，按数据类型移除零宽和控制字符，再压缩空白。这是 `dt-exact-dedup-code` 的预处理。过度规范化可能合并本来不同的语言文本，所以规则要按域启用；homoglyph 映射只对高价值子集使用。评委会贴两段「看起来一样」的转载：一段夹了零宽空格，一段用全角数字。`hash(text)` 对不上。

UAX #15：NFKC 把兼容字符折到规范形，全角 `Ａ` 变 `A`，`ﬁ` 变 `fi`。网页喜欢用兼容区字符逃过精确哈希，不要 NFC 完事。

## 便宜规则先做完

零宽字符（ZWSP、ZWNJ、BOM）和 C0 控制符丢掉。再小写、压缩空白。

```python
import hashlib
import re
import unicodedata

# 零宽空格、ZWNJ、ZWJ、BOM、word joiner
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍﻿⁠"))
CONTROL = re.compile(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]")
WHITESPACE = re.compile(r"\s+")


def canon(text, strip_zero_width=True):
    """去重用的规范形：NFKC、去零宽和 C0 控制符、小写、压缩空白。"""
    text = unicodedata.normalize("NFKC", text)
    if strip_zero_width:
        text = text.translate(ZERO_WIDTH)
    text = CONTROL.sub("", text)
    text = text.lower()
    return WHITESPACE.sub(" ", text).strip()


def fingerprint(text):
    return hashlib.blake2b(canon(text).encode(), digest_size=16).digest()
```

### 可执行测试

```python
# 全角字母数字经 NFKC 折成半角
assert canon("ＡＢＣ１２３") == "abc123"

# 连字 ﬁ 展开成 fi
assert canon("ﬁle") == "file"

# 夹了零宽空格的转载和原文指纹相同
assert fingerprint("price: 100 dollars") == fingerprint("price:​ 100​ dollars")

# 关掉零宽剥离时，两者不再相同（代码等需要保留原样的域）
assert canon("a​b", strip_zero_width=False) != canon("ab", strip_zero_width=False)

# 控制符删除，换行和制表符压成单个空格
assert canon("line1\x07\n\n\tline2") == "line1 line2"

# 不做 homoglyph 映射：西里尔 а 和拉丁 a 仍然不同
assert canon("а") != canon("a")
```

口播两处不要做进默认路径：

1. 去掉所有标点。公式、代码、多语的撇号会塌。
2. 全表 homoglyph（西里尔 `а` 当拉丁 `a`）。TR39 的混淆表很大，误杀俄语、希腊语正文。只对「和评测题面比」或「和许可书比」的高价值路径开。

## 按域开

代码：保留空白结构，只去零宽。`dt-winnow-code` 吃的是 文本处理单位（token），不吃这套 NFKC。

中日韩：NFKC 会动兼容汉字，一般可接受；不要额外 `casefold` 出奇怪匹配。

监督微调（SFT） 对话：用户有意打的零宽（隐写、越狱）应当被清掉再训，但 lineage 记 `stripped_zw=true`，安全评测另留一份原文，见 `dt-safety-refuse`。

规范化过度的信号：短文档碰撞率突然升高。抽 100 对人工看，再决定要不要关某一条规则。

## 追问

- **NFC 和 NFKC 选哪个？** 去重用 NFKC。存档 / 展示用 NFC 或原文。训练吃哪份要写进 dataset card。
- **零宽是 PII 吗？** 不是。它是去重和注入的问题。真 PII 走 `dt-pii-luhn-code`。
- **和 MinHash 的关系？** shingle 也要从 `canon` 后的文本切，否则同一转载两套签名。
