---
id: lc-12-integer-to-roman
section: array-string
order: 18
level: A
title: LC 12 · 整数转罗马数字
quick: >-
  贪心表按 $1000,900,500,400,\ldots,1$ 从大到小：能减就追加对应符号。时间 $O(1)$（数值范围固定）。
tags:
  - Hash
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 12. 整数转罗马数字
    url: https://leetcode.cn/problems/integer-to-roman/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把 $1$ 到 $3999$ 的整数转成罗马数字。减法形式用 `CM`、`CD`、`XC`、`XL`、`IX`、`IV`。

## 思路

把 $900$、$400$ 等减法档位也做成表项，按从大到小贪心：当前数 $\ge$ 面值就减去并拼符号。这样不用单独处理 $4$、$9$。

按千 / 百 / 十 / 个位查表也可以。面试贪心表更短。

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

时间、空间都是 $O(1)$：输入上界 $3999$，输出长度有常数上限。

## 边界

- $1$、$3999$，以及 $4/9/40/90/400/900$ 各减法档都要覆盖：贪心表里必须有 `IV`、`IX`、`XL`、`XC`、`CD`、`CM`，否则会拼出 `IIII` 这类非法串。

## 追问

- **输入超出 $3999$，或要写更大的整数？** 标准罗马数字通常只约定到 $3999$（`MMMCMXCIX`）。再大没有统一面试约定：有的体系用上划线表示 $\times 1000$，有的直接拒绝。白板先问清范围。若允许扩展，就把更大的面值做成新表项，贪心逻辑不变，仍从大到小减。时间与表长度成正比；标准范围内表长固定，所以是 $O(1)$。易错点是不要假装 `MMMM` 是合法标准写法。

- **反过来，罗马转整数（LC 13）？** 建符号表 `I,V,X,L,C,D,M`。从左扫：若当前值小于右侧，就减去当前，否则加上。最后一位只能加。不必枚举六种减法对，相邻比较即可。时间 $O(n)$，额外空间 $O(1)$。易错点是先减后加的顺序：`IV` 是 $-1+5=4$，从右往左扫「比左边大就减」也对。独立卡见 `lc-13-roman-to-integer`。

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

