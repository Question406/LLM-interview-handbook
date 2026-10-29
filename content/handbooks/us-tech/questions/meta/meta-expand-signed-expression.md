---
id: meta-expand-signed-expression
section: meta
order: 926
level: A
title: "Meta：去掉 plus/minus expression 的 parentheses，合并变量 coefficients"
quick: "这里没有乘法，因此每个变量最后只会贡献一个正负整数。我会维护当前组继承的 sign，再累计变量前连续的 plus/minus signs。"
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
  - title: "公开来源：Meta：去掉 plus/minus expression 的 parentheses，合并变量 coefficients"
    url: "https://landthelab.com/companies/meta"
    type: secondary
---

## 题目描述

来源：Land the Lab 的 Meta 目录列出 remove parentheses from a plus-minus expression。下面用形式化 grammar 和 coefficient map 规定练习接口。

### 输入、接口与规则

实现 `expand_expression(text) -> dict[str,int]`。输入保证满足 grammar：expr := term ((+|-) term)*；term := (+|-)* atom；atom := 一个 lowercase ASCII 字母，或 (expr)。允许任意 ASCII 空白；expr 非空，不含乘法、数字或空括号。总长度不超过 100000，nesting depth 可能很深。

返回每个变量在展开和合并后的整数 coefficient，移除 coefficient=0 的变量；dict 顺序不参与评分。不使用 eval 或 symbolic algebra 库，不修改输入。需要正确处理 subtraction of a group、嵌套 parentheses 与多个 unary signs；避免依赖 Python recursion limit。

### 输入输出示例

```text
输入 "a-(b-c)+a" -> {"a":2,"b":-1,"c":1}。
输入 "a-(a)" -> {}。
输入 "--a-(-b+c)" -> {"a":1,"b":1,"c":-1}。
```

## 回答思路

> **Situation / Task：** 括号前的减号会改变整组符号；目标是 coefficient map。  
> **Approach / Why：** Stack 保存当前组的累计 sign，每个变量的贡献是 group sign 乘局部 sign。  
> **Result / Check：** 检查双重负号、深 nesting 与抵消为零。

## 解题思路与参考答案

这里没有乘法，因此每个变量最后只会贡献一个正负整数。我会维护当前组继承的 sign，再累计变量前连续的 plus/minus signs。

遇到左括号，把 group sign 乘局部 sign 压入 stack；遇到右括号恢复上一层。这样 a-(b-c) 中 b 贡献 -1、c 贡献 +1，深 nesting 也不需要递归。

### 完整参考实现

```python
from collections import Counter


def expand_expression(text):
    stack = [1]
    local = 1
    result = Counter()
    for char in text:
        if char.isspace():
            continue
        if char == '+':
            continue
        if char == '-':
            local = -local
        elif char == '(':
            stack.append(stack[-1] * local)
            local = 1
        elif char == ')':
            stack.pop()
            local = 1
        else:
            result[char] += stack[-1] * local
            local = 1
    return {char: value for char, value in result.items() if value}
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert expand_expression('a-(b-c)+a') == {'a': 2, 'b': -1, 'c': 1}
assert expand_expression('a-(a)') == {}
assert expand_expression('--a-(-b+c)') == {'a': 1, 'b': 1, 'c': -1}
assert expand_expression('a--b') == {'a': 1, 'b': 1}
assert expand_expression('-(' * 10000 + 'a' + ')' * 10000) == {'a': 1}
from random import Random

rng = Random(10)


def make(depth):
    if depth == 0:
        return rng.choice('abc')
    return '(' + make(depth - 1) + rng.choice('+-') + make(depth - 1) + ')'


for _ in range(100):
    text = make(4)
    coefficients = expand_expression(text)
    values = {c: rng.randint(-9, 9) for c in 'abc'}
    assert sum(coefficients.get(c, 0) * values[c] for c in values) == eval(
        text, {'__builtins__': {}}, values
    )
print('expression tests passed')
```

## 复杂度与追问

输入长度 N，时间 `O(N)`，空间 `O(depth+26)`。输入保证合法；若要校验 grammar，需要另外维护“期待 atom / operator”的 parser 状态，不能只加一个括号计数。
