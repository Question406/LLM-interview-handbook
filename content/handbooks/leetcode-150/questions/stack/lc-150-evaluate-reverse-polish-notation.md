---
id: lc-150-evaluate-reverse-polish-notation
section: stack
order: 4
level: A
title: LC 150 · 逆波兰表达式求值
quick: "用栈：数字入栈，遇到运算符先弹右操作数、再弹左操作数，算完把结果压回，减法和除法的顺序不能弄反。题目要求除法向零截断，Python 的 // 是向负无穷取整，所以示例用 int(a / b)。"
tags:
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 150. 逆波兰表达式求值
    url: https://leetcode.cn/problems/evaluate-reverse-polish-notation/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一个合法的逆波兰表达式，即运算符写在两个操作数或子表达式之后的后缀表达式，计算其整数结果。支持加、减、乘、除；减法与除法保留两个操作数的原先左右顺序，整数除法向 0 截断。

### 输入与输出

实现 `evalRPN(tokens) -> int`。tokens 中的数字以字符串给出，可以为负数；运算符是 "+"、"-"、"*"、"/"。返回整个表达式的值。

### 约束与约定

- `1 <= len(tokens) <= 10000`。
- 数字 token 的值在 `[-200,200]`。
- 输入保证是完整合法表达式且不会除以 0；所有中间值与最终答案都能用 32 位有符号整数表示。

### 示例

```text
输入：tokens = ["2","1","+","3","*"]
输出：9
```

示例表达的是 (2+1)*3，结果为 9；例如 -7 除以 3 应得到 -2 而不是 -3。

[官方原题与完整题面](https://leetcode.com/problems/evaluate-reverse-polish-notation/description/)。

## 解题思路与参考答案

## 题意

给定逆波兰（后缀）表达式的 token 列表，计算结果。运算符为 `+ - * /`，操作数为整数。除法向零截断。

## 思路

后缀表达式天然适合用栈，因为扫到运算符时，它要的两个操作数一定已经在栈里了。token 是数字就入栈；是运算符就先弹出右操作数 $b$、再弹出左操作数 $a$，算出 $a\oplus b$ 压回去。扫完以后栈里只剩结果。

拿 `["2","1","+","3","*"]` 走一遍。$2$、$1$ 入栈，遇到 `+` 弹出 $1$ 和 $2$，压回 $3$；$3$ 入栈，遇到 `*` 弹出两个 $3$，压回 $9$，答案是 $9$。

有两个地方我会主动说。弹出顺序是先右后左，减法和除法不可交换，顺序弄反答案就错。另外 Python 的 `//` 向负无穷取整，`(-7) // 3 == -3`，这题要的是 `-2`，所以必须写 `int(a / b)`。

## 参考代码

```python
from typing import List


def evalRPN(tokens: List[str]) -> int:
    st = []
    for t in tokens:
        if t in "+-*/":
            b, a = st.pop(), st.pop()
            if t == "+":
                st.append(a + b)
            elif t == "-":
                st.append(a - b)
            elif t == "*":
                st.append(a * b)
            else:
                st.append(int(a / b))
        else:
            st.append(int(t))
    return st[-1]


if __name__ == "__main__":
    assert evalRPN(["2", "1", "+", "3", "*"]) == 9
    assert evalRPN(["4", "13", "5", "/", "+"]) == 6
    assert evalRPN(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22
    assert evalRPN(["4", "-2", "/", "2", "+"]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert evalRPN(["2", "1", "+", "3", "*"]) == 9
assert evalRPN(["4", "13", "5", "/", "+"]) == 6
assert evalRPN(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。每个 token 处理一次。

## 边界

只有一个数字时不进运算符分支，栈里就剩它。

负数 token `"-2"` 不满足 `t in "+-*/"`，会整段走 `int(t)`，不会被当成减号。

除法要向零截断，`7 / -3 = -2`，所以用 `int(a / b)`，写 `//` 会得到 $-3$。

减、除不可交换，所以先弹右操作数 $b$，再弹左操作数 $a$。

## 追问

**中缀带括号怎么算（LC 224）？**
后缀已经把优先级排好了，中缀得自己处理 `+ -` 和括号。维护 `res`、当前 `num`、当前 `sign`，遇到 `(` 把外层的 `res` 和 `sign` 压栈并清零，遇到 `)` 先收尾，再乘栈顶符号、加回外层 `res`。没有乘除时一层符号栈就够，时间 $O(n)$。也可以先用调度场算法转成后缀，再走这题。独立卡见 `lc-224-basic-calculator`。

```python
def calculate(s):
    st, res, num, sign = [], 0, 0, 1
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in "+-":
            res += sign * num
            num = 0
            sign = 1 if ch == "+" else -1
        elif ch == "(":
            st.append(res)
            st.append(sign)
            res, sign = 0, 1
        elif ch == ")":
            res += sign * num
            num = 0
            res = res * st.pop() + st.pop()
    return res + sign * num
```

**表达式可能不合法呢？**
这题保证合法。真要校验，可以和求值同时做，不用先扫一遍。遇到运算符时栈深度必须 $\ge 2$，否则缺操作数；除数为 $0$ 直接失败；扫完栈里必须恰好一个数，多了说明运算符不够；token 既不是整数也不是四则运算符，也算非法。中缀还要检查括号匹配，可以复用 `lc-20-valid-parentheses`。

```python
def evalRPNChecked(tokens):
    st = []
    for t in tokens:
        if t in "+-*/":
            if len(st) < 2:
                raise ValueError("underflow")
            b, a = st.pop(), st.pop()
            if t == "/" and b == 0:
                raise ValueError("div0")
            st.append({"+" : a + b, "-": a - b, "*": a * b, "/": int(a / b)}[t])
        else:
            st.append(int(t))
    if len(st) != 1:
        raise ValueError("leftover")
    return st[-1]
```
