---
id: drustz-25498ccba84bdfba7b
section: anthropic
order: 80
level: A
title: Token Usage Calculation
quick: original-structured-preparation-guide · Token Usage Calculation
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/1f861fb5-8d4f-46c0-b1f4-d2599788cc8a
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Token Usage Calculation（Token 用量估算）

> 公开题面说明“约每 4 个字符算一个 token”，但公开样例与常见取整方式对不上。下面同时展示两种合理口径，不把其中一种伪装成已确认规则。

## 题目要做什么

读取一段可能包含多行的文本，根据“约 4 个字符对应 1 个 token”的简化规则，返回估算 token 数。这里不要求调用真实 tokenizer。

## 两种可能的实现

如果不足 4 个字符也算一个 token，使用向上取整：

```python
def estimate_tokens(text: str) -> int:
    return (len(text) + 3) // 4
```



如果只统计完整的四字符组，则使用：

```python
def estimate_complete_groups(text: str) -> int:
    return len(text) // 4
```



面试时应先确认：尾部不足 4 个字符如何处理、空格和换行是否计入、字符是 Unicode code point 还是字节。

## 复杂度

文本已在内存中时，Python 的 `len()` 为 `O(1)`；如果把读取输入算进去，总时间为 `O(n)`、空间为 `O(n)`。分块累计字符数可把额外空间降到 `O(1)`。

## 公开样例异常

公开样例正文按常见字符统计约为 51～52 个字符，无论向下还是向上除以 4，都得不到页面给出的 7。因此不能根据该样例反推出可靠取整规则。

## 边界

空文本、1～3 个字符、末尾换行、Windows CRLF、emoji 和 Unicode 组合字符。这个算法只是粗略估算，不等于 Claude 或其他模型的真实 tokenizer。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1f861fb5-8d4f-46c0-b1f4-d2599788cc8a)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
