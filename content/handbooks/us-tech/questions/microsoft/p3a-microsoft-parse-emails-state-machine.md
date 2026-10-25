---
id: p3a-microsoft-parse-emails-state-machine
section: microsoft
order: 605
level: A
title: "Microsoft AI / Copilot：日志邮箱解析：显示名、注释与去重"
quick: "我会用状态机逐字符扫描，只在引号和括号注释之外用分号结束记录，同时保留转义状态。记录取出地址后再校验，按完整地址忽略大小写去重、保留首次写法；流结束时状态未闭合就报错。"
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · parse-emails-state-machine"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/parse-emails-state-machine
    type: secondary
---

## 题目描述

从含显示名、注释和分隔符的邮件地址列表中提取地址，保留出现顺序并去重。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`emails(text)` 返回邮箱字符串列表。顶层分号分隔记录；双引号显示名中允许反斜杠转义，圆括号注释允许嵌套，二者内部的分号不分隔记录。输入的引号、注释和转义结构平衡。

这是有限的邮件语法子集：地址本地部分使用 ASCII 字母、数字及 `._+-`，域名须有点分隔；可提取 `显示名 <地址>` 或裸地址，无法解析为该子集邮箱的记录跳过。完整地址按大小写不敏感方式去重，输出保留第一次出现的原始大小写和先后次序。text 长度不超过 100000，不要求完整 RFC 邮件标准。

### 示例

```text
text = '"A;B" <a@x.com>; a@x.com; C(c;d)<c@y.org>'
emails(text) = ["a@x.com","c@y.org"]
text = 'a@x.com (outer(inner;note)); BAD; A@X.COM'
emails(text) = ["a@x.com"]
```

## 解题思路与参考答案

我会用状态机识别真正的记录边界，再提取、校验和去重邮箱。比如 `"A;B" <a@x.com>` 的分号属于显示名，`C(c;d)` 的分号属于注释，两处都不能切开。

## 题目

从日志文本里提取邮箱地址。记录之间用分号分隔，每条记录可能带显示名（可以加引号）和括号注释。要求单次扫描完成解析，并对地址去重。

> 来源：一亩三分地 Microsoft AI / Copilot 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。这是公司层面的通用题，不能因为相邻题卡就归到 LLM 团队。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

`text.split(";")` 无法区分这些分号，所以逐字符扫描时要记住三个状态：

- 是否在双引号里：引号内的分号和括号都是普通字符；
- 注释嵌套深度：遇到 `(` 加一、`)` 减一，深度大于 0 时内容全部丢弃；
- 上一个字符是不是反斜杠：被转义的字符按字面处理，不改变状态。

只有在引号外、注释外遇到分号，才算一条记录结束。切出记录以后，再从中取出地址并校验格式。

需要和面试官确认的规则有：转义怎么处理；非法记录是跳过还是报错；去重时大小写是否敏感、保留哪一种写法；输入结尾还有没闭合的引号或括号时怎么办。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `emails(text) -> list[str]`：按出现顺序返回不重复的邮箱地址。
- 记录以顶层分号分隔。显示名可以带双引号和反斜杠转义；括号注释可以嵌套，注释里的分号不切分记录。
- 只接受 ASCII 地址 `local@domain`：local 部分允许字母、数字和 `._+-`，domain 至少包含一个点。
- 按完整地址的 `casefold()` 去重，保留第一次出现时的大小写。格式不合法的记录跳过；输入结束时引号、注释或转义未闭合，抛 `ValueError`。
- 输入不超过 $10^5$ 个字符。这是约定好的子集，不是完整的 RFC 5322 解析器。

### 输入输出示例

```text
emails('"A;B" <a@x.com>; a@x.com; C(c;d)<c@y.org>')  -> ['a@x.com', 'c@y.org']
emails('a@x.com (outer (inner;)); BAD; A@X.COM')     -> ['a@x.com']
emails('a@x.com (')                                  -> ValueError
```

### 解题思路与正确性

实现分两步。`split_records` 是状态机：注释内容在扫描时直接丢掉，引号内容原样保留，所以显示名里的分号不会被误当成分隔符。切出的记录交给标准库 `parseaddr`，它能处理「显示名 <地址>」和裸地址两种写法，再用正则检查地址是否属于约定的子集。

去重只看地址本身，和显示名无关，所以 `"Alice" <a@x.com>` 与 `a@x.com` 算同一个地址。

### 完整参考实现（Python 3）

```python
import re
from email.utils import parseaddr

ADDRESS = re.compile(r"[A-Za-z0-9._+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+")


def split_records(text):
    """单次扫描：去掉括号注释（可嵌套），只在引号和注释之外的分号处切分记录。"""
    records = []
    current = []
    comment_depth = 0
    in_quotes = False
    escaped = False
    for char in text:
        if escaped:
            # 反斜杠后的字符按字面处理；注释里的内容一律丢弃
            if not comment_depth:
                current.append(char)
            escaped = False
            continue
        if char == "\\":
            if not comment_depth:
                current.append(char)
            escaped = True
            continue
        if comment_depth:
            if char == "(":
                comment_depth += 1
            elif char == ")":
                comment_depth -= 1
            continue
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == "(" and not in_quotes:
            comment_depth = 1
        elif char == ";" and not in_quotes:
            records.append("".join(current))
            current = []
        else:
            current.append(char)
    if comment_depth or in_quotes or escaped:
        raise ValueError("unclosed quote, comment or escape at end of input")
    records.append("".join(current))
    return records


def emails(text):
    """返回合法邮箱地址，按完整地址忽略大小写去重，保留第一次出现时的写法。"""
    seen = set()
    result = []
    for record in split_records(text):
        address = parseaddr(record)[1]  # 处理「显示名 <地址>」和裸地址两种写法
        if not ADDRESS.fullmatch(address):
            continue  # 非法记录直接跳过
        key = address.casefold()
        if key not in seen:
            seen.add(key)
            result.append(address)
    return result
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert emails('"A;B" <a@x.com>; a@x.com; C(c;d)<c@y.org>') == ["a@x.com", "c@y.org"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
# 引号里的分号、注释里的分号都不切分记录；重复地址只保留一次
assert emails('"A;B" <a@x.com>; a@x.com; C(c;d)<c@y.org>') == ["a@x.com", "c@y.org"]

# 嵌套注释被整体去掉；非法记录跳过；去重忽略大小写
assert emails("a@x.com (outer (inner;)); BAD; A@X.COM") == ["a@x.com"]

# 首次出现的大小写被保留
assert emails("Bob@Example.com; bob@example.com") == ["Bob@Example.com"]

# 未闭合的注释或引号报错
for bad in ["a@x.com (", '"a <a@x.com>']:
    try:
        emails(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"{bad!r} should raise ValueError")
```

### 复杂度与追问

设输入长度为 $L$、不同地址数为 $U$。扫描是 $O(L)$，正则对这个子集是线性匹配，去重集合占 $O(U)$ 空间。

- 国际化邮箱（非 ASCII 字符）、带引号的 local 部分（`"john doe"@x.com`）、只有域名的地址都不在这个约定里。现场如果要求支持，应该换成正式的邮箱语法解析器，而不是继续往正则里加规则。
- 输入是很大的日志流怎么办？状态机本来就是逐字符处理，可以改成按块读取，把状态（当前记录、引号、注释深度、转义）保留在块与块之间。
