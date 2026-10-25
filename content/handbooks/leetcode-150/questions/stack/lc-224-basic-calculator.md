---
id: lc-224-basic-calculator
section: stack
order: 5
level: A
title: LC 224 · 基本计算器
quick: "一层括号相当于给里面整段乘一个符号，所以用栈保存外层的结果和符号。扫数字累加，遇 `+`/`-` 把 `sign * num` 加进结果并换符号；`(` 把当前结果与 `sign` 入栈清零，`)` 出栈把括号值乘符号再加回外层。"
tags:
  - Stack
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 224. 基本计算器
    url: https://leetcode.cn/problems/basic-calculator/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定表示合法算术表达式的字符串 s，计算其整数结果。表达式由十进制整数、加号、减号、左右括号和空格构成，括号可以嵌套；本题没有乘法或除法。允许一元负号，例如 `-1` 或 `-(2+3)`，不使用一元正号。

### 接口与输出

实现 `calculate(s: str) -> int`。应实现表达式求值，不调用 eval 这类直接执行表达式字符串的内置工具。

### 合法输入与约束

`1 <= len(s) <= 300000`。输入表达式合法，没有两个连续运算符；每个数和计算过程中的结果都在 32 位有符号整数范围内。空格不改变计算结果。

### 示例

```text
输入：s = "1 + 1"
输出：2
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/basic-calculator/description/)。

## 解题思路与参考答案

## 题意

计算只含非负整数、`+`、`-`、括号与空格的表达式。没有乘除。括号可嵌套。

## 思路

没有乘除，难点只在括号。我会把一层括号看成给里面整段乘一个符号，进括号前把外层的状态存进栈里。需要维护的是 `res`、当前 `num`、当前 `sign`（$+1$ 或 $-1$）。

扫到数字就 `num = num * 10 + d`，多位数这样拼起来。遇到 `+` 或 `-`，先把 `sign * num` 加进 `res`，`num` 清零，`sign` 换成新符号。遇到 `(`，把外层的 `res` 和 `sign` 压栈，然后 `res=0`、`sign=+1`，开始算括号里的子表达式。遇到 `)`，先把当前 `num` 收尾，再 `res *= 栈顶符号`，加上栈里保存的外层 `res`。空格直接跳过，结束时别忘了加上最后一段 `sign * num`。

拿 `1-(2+3)` 走一下。读完 `1`，遇到 `-` 时 `res=1`、`sign=-1`。遇到 `(`，把外层的 $1$ 和符号 $-1$ 压栈，括号里从零开始算出 $5$。遇到 `)`，$5$ 乘上 $-1$，再加回外层的 $1$，得到 $-4$。

## 参考代码

```python
def calculate(s: str) -> int:
    st = []
    res = num = 0
    sign = 1
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
            res = 0
            sign = 1
        elif ch == ")":
            res += sign * num
            num = 0
            res *= st.pop()
            res += st.pop()
    return res + sign * num


if __name__ == "__main__":
    assert calculate("1 + 1") == 2
    assert calculate(" 2-1 + 2 ") == 3
    assert calculate("(1+(4+5+2)-3)+(6+8)") == 23
    assert calculate("1-(     -2)") == 3
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert calculate("1 + 1") == 2
assert calculate(" 2-1 + 2 ") == 3
assert calculate("(1+(4+5+2)-3)+(6+8)") == 23
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（括号嵌套深度）。每个字符处理一次。

## 边界

前导空格、数字之间的空格都不是目标字符，直接跳过。`1-( -2)` 里括号内的负号按减号处理，空格不影响。

最外层没有括号时，栈一直是空的，只靠 `res/sign/num`。结果为负也没问题，`sign` 会一路乘进去。

多位数要用 `num = num * 10 + d` 拼，按个位相加就错了。

## 追问

**加上乘除（LC 227）呢？**
没有括号时，用栈存「当前项」。遇到 `+`/`-` 把 `±num` 压栈；遇到 `*`/`/` 立刻和栈顶结算，除法向零截断用 `int(a / b)`；扫完 `sum(stack)`。优先级就靠「乘除立刻算、加减先搁着」。空格跳过，最后一个数要用一个哨兵运算符冲出来。再加括号就是 LC 772：遇到 `(` 递归（或者压一套 `st/op/num`），遇到 `)` 返回当前段的和。这个不必另开独立卡，先把 227 写熟。

```python
def calculate227(s):
    st, num, op = [], 0, "+"
    for i, ch in enumerate(s + "+"):
        if ch == " ":
            continue
        if ch.isdigit():
            num = num * 10 + int(ch)
            continue
        if op == "+":
            st.append(num)
        elif op == "-":
            st.append(-num)
        elif op == "*":
            st.append(st.pop() * num)
        else:
            st.append(int(st.pop() / num))
        op, num = ch, 0
    return sum(st)


def calculate772(s):
    def expr(it):
        st, num, op = [], 0, "+"
        while True:
            c = next(it, ")")
            if c == " ":
                continue
            if c.isdigit():
                num = 10 * num + int(c)
                continue
            if c == "(":
                num = expr(it)
                continue
            if op == "+":
                st.append(num)
            elif op == "-":
                st.append(-num)
            elif op == "*":
                st.append(st.pop() * num)
            else:
                st.append(int(st.pop() / num))
            if c == ")":
                return sum(st)
            op, num = c, 0
    return expr(iter(s))
```

**一元负号不带括号怎么办？**
比如开头的 `-1+2`，或者 `1+-2`。`-` 出现在表达式开头、`(` 之后或另一个运算符之后时，它表示正负号，二元减法的规则用不上。这时令 `sign=-1` 作用到下一个数（或括号段），不要先把当前 `res` 结算掉。也可以在这些位置补一个 `0`，把 `-2` 当成 `0-2`。这题的负号都用括号包着（`1-(-2)`），按二元减就能过，所以我会先问清楚一元负号会不会出现。

```python
def calculateUnary(s):
    s = s.replace(" ", "")
    st, res, num, sign = [], 0, 0, 1
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in "+-":
            unary = i == 0 or s[i - 1] in "+-("
            if unary:
                sign *= 1 if ch == "+" else -1
            else:
                res += sign * num
                num = 0
                sign = 1 if ch == "+" else -1
        elif ch == "(":
            st.append((res, sign))
            res, num, sign = 0, 0, 1
        elif ch == ")":
            res += sign * num
            num = 0
            prev_res, prev_sign = st.pop()
            res = prev_res + prev_sign * res
            sign = 1
        i += 1
    return res + sign * num
```
