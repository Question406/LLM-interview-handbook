---
id: lc-150-evaluate-reverse-polish-notation
section: stack
order: 4
level: A
title: LC 150 · 逆波兰表达式求值
quick: "数字入栈，遇运算符先弹出右操作数，再弹左操作数，计算后压回结果。减法和除法不能颠倒顺序。Python 的 // 向负无穷取整，题目要求向零截断，示例用 int(a / b)。"
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

## 题意

给定逆波兰（后缀）表达式的 token 列表，计算结果。运算符为 `+ - * /`，操作数为整数。除法向零截断。

## 思路

栈。token 是数字就入栈；是运算符则先弹右操作数 $b$、再弹左操作数 $a$，算 $a\oplus b$ 压回。后缀保证扫描到运算符时栈里已有足够操作数。最后栈里只剩结果。

Python 的 `//` 是向负无穷取整：`(-7) // 3 == -3`，但这题要 `-2`。必须 `int(a / b)`。弹出顺序是右再左，减法和除法不可交换。

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

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。每个 token 处理一次。

## 边界

- 单数字：不进运算符分支，栈里只剩它。
- 负数 token `"-2"`：`t not in "+-*/"`，整段 `int(t)`，不是减号。
- 除法向零：`7 / -3 = -2`，必须 `int(a / b)`，不能用 `//`。
- 减、除不可交换：先弹右操作数 $b$ 再弹左操作数 $a$。

## 追问

- **中缀带括号怎么算（LC 224）？** 后缀已经排好优先级；中缀要自己处理 `+ -` 与括号。维护 `res`、当前 `num`、当前 `sign`，遇 `(` 把外层 `res` 和 `sign` 压栈并清零，遇 `)` 先收尾再乘栈顶符号、加回外层 `res`。没有乘除时一层符号栈就够。时间 $O(n)$。也可以先用调度场算法转后缀再走这题。独立卡见 `lc-224-basic-calculator`。

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

- **表达式可能非法？** 这题保证合法。若要校验：遇运算符时栈深度必须 $\ge 2$，否则缺操作数；除数为 $0$ 直接失败；扫完栈里必须恰好一个数，多了说明操作符不够。token 既不是整数也不是四则运算也是非法。中缀还要括号匹配，可复用 `lc-20-valid-parentheses`。校验可以和求值同时做，不必先扫一遍。

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
