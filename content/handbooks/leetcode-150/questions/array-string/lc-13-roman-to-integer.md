---
id: lc-13-roman-to-integer
section: array-string
order: 17
level: S
title: LC 13 · 罗马数字转整数
quick: "建一张符号表，从左往右扫：`s[i]` 的值 $\\lt$ `s[i+1]` 就减去当前值，否则加上。小符号写在大符号左边表示减，所以比较相邻值就够，不用特判六种组合。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Hash
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 13. 罗马数字转整数
    url: https://leetcode.cn/problems/roman-to-integer/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一个合法的罗马数字字符串，返回它表示的十进制整数。罗马数字使用 I、V、X、L、C、D、M，分别表示 1、5、10、50、100、500、1000。通常较大的符号在前；只有 IV、IX、XL、XC、CD、CM 这六种相邻组合使用减法含义，分别表示 4、9、40、90、400、900。

### 输入与输出

实现 `romanToInt(s: str) -> int`。`s` 是罗马数字表示，返回对应整数；输入保证符合罗马数字规则，不需要判断表示是否合法。

### 约束

- `1 <= len(s) <= 15`。
- 字符仅为 `I V X L C D M`，数值范围为 1 到 3999。

### 示例

```text
输入：s = "III"
输出：3
```

三个 I 表示三个 1，因此结果为 3；例如合法表示 `MCMXCIV` 对应 1994。

## 解题思路与参考答案

## 题意

给你一个合法罗马数字字符串 `s`，转成整数。减法对只有 `IV`、`IX`、`XL`、`XC`、`CD`、`CM`。

## 思路

我会建一张符号表，从左往右扫，只比较相邻两位。罗马数字里小的符号写在大的左边表示减，所以扫到位置 $i$ 时，它比右边小就减 `val(s[i])`，否则就加，最后一位只能加。这样不用特判六种减法组合。

符号表先列出来：`I=1,V=5,X=10,L=50,C=100,D=500,M=1000`。拿 `MCMXCIV` 走一遍：`M` 加 $1000$；`C` 比右边的 `M` 小，减 $100$；`M` 加 $1000$；`X` 比 `C` 小，减 $10$；`C` 加 $100$；`I` 比 `V` 小，减 $1$；最后 `V` 加 $5$，合计 $1994$。

## 参考代码

```python
def romanToInt(s: str) -> int:
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    ans = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and val[ch] < val[s[i + 1]]:
            ans -= val[ch]
        else:
            ans += val[ch]
    return ans


if __name__ == "__main__":
    assert romanToInt("III") == 3
    assert romanToInt("LVIII") == 58
    assert romanToInt("MCMXCIV") == 1994
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert romanToInt("III") == 3
assert romanToInt("LVIII") == 58
assert romanToInt("MCMXCIV") == 1994
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。符号表大小固定。

## 边界

单字符直接查表，比如 `V` $\to$ $5$。全是加法的情况比如 `VIII` $=8$，每位都比右边大或相等，一路加下去。连续减法对比如 `MCMXCIV`，相邻小减大加就行，不必每次跳过两个字符。

## 追问

**输入可能非法怎么办？**
本题保证合法，不用校验。真要校验，就扫一遍检查这些规则：只允许 `I,V,X,L,C,D,M`；`I,X,C,M` 最多连写三次，`V,L,D` 不能重复；减法对只能是 `IV,IX,XL,XC,CD,CM`，且被减符号左边不能再出现同类。比如 `IL`、`IC`、`VX` 都是非法减法。时间 $O(n)$。

**反过来，整数转罗马（LC 12）？**
用贪心查表。把 $900$、$400$ 这些减法档也做成表项，按面值从大到小处理，当前数不少于面值就整除、拼上对应符号，这样 $4$、$9$ 不用单独处理。输入上界是 $3999$，所以时间和空间都是 $O(1)$。表里必须有六种减法，否则会输出 `IIII`。独立卡见 `lc-12-integer-to-roman`。

```python
def intToRoman(num):
    table = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    parts = []
    for val, sym in table:
        q, num = divmod(num, val)
        parts.append(sym * q)
    return "".join(parts)
```
