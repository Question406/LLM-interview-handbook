---
id: dt-pii-luhn-code
section: tech-screen
order: 11
level: A
title: CoderPad：PII 门怎么写，信用卡 Luhn 和代码假阳性怎么处理？
quick: >-
  先用正则找可能的 personally identifiable information (PII)，再做校验：信用卡号用
  Luhn，邮箱和电话查格式。命中后记下文本位置，隔离还是脱敏交给单独的规则决定。代码里的示例卡号 `4111-1111-1111-1111` 和 ISBN
  会 false positive，要按领域设白名单，命中都记录下来再处理。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: ISO/IEC 7812 (Luhn check)
    url: 'https://en.wikipedia.org/wiki/Luhn_algorithm'
    type: primary
  - title: Datasets used for Apple Intelligence
    url: 'https://www.apple.com/legal/ai-regulations/training-data/'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现文本中的敏感信息候选检测，包括银行卡号、邮箱和电话号码。返回原文中可定位的片段；只检测，不删除文本，也不联系任何外部服务。

### 输入与接口

- `luhn_ok(digits)` 接受只含十进制数字的字符串，判断是否通过标准 Luhn 校验。
- `find_pii(text)` 返回 `Span(kind,start,end,value)` 对象列表，start/end 是 Python 字符串的左闭右开下标。
- 卡号候选为 13–19 位数字，数字间可有单个空格或连字符，且必须通过 Luhn。邮箱与电话使用下文给出的正则匹配约定。

### 输出与约束

kind 取 card、email 或 phone；value 必须等于 `text[start:end]`，片段不能吞掉末尾空白或标点。没有候选时返回空列表。结果按 card、email、phone 三类顺序列出，各类内部按出现顺序。

银行卡号覆盖范围内的数字片段不能再次报告为电话。电话格式允许可选的 1–3 位国家码、2–4 位区号，以及 3–4 位加 4 位本地号码；精确匹配规则为：邮箱使用
`EMAIL = \b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b`（忽略大小写）；电话使用
`PHONE = (?<!\w)(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{4}(?!\w)`（区分大小写不影响数字匹配）。Luhn 的定义是从右边第二位开始隔位翻倍，大于 9 的数减 9，总和应能被 10 整除。

### 示例

```text
luhn_ok("4111111111111111") -> True
luhn_ok("4111111111111112") -> False
find_pii("mail a@b.com")
-> [Span(kind="email",start=5,end=12,value="a@b.com")]
```

## 解题思路与参考答案

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

测试覆盖 Luhn、带空格的卡号、span boundaries、订单号、邮箱电话和空结果：

```python
# Luhn：测试卡号通过，改一位就不通过
assert luhn_ok("4111111111111111")
assert not luhn_ok("4111111111111112")
assert luhn_ok("79927398713")

# 带空格的卡号被识别为 card，span 覆盖原文
text = "Charge card 4111 1111 1111 1111 today."
spans = find_pii(text)
assert [s.kind for s in spans] == ["card"]
assert text[spans[0].start : spans[0].end] == "4111 1111 1111 1111"

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

检测函数只负责找 span，怎么处理按场景定。网页正文里命中卡号，整篇 quarantine；论坛回复里有一个邮箱，挖空后可以留，lineage 记 `redacted=email`；代码仓库里检测器照样打开，但 `example.com`、`4111111111111111` 和测试夹具进白名单。先记 span 再决定，是因为挖空后的文本会变成 `please charge ****`，质量分可能下降，静默 `re.sub` 会让下周的 attribution 对不上。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert luhn_ok("4111111111111111")` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**假阳性一般从哪来？**
ISBN、EAN、Git commit 里的长数字串、美国电话号码和订单号。Luhn 能挡掉一批，但挡不住示例卡。下一层是 NER 或专用检测器，热路径上仍然先跑正则。

**身份证、护照号怎么查？**
按 locale 分规则，别用一张美国正则扫全球。PII 检测和质量过滤一样，要按语言做 calibration、按域开关。

**命中了是挖空还是整篇扔？**
看场景：网页正文里有卡号整篇 quarantine，论坛回复里一个邮箱挖空后可以留，并在 lineage 里记下来。

**假名邮箱呢？**
`noreply@` 和 `github.com` 的 noreply 地址可以放行，个人域名邮箱不行。

**只脱敏不删除，评测还能用吗？**
脱敏后的文档不能混进「未脱敏」的对照实验，dataset card 里要写检测器版本。

相关：`dt-quality-filter-code`
