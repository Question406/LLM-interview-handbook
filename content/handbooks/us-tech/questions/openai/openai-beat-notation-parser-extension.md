---
id: openai-beat-notation-parser-extension
section: openai
order: 933
level: A
title: "OpenAI 题型扩展：解析 beat notation，用 Fraction 校验 bar duration"
quick: "我会先把 syntax 和音乐规则分开。Regex 负责检查一个 note token 的形状，Fraction 负责算 duration，遇到 bar separator 时再检查总时长。"
companies:
  - openai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：OpenAI 题型扩展：解析 beat notation，用 Fraction 校验 bar duration"
    url: "https://aceoffer.app/interviews/oai_staff_beat_notation_conversion"
    type: secondary
---

## 题目描述

来源：AceOffer 公开页面列出 Staff / Beat Notation Conversion 与 structured-text parsing。以下 text format、4/4 bar 规则与输出 schema 均由手册定义。

### 输入、接口与规则

实现 `parse_score(text) -> list[list[tuple[str,Fraction]]]`。输入是一段自定义 notation：空白分隔 tokens；音符 token 为 `C4:1/4` 这种形式，pitch 必须匹配 `[A-G][0-8]`，或为 `REST`。冒号后是正整数 numerator/denominator，表示以 whole note 为单位的 duration；不支持 accidentals。每个 bar 以独立 token `|` 结束。

每个 bar 的 duration 之和必须恰好为 1，即一个 4/4 bar。返回 bars，每个 bar 是 `(pitch, Fraction)` 列表，保留 token 顺序。空文本返回 []；非法 token、零 duration、空 bar、总 duration 不等于 1、最后未写 | 均抛 ValueError。用 exact rational arithmetic；不修改输入。

### 输入输出示例

```text
输入 "C4:1/2 REST:1/4 D4:1/4 |"
返回 [[("C4",Fraction(1,2)),("REST",Fraction(1,4)),("D4",Fraction(1,4))]]。
输入 "C4:1/3 C4:1/3 C4:1/3 |" 合法。
输入 "C4:1/4 |" -> ValueError。
```

## 回答思路

> **Situation / Task：** Grammar 和时间单位先固定；输出必须保留 bar 与 note 次序。  
> **Approach / Why：** Token parser 验证 syntax，Fraction 精确累计每个 bar 的 duration。  
> **Result / Check：** 检查三分音符、空 bar、非法 pitch 和缺失结束符。

## 解题思路与参考答案

我会先把 syntax 和音乐规则分开。Regex 负责检查一个 note token 的形状，Fraction 负责算 duration，遇到 bar separator 时再检查总时长。

这里不能用 float 累加后直接比较 1。像三个 1/3 应该严格组成一小节；exact rational arithmetic 可以让合法性判断和输出格式都保持确定。

### 完整参考实现

```python
import re
from fractions import Fraction


def parse_score(text):
    token_re = re.compile(r'([A-G][0-8]|REST):([0-9]+)/([0-9]+)')
    bars = []
    current = []
    total = Fraction(0)
    for token in text.split():
        if token == '|':
            if not current or total != 1:
                raise ValueError('invalid bar duration')
            bars.append(current)
            current = []
            total = Fraction(0)
            continue
        match = token_re.fullmatch(token)
        if not match:
            raise ValueError('invalid token')
        pitch, num, den = match.groups()
        num, den = int(num), int(den)
        if num <= 0 or den <= 0:
            raise ValueError('duration must be positive')
        duration = Fraction(num, den)
        current.append((pitch, duration))
        total += duration
    if current:
        raise ValueError('missing bar separator')
    return bars
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert parse_score('C4:1/2 REST:1/4 D4:1/4 |') == [
    [('C4', Fraction(1, 2)), ('REST', Fraction(1, 4)), ('D4', Fraction(1, 4))]
]
assert parse_score('C4:1/3 C4:1/3 C4:1/3 |') == [[('C4', Fraction(1, 3))] * 3]
assert parse_score('') == []
assert len(parse_score('C4:1/1 | D4:1/1 |')) == 2
for bad in ['|', 'C9:1/1 |', 'C4:0/1 |', 'C4:1/0 |', 'C4:1/4 |', 'C4:1/1', 'C4:1/1|']:
    try:
        parse_score(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(bad)
print('beat parser tests passed')
```

## 复杂度与追问

若输入字符数为 N，在整数位宽受限时 parsing 约 `O(N)`；Fraction arithmetic 的实际成本还取决于 numerator/denominator 的位数。追问允许变拍号时，把 bar expected duration 作为输入，不能硬编码为 1。
