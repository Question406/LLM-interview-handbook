---
id: dt-pii-luhn-code
section: tech-screen
order: 11
level: A
title: CoderPad：PII 门怎么写，信用卡 Luhn 和代码假阳性怎么处理？
quick: "先用正则找可能的个人信息，再做校验：信用卡号用 Luhn，邮箱和电话查格式。命中后记下文本位置，隔离还是脱敏交给单独的规则决定。代码里的示例卡号 `4111-1111-1111-1111` 和 ISBN 会误报，要按领域设白名单，命中都记录下来再处理。"
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

我分两层做：先用正则找候选，再校验，信用卡号用 Luhn，邮箱和电话查格式。命中后只记 span 并隔离检查，整篇扔还是挖空交给单独的决策规则。`dt-quality-filter-code` 里的信用卡正则是第一刀，这题在它后面补上校验。

比如「Charge card 4111 1111 1111 1111 today.」，正则先抓到一串 16 位数字，Luhn 过了，记成 card。换成「order 1234567812345678」，同样 16 位，Luhn 不过，就不报。不过 `4111111111111111` 本身是文档里常见的示例卡，校验过了也可能只是文档，所以代码和论文里的示例卡号、ISBN 都要按领域设白名单。

Luhn 的规则是从右往左，奇数位原样，偶数位乘 2（大于 9 再减 9），总和能被 10 整除才像卡号。

## 正则找候选，再做校验

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

测试覆盖 Luhn、带空格的卡号、span 边界、订单号、邮箱电话和空结果：

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

几个正则都是线性扫一遍，热路径上跑得动，更贵的检测器放到后面。

## 检测和决策分开

检测函数只负责找 span，怎么处理按场景定。网页正文里命中卡号，整篇 quarantine；论坛回复里有一个邮箱，挖空后可以留，lineage 记 `redacted=email`；代码仓库里检测器照样打开，但 `example.com`、`4111111111111111` 和测试夹具进白名单。先记 span 再决定，是因为挖空后的文本会变成 `please charge ****`，质量分可能下降，静默 `re.sub` 会让下周的归因对不上。

## 追问

**假阳性一般从哪来？**
ISBN、EAN、Git commit 里的长数字串、美国电话号码和订单号。Luhn 能挡掉一批，但挡不住示例卡。下一层是 NER 或专用检测器，热路径上仍然先跑正则。

**身份证、护照号怎么查？**
按 locale 分规则，别用一张美国正则扫全球。PII 检测和质量过滤一样，要按语言校准、按域开关。

**命中了是挖空还是整篇扔？**
看场景：网页正文里有卡号整篇 quarantine，论坛回复里一个邮箱挖空后可以留，并在 lineage 里记下来。

**假名邮箱呢？**
`noreply@` 和 `github.com` 的 noreply 地址可以放行，个人域名邮箱不行。

**只脱敏不删除，评测还能用吗？**
脱敏后的文档不能混进「未脱敏」的对照实验，dataset card 里要写检测器版本。

相关：`dt-quality-filter-code`
