---
id: meta-streaming-kmp-search
section: meta
order: 924
level: A
title: "Meta AI Coding 扩展：将 brute-force substring search 改成 streaming KMP"
quick: "我会把 chunk 当成传输方式，搜索状态始终只有已经匹配的 pattern prefix 长度和全局字符位置。这样 chunk 结束时不需要清空状态。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta AI Coding 扩展：将 brute-force substring search 改成 streaming KMP"
    url: "https://aceoffer.app/interviews/ai-coding"
    type: secondary
---

## 题目描述

来源：AceOffer 的 Meta AI coding 综述提到优化 brute-force string search。下面扩展为 chunked input，streaming 接口由手册设定。

### 输入、接口与规则

实现 `find_matches(chunks, pattern) -> list[int]`。chunks 是只能遍历一次的 string iterable，可以包含空 chunk；pattern 是非空字符串。把 chunks 逻辑拼接成完整文本，返回 pattern 所有出现位置的 0-based 字符下标，允许 overlaps，顺序升序。空 pattern 抛 ValueError，空文本返回空列表。

不能先 join 全部 chunks，也不能在每个 chunk 上独立调用搜索，因为匹配可能跨多个 chunks。输入按 Python Unicode code points 计数，pattern 最长 100000。除返回结果外，额外内存应为 `O(len(pattern))`；目标时间为文本总长度与 pattern 长度之和的线性量级。

### 输入输出示例

```text
chunks=iter(["ab","a","ba"]), pattern="aba" -> [0,2]。
chunks=["a","","aa"], pattern="aa" -> [0,1]。
chunks=[], pattern="x" -> []。
```

## 回答思路

> **Situation / Task：** 匹配可能跨 chunk，且 overlaps 也要返回。  
> **Approach / Why：** KMP prefix table 记录失败后能保留的匹配长度，跨 chunks 保留 matched。  
> **Result / Check：** 在每一种切分下与完整文本的 brute-force oracle 比较。

## 解题思路与参考答案

我会把 chunk 当成传输方式，搜索状态始终只有已经匹配的 pattern prefix 长度和全局字符位置。这样 chunk 结束时不需要清空状态。

遇到不匹配时，用 prefix table 回退，避免重新读取文本。找到完整匹配后也要按 prefix table 回退，不能直接归零，否则像 aaa 中找 aa 会漏掉 overlap。

### 完整参考实现

```python
def find_matches(chunks, pattern):
    if not pattern:
        raise ValueError('empty pattern')
    prefix = [0] * len(pattern)
    matched = 0
    for i in range(1, len(pattern)):
        while matched and pattern[i] != pattern[matched]:
            matched = prefix[matched - 1]
        if pattern[i] == pattern[matched]:
            matched += 1
        prefix[i] = matched
    result = []
    matched = 0
    pos = 0
    for chunk in chunks:
        for char in chunk:
            while matched and char != pattern[matched]:
                matched = prefix[matched - 1]
            if char == pattern[matched]:
                matched += 1
            if matched == len(pattern):
                result.append(pos - len(pattern) + 1)
                matched = prefix[matched - 1]
            pos += 1
    return result
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert find_matches(iter(['ab', 'a', 'ba']), 'aba') == [0, 2]
assert find_matches(['a', '', 'aa'], 'aa') == [0, 1]
from itertools import product

for n in range(7):
    for chars in product('ab', repeat=n):
        text = ''.join(chars)
        for pattern in ['a', 'b', 'aa', 'aba', 'bab']:
            expected = [i for i in range(n) if text.startswith(pattern, i)]
            for cut in range(n + 1):
                assert (
                    find_matches(iter([text[:cut], '', text[cut:]]), pattern)
                    == expected
                )
print('streaming KMP tests passed')
```

## 复杂度与追问

文本总长 T、pattern 长 M，时间 `O(T+M)`，除输出外空间 `O(M)`。追问 byte streams 时，先用 incremental decoder 保证 code point 完整，再交给本模块。
