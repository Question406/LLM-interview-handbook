---
id: lc-13-roman-to-integer
section: array-string
order: 17
level: S
title: LC 13 · 罗马数字转整数
quick: >-
  建符号表。从左扫：若 `s[i]` 的值 $\lt$ `s[i+1]` 则减去当前，否则加上。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Hash
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 13. 罗马数字转整数
    url: https://leetcode.cn/problems/roman-to-integer/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定合法罗马数字字符串 `s`，转成整数。减法对只有 `IV`、`IX`、`XL`、`XC`、`CD`、`CM`。

## 思路

小的符号写在大的左边表示减。扫到位置 $i$，若它比右边小就减 `val(s[i])`，否则加。最后一位只能加。不必特判六种组合，比较相邻值即可。

面试先报符号表：`I=1,V=5,X=10,L=50,C=100,D=500,M=1000`。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。符号表大小固定。

## 边界

- 单字符：直接查表，如 `V` $\to$ $5$。
- 全加法：如 `VIII` $=8$，每位都比右边大或相等，一路加。
- 连续减法对：如 `MCMXCIV`，相邻小减大加即可，不必一次吃两个字符。

## 追问

- **输入可能非法？** 本题保证合法，不必校验。若要校验：只允许 `I,V,X,L,C,D,M`；`I,X,C,M` 最多连写三次，`V,L,D` 不能重复；减法对只能是 `IV,IX,XL,XC,CD,CM`，且被减符号左边不能再出现同类。扫一遍检查这些规则，时间 $O(n)$。易错点是 `IL`、`IC`、`VX` 都是非法减法。

- **反过来，整数转罗马（LC 12）？** 把 $900$、$400$ 等减法档也做成表项，按从大到小贪心：当前数不少于面值就整除，拼上对应符号。这样不用单独处理 $4$、$9$。时间、空间都是 $O(1)$（输入上界 $3999$）。易错点是表必须含六种减法，否则会输出 `IIII`。独立卡见 `lc-12-integer-to-roman`。

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

