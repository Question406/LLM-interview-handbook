---
id: dt-pii-luhn-code
section: tech-screen
order: 11
level: A
title: CoderPad：PII 门怎么写，信用卡 Luhn 和代码假阳性怎么处理？
quick: "先用正则找可能的个人信息，再用 Luhn 校验信用卡号、检查邮箱和电话格式。命中后记录文本位置，隔离或脱敏由单独规则决定。代码中的示例卡号 `4111-1111-1111-1111` 和 ISBN 可能误报，要结合领域白名单判断，不能静默删除。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - PII
  - Filtering
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: ISO/IEC 7812 (Luhn check)
    url: https://en.wikipedia.org/wiki/Luhn_algorithm
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先用正则找候选，信用卡号用 Luhn 校验，邮箱和电话再检查格式。命中后记录 span，并隔离检查。代码和论文里的示例卡号、ISBN 可能误报，要按领域设置白名单，不能直接用 `re.sub` 悄悄删掉。`dt-quality-filter-code` 的信用卡正则是第一刀。追问常是：假阳怎么办、挖空还是整篇扔。现场不要发明内部检测器名字。

Luhn：从右往左，奇数位原样，偶数位乘 2（大于 9 再减 9），和能被 10 整除才像卡号。`4` 开头 16 位很多是示例卡，校验过了仍可能是文档。Apple 支持页写了会滤标识、避开大规模汇聚个人信息的站。

## 候选加校验，不要只靠正则

```python
import re
from dataclasses import dataclass

# 13 到 19 位数字，中间可夹单个空格或连字符；不吞掉末尾的分隔符
CARD = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{4}(?!\w)"
)


@dataclass
class Span:
    kind: str
    start: int
    end: int
    value: str


def luhn_ok(digits):
    """Luhn 校验：从右往左每隔一位乘 2（大于 9 减 9），总和能被 10 整除。"""
    if not digits.isdigit():
        raise ValueError("luhn_ok expects a string of digits")
    total = 0
    double = False
    for ch in reversed(digits):
        n = int(ch)
        if double:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        double = not double
    return total % 10 == 0


def find_pii(text):
    """返回候选 PII span。只做检测，删除还是脱敏由上层决定。"""
    spans = []
    card_ranges = []
    for m in CARD.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            spans.append(Span("card", m.start(), m.end(), m.group()))
            card_ranges.append((m.start(), m.end()))
    for m in EMAIL.finditer(text):
        spans.append(Span("email", m.start(), m.end(), m.group()))
    for m in PHONE.finditer(text):
        # 卡号里的数字片段不重复报成电话
        if any(start <= m.start() < end for start, end in card_ranges):
            continue
        spans.append(Span("phone", m.start(), m.end(), m.group()))
    return spans
```

### 可执行测试

```python
# Luhn：测试卡号通过，改一位就不通过
assert luhn_ok("4111111111111111")
assert not luhn_ok("4111111111111112")
assert luhn_ok("79927398713")

# 带空格的卡号被识别为 card，span 覆盖原文
text = "Charge card 4111 1111 1111 1111 today."
spans = find_pii(text)
assert [s.kind for s in spans] == ["card"]
assert text[spans[0].start:spans[0].end] == "4111 1111 1111 1111"

# span 不包含卡号后面的空格
assert spans[0].value == "4111 1111 1111 1111"

# 过不了 Luhn 的 16 位数字（如订单号）不报 card
assert all(s.kind != "card" for s in find_pii("order 1234567812345678"))

# 邮箱和电话各自识别
spans = find_pii("mail alice@example.com or call +1 415-555-0123")
assert [(s.kind, s.value) for s in spans] == [
    ("email", "alice@example.com"),
    ("phone", "+1 415-555-0123"),
]

# 没有 PII 的文本返回空列表
assert find_pii("nothing sensitive here") == []
```

决策不要写在检测里。网页正文命中卡号：整篇 quarantine。论坛回复里一个邮箱：挖空后可留，lineage 记 `redacted=email`。代码仓库：检测器打开，但 `example.com`、`4111111111111111`、测试夹具进白名单。

## 假阳性

ISBN、EAN、Git commit 里的长数字串、US 电话和订单号。Luhn 能挡一批，挡不住示例卡。NER / 专用检测器是下一层，热路径仍先正则。

身份证、护照号按 locale 分规则，不要用一张美国正则打全球。AFM 过滤是按语言校准的，PII 同样按域开。

挖空后的文本会变成 `please charge ****`，质量分可能掉。因此先记下 span，再决定删除整篇还是脱敏。静默 `re.sub` 会让下周归因对不上。

## 追问

- **用户对话能扫了就进预训练吗？** 苹果默认用户交互不进基础模型。这题扫的是许可网页和开源集，见 `dt-privacy-feedback`。
- **假名邮箱呢？** `noreply@`、`github.com` 的 noreply 可以放行。个人域邮箱不行。
- **只脱敏不删除，评测还能用吗？** 脱敏后的文档不能混入「未脱敏」的对照实验。dataset card 写检测器版本。
