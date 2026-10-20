---
id: stripe-csv-validate
section: stripe
order: 2
level: S
title: Stripe：多行 CSV 做数据集校验，店面三 part
quick: >-
  输入是一整段多行 CSV 字符串。先逐行拒绝空字段，再按 banned word 滤掉，再用 stop word 对其中两列做 tokenize。
  题干很长，先和面试官整理成能测试的规则，再写实现。
tags:
  - Stripe
  - Coding
  - Parsing
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Stripe L3 全套挂经，2026 年 3 月 senior 店面
    url: https://www.1point3acres.com/bbs/thread-1171504-1-1.html
    type: candidate-first-hand
  - title: Stripe Software Engineer Interview Guide，CSV 另一变体
    url: https://www.tryexponent.com/guides/stripe-software-engineer-interview
    type: secondary
---

## 真题记录

2026 年 3 月，Stripe senior SDE，海投。2 月店面是 Dataset validation。作者用 Java，输入是多行 CSV 字符串，用 `BufferedReader` 一行行读。三 part 都写完了。Onsite 另有系统设计，见 `stripe-onsite-debug`。

能从帖子里核对的规则：

1. 逐行读，空字符串不合法。
2. 有 banned word，要过滤。
3. 给了 stop words，要对所有行里的某两列 tokenize。帖子在这里被截断，两列怎么拼、比例怎么算，原文没留下来。

不要把截断的半句补全。现场第三 part 以面试官提炼的规则为准。作者说题干长到读不完，是面试官帮着收成这三问。

## 另一份公开变体

Exponent 的 2026 指南写了另一位 SWE 的 CSV，结构和这篇不完全一样：表头不能缺、连续逗号当空字段、某列的值必须在另一列出现过、字段之间的循环依赖要当图检测。当成长题的后续 part 来练可以，不要当成 2026 年 3 月这帖的第三问。

## 我会怎么写

先写一个只负责切行、切列的 reader，后面每 part 只加一条规则，不把校验揉进解析。

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

Part 2 用集合查 banned word。帖子没说是整格相等还是子串，我会问。整格相等就 `value in banned`。子串就要定大小写和单词边界。

Part 3 只对面试官点名的两列切词。stop word 先放进 set。切完如果要求「两列之间有某种重合」，用集合交集，不要双重循环扫词。

Java 里不要 `split(",")`。字段里可以有引号和逗号，`BufferedReader` 只负责行，列交给 CSV parser。

## 追问

**循环依赖那问怎么答？** 那是另一则报告里的 part。把列依赖画成有向边，DFS 三色标记，灰节点再次访问就是环。这帖的店面没有写到这一问。

**时间不够写不完第三 part？** 作者写完三 part 仍然在 onsite 后挂了。店面先保证前两 part 有测试、名字读得懂。第三 part 规则没听清就开写，会在错误的 tokenize 上耗完时间。
