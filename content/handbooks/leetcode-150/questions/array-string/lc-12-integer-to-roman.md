---
id: lc-12-integer-to-roman
section: array-string
order: 18
level: A
title: LC 12 · 整数转罗马数字
quick: "建立面值与符号表 $1000,900,500,400,\\ldots,1$，从大到小减去能容纳的面值，并拼接符号。减法写法也放进表，避免单独处理 4 和 9。输入上限 $3999$ 固定，所以时间与空间都是 $O(1)$。"
tags:
  - Hash
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 12. 整数转罗马数字
    url: https://leetcode.cn/problems/integer-to-roman/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给你一个 $1$ 到 $3999$ 的整数，转成罗马数字。减法那种写法就是 `CM`、`CD`、`XC`、`XL`、`IX`、`IV`。

## 思路

把 $900$、$400$ 等减法写法也作为表项，从最大面值开始处理。只要当前数 $\ge$ 面值，就减去该值并拼接对应符号。这样 $4$、$9$ 可以与普通面值一起处理，无需额外分支。

按千、百、十、个位各查一张表也能做；白板我一般还是贪心表，更短。

## 参考代码

```python
def intToRoman(num: int) -> str:
    table = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    parts = []
    for val, sym in table:
        if num == 0:
            break
        q, num = divmod(num, val)
        parts.append(sym * q)
    return "".join(parts)


if __name__ == "__main__":
    assert intToRoman(3749) == "MMMDCCXLIX"
    assert intToRoman(58) == "LVIII"
    assert intToRoman(1994) == "MCMXCIV"
    print("ok")
```

## 复杂度

时间和空间都是 $O(1)$。输入最大 $3999$，输出长度也有常数上限。

## 边界

- $1$ 和 $3999$ 要过一遍。减法档 $4/9/40/90/400/900$ 也得覆盖：表里必须有 `IV`、`IX`、`XL`、`XC`、`CD`、`CM`，漏了就会拼出 `IIII` 这种非法串。

## 追问

- **输入超出 $3999$，或要写更大的整数？** 标准罗马数字一般只约定到 $3999$（`MMMCMXCIX`）。再大没有统一面试约定：有的体系用上划线表示 $\times 1000$，有的直接拒绝，所以先问清范围。若允许扩展，就把更大的面值做成新表项，贪心还是从大到小减。时间和表长度成正比；标准范围内表长固定，所以是 $O(1)$。这块容易栽：别假装 `MMMM` 是合法标准写法。

- **反过来，罗马转整数（LC 13）？** 建符号表 `I,V,X,L,C,D,M`。从左扫：当前值比右边小就减当前，否则加。最后一位只能加。不必枚举六种减法对，相邻比一下就行。时间 $O(n)$，额外空间 $O(1)$。顺序这块容易栽：`IV` 是 $-1+5=4$；从右往左扫「比左边大就减」也对。独立卡见 `lc-13-roman-to-integer`。

```python
def romanToInt(s):
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    ans = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and val[ch] < val[s[i + 1]]:
            ans -= val[ch]
        else:
            ans += val[ch]
    return ans
```
