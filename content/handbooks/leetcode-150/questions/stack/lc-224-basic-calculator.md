---
id: lc-224-basic-calculator
section: stack
order: 5
level: A
title: LC 224 · 基本计算器
quick: >-
  扫数字累加，遇 `+`/`-` 把 `sign * num` 加入结果并改符号。`(` 把当前结果与 `sign` 入栈清零，`)` 出栈把括号值乘符号再累加。
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

## 题意

计算只含非负整数、`+`、`-`、括号与空格的表达式。没有乘除。括号可嵌套。

## 思路

一层括号相当于给里面整段乘一个符号。维护 `res`、当前 `num`、当前 `sign`（$+1$ 或 $-1$），以及栈：

- 数字：`num = num * 10 + d`。
- `+` / `-`：先把 `sign * num` 加进 `res`，`num` 清零，`sign` 改成新符号。
- `(`：把外层 `res` 与 `sign` 压栈，然后 `res=0`、`sign=+1`，开始算子表达式。
- `)`：先收尾当前 `num`，再 `res *= 栈顶符号`，加上栈里保存的外层 `res`。

空格跳过。结束时别忘了加上最后一段 `sign * num`。`1-(2+3)` 在 `(` 处记下外层 $1$ 和符号 $-1$。

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

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（括号嵌套深度）。每个字符处理一次。

## 边界

- 前导空格、数字间空格：非目标字符跳过。
- `1-( -2)`：负号在括号里当减号，空格不影响。
- 最外层无括号：栈空，只靠 `res/sign/num`。
- 结果为负：`sign` 一路乘进去。
- 连续数字多位：`num = num * 10 + d`，不要按个位加。

## 追问

- **加上乘除（LC 227）？** 没有括号时，用栈存「当前项」。遇 `+`/`-` 把 `±num` 压栈；遇 `*`/`/` 立刻与栈顶结算（除法向零：`int(a / b)`）。扫完 `sum(stack)`。优先级靠「乘除立即算、加减先搁着」。空格跳过，最后一个数要用哨兵运算符冲刷。再加括号是 LC 772：遇到 `(` 递归（或压一套 `st/op/num`），遇到 `)` 返回当前段的和。独立卡不必另开，227 先写熟。

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

- **一元负号不带括号？** 如开头的 `-1+2` 或 `1+-2`。若 `-` 出现在表达式开头、`(` 之后或另一个运算符之后，它是符号不是二元减：令 `sign=-1` 应用到下一个数（或括号段），不要先把当前 `res` 结算掉。也可以在这些位置补一个 `0`，把 `-2` 当成 `0-2`。这题用括号包住负号（`1-(-2)`），所以按二元减就能过。我会先问清一元负号是否出现。

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
