---
id: drustz-083a6b4bdd82f25d7e
section: openai
order: 160
level: A
title: Valid Parentheses with Redundancy Check
quick: >-
  original-structured-preparation-guide · Valid Parentheses with Redundancy
  Check
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/663d5171-6dc3-42c3-bc4e-5d7e1cdf504c
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 有效且无冗余的括号

## 题目要做什么

给定一个算术表达式，判断：

1. 所有括号是否正确配对；
2. 是否存在冗余括号。

这里采用常见面试定义：如果一对括号内部在**当前层**没有二元运算符，那么这对括号是冗余的。例如 `((a-d) + ((b+c)))` 中，`(b+c)` 外层的括号没有增加任何运算作用，所以结果应为 `False`。

## 栈解法

从左到右扫描：

- 普通字符和左括号入栈；
- 遇到右括号时，一直弹栈到最近的左括号；
- 如果找不到左括号，说明括号不匹配；
- 如果弹出的这一层没有运算符，说明当前括号冗余。

```python
def valid_without_redundancy(expr: str) -> bool:
    stack: list[str] = []
    operators = set("+-*/")

    for ch in expr:
        if ch != ")":
            stack.append(ch)
            continue

        has_operator = False
        while stack and stack[-1] != "(":
            has_operator |= stack.pop() in operators

        if not stack:  # 没有与当前右括号匹配的左括号
            return False

        stack.pop()  # 弹出左括号
        if not has_operator:  # 当前层没有二元运算符
            return False

    return "(" not in stack
```



## 复杂度

每个字符最多入栈、出栈一次，因此时间为 `O(n)`，空间为 `O(n)`。

## 边界与定义差异

- `()`、`(a)` 和多余的左右括号；
- 完全没有括号的表达式通常视为合法且无冗余；
- 函数调用 `f(x)`、数组下标、单目负号和完整运算符优先级不适合这个简化规则；
- 如果题目要求判断“删除括号后语义是否变化”，应使用 tokenizer 或 AST，而不是只看字符栈。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/663d5171-6dc3-42c3-bc4e-5d7e1cdf504c)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
