---
id: stripe-csv-validate
section: stripe
order: 2
level: S
title: Stripe：多行 CSV 做数据集校验，店面三 part
quick: >-
  先写一个只管切行切列的 reader，再每个 part 加一条规则：逐行拒绝空字段，按 banned word 滤掉，用 stop word 对其中两列做
  tokenize。输入是一整段多行 CSV 字符串。题干很长，先和面试官整理成能测试的规则，再写实现。
tags:
  - Stripe
  - Coding
  - Parsing
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22T00:00:00.000Z
sources:
  - title: Stripe L3 全套挂经，2026 年 3 月 senior 店面
    url: 'https://www.1point3acres.com/bbs/thread-1171504-1-1.html'
    type: candidate-first-hand
  - title: Stripe Software Engineer Interview Guide，CSV 另一变体
    url: 'https://www.tryexponent.com/guides/stripe-software-engineer-interview'
    type: secondary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现数据集校验的 CSV 读取核心：把整段 CSV 字符串解析为表头和数据行，并保留带引号字段中的逗号。公开面经提及空字段检查、banned word 和两列 tokenize，但没有留下后两部分完整语义；本页可运行主练习仅覆盖已有明确实现的 reader。

### 输入与接口

实现 rows(text)。text 为合法 CSV 语法的非空字符串，第一条记录是表头；表头名唯一且非空，原样保留。合法练习输入中的每条数据记录与表头列数一致，且字段去首尾空白后非空；允许带引号的逗号与标准 CSV 转义。

### 输出与约束

返回 (header,out)：header 为表头字符串列表；out 按数据记录输入顺序返回字典列表，键为对应表头，值为字段去首尾空白后的字符串。只含表头时返回空 out，不把字段自动转换成数字或布尔值；不修改表头大小写。

需使用标准 CSV 字段语义，不能简单按逗号 split。空字段拒绝、banned word 过滤与去 stop words 分词是后续需求讨论，正常输入测例不要求异常处理；后两项必须另行明确列名、大小写、word boundaries 及输出格式后再实现，不能把推测规则混入 rows 默认行为。

### 示例

```text
输入（实际换行）：
name,note
 Alice ,"x,y"

rows(text) -> (["name","note"],[{"name":"Alice","note":"x,y"}])
rows("name,note\n" 中含实际换行) -> (["name","note"],[])
```

## 解题思路与参考答案

这题我会先写一个只管切行、切列的 reader，然后每个 part 只加一条规则：第一 part 拒绝空字段，第二 part 滤掉 banned word，第三 part 用 stop word 对面试官点名的两列 tokenize。题干很长，动手前先和面试官把规则收成能测的几条。

帖子是 2026 年 3 月的 Stripe senior SDE，海投。2 月的店面题是 Dataset validation，作者用 Java，输入是一整段多行 CSV 字符串，用 `BufferedReader` 一行行读，三 part 都写完了。Onsite 另有系统设计，见 `stripe-onsite-debug`。帖子里能核对的规则就三条：逐行读，空字符串不合法；有 banned word，要过滤；给了 stop words，要对所有行里的某两列 tokenize。帖子在第三条这里被截断，两列怎么拼、比例怎么算，原文没留下来。这半句别自己补全，第三 part 以面试官提炼的规则为准。作者说题干长到读不完，是面试官帮着收成这三问的。

我会先把 CSV 读取封装成一个函数，让后续 banned word 和 tokenize 规则能复用同一批行。下面这版同时检查列数和空字段：

```python
import csv
import io


def rows(text):
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    out = []
    for line_no, cols in enumerate(reader, start=2):
        if len(cols) != len(header) or any(c.strip() == "" for c in cols):
            raise ValueError(f"empty field at line {line_no}")
        out.append(dict(zip(header, (c.strip() for c in cols))))
    return header, out
```

第二 part 用集合查 banned word。帖子没说是整格相等还是子串，我会问。整格相等就是 `value in banned`；子串的话还要定大小写和 word boundaries。

第三 part 只对面试官点名的两列切词，stop word 先放进 set。切完如果要求「两列之间有某种重合」，就用集合交集，别双重循环扫词。

用 Java 写的话别 `split(",")`，字段里可以有引号和逗号。`BufferedReader` 只负责行，列交给 CSV parser。

Exponent 的 2026 指南里有另一位 SWE 的 CSV，结构和这篇不完全一样：表头不能缺，连续逗号当空字段，某列的值必须在另一列出现过，字段之间的循环依赖要当成图来检测。拿它当长题的后续 part 来练可以，别当成 2026 年 3 月这帖的第三问。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

带引号的逗号应保留在一个字段中，字段两侧空白应去掉；空字段必须报错，并保留输入行号便于定位。

```python
header, result = rows('name,note\n Alice ,"x,y"\n')
assert header == ["name", "note"]
assert result == [{"name": "Alice", "note": "x,y"}]
try:
    rows("name,note\nAlice,\n")
except ValueError as error:
    assert "line 2" in str(error)
else:
    raise AssertionError("empty field must fail")
print("simple tests passed")
```

## 追问

**循环依赖那问怎么答？**
把列依赖画成有向边，DFS 三色标记，灰节点被再次访问就是有环。那是另一则报告里的 part，这帖的店面没有写到这一问。

**时间不够，第三 part 写不完怎么办？**
先保证前两 part 有测试、名字读得懂。第三 part 规则没听清就开写，时间会耗在错误的 tokenize 上。作者三 part 都写完了，onsite 后照样挂了。
