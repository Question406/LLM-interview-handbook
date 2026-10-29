---
id: dt-unicode-canon-code
section: tech-screen
order: 12
level: A
title: CoderPad：精确哈希之前，Unicode / 零宽字符怎么规范化？
quick: >-
  算精确哈希之前，先用 NFKC
  统一兼容字符和全角形式，按场景去掉零宽和控制字符，再压缩空白。规范化过度会把本来不同的文本变成一样，所以规则按数据类型开；跨文字体系的形近字映射只用在需要复核的高价值数据上。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Unicode Standard Annex
    url: 'https://unicode.org/reports/tr15/'
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
  - title: Confusable Detection (Unicode TR39)
    url: 'https://unicode.org/reports/tr39/'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

为文本 deduplication 提供稳定的 Unicode 规范化文本和指纹。

### 输入与接口

实现 canon(text,`strip_zero_width`=True) 和 fingerprint(text)。text 为 Unicode 字符串。canon 返回字符串；fingerprint 返回规范化文本 UTF-8 编码后的 BLAKE2b 十六进制摘要，`digest_size`=16。

### 输出与约束

canon 依次使用 NFKC 规范化、可选删除零宽字符、删除指定控制字符、转小写、把连续空白合并成一个 ASCII 空格并去掉首尾空白。零宽集合为 U+200B、U+200C、U+200D、U+FEFF、U+2060。控制字符集合为 U+0000–0008、000B–000C、000E–001F、007F。

制表符和换行作为空白合并，不能在删除控制字符时直接拼接它们两边的词。`strip_zero_width`=False 时保留上述零宽字符。不做同形异字映射，例如西里尔字母а不自动变成拉丁字母 a。fingerprint 使用 canon 的默认设置。

### 示例

```text
canon("ＡＢＣ１２３") -> "abc123"
canon("ﬁle") -> "file"
canon("line1\x07\n\tline2" 中相应转义表示的实际控制字符) -> "line1 line2"
canon("a\u200bb" 中包含实际U+200B字符) -> "ab"
fingerprint("ＡＢＣ") == fingerprint("abc") -> True
```

## 解题思路与参考答案

算精确哈希之前我会先规范化：用 NFKC 统一兼容字符和全角形式，按数据类型去掉零宽和控制字符，再压缩空白。这是 `dt-exact-dedup-code` 的预处理。

面试官常会贴两段「看起来一样」的转载，比如「price: 100 dollars」，另一份在冒号和数字后面各夹了一个零宽空格，或者一份写的是全角的 `ＡＢＣ１２３`，`hash(text)` 就对不上。选 NFKC，是因为按 UAX #15，NFKC 会把兼容字符折成规范形，全角 `Ａ` 变成 `A`，`ﬁ` 变成 `fi`；网页常用兼容区字符逃过精确哈希，NFC 不做这种兼容折叠。

## 便宜规则先做完

丢掉零宽字符（ZWSP、ZWNJ、BOM）和 C0 控制符，再小写、压缩空白。

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

测试覆盖全角、连字、零宽、关掉零宽剥离、控制符和不做 homoglyph：

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

每篇文本线性扫几遍，成本可以忽略。有两件事我不会放进默认路径。一是去掉所有标点，公式、代码和 multilingual 里的撇号都会被破坏。二是全表 homoglyph 映射（把西里尔 `а` 当成拉丁 `a`），TR39 的混淆表很大，会 false rejection 俄语和希腊语正文，只在「和评测题面比」或「和许可书比」这种高价值路径上开。

## 按域开启

代码保留空白结构，只去零宽字符，`dt-winnow-code` 处理的是 token，不用这套 NFKC。中日韩用 NFKC 会改动兼容汉字，一般可以接受，但别再额外 `casefold`，否则会出现奇怪的匹配。SFT 对话里，用户有意打的零宽字符（隐写、越狱）应当清掉再训，但 lineage 要记 `stripped_zw=true`，安全评测另留一份原文，见 `dt-safety-refuse`。

规范化过度的信号是短文档的碰撞率突然升高，这时抽 100 对人工看，再决定要不要关掉某一条规则。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert canon("ＡＢＣ１２３") == "abc123"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条 assertion 都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**NFC 和 NFKC 选哪个？**
deduplication 用 NFKC，存档和展示用 NFC 或原文。训练用的是哪一份要写进 dataset card。

**零宽字符算 PII 吗？**
不算，它是 deduplication 和注入的问题。PII 检查走 `dt-pii-luhn-code`。

**和 MinHash 什么关系？**
shingle 也要从 `canon` 之后的文本切，不然同一篇转载会得到两套签名。

**怎么发现规范化过度了？**
看短文档的碰撞率，突然升高就抽 100 对人工看，再决定关哪条规则。

相关：`dt-exact-dedup-code`、`dt-winnow-code`、`dt-safety-refuse`、`dt-pii-luhn-code`
