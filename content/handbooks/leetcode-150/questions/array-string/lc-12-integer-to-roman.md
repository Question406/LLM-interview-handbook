---
id: lc-12-integer-to-roman
section: array-string
order: 18
level: A
title: LC 12 · 整数转罗马数字
quick: "用贪心查表：把 $1000,900,500,400,\\ldots,1$ 连同减法写法一起放进面值表，从大到小能减就减、拼上对应符号，4 和 9 就不用单独处理。输入上限 $3999$ 固定，所以时间与空间都是 $O(1)$。"
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

## 题目描述

给定整数 `num`，返回它的标准罗马数字表示。罗马数字使用 `I=1`、`V=5`、`X=10`、`L=50`、`C=100`、`D=500`、`M=1000`。除了指定的减法组合，符号按数值从大到小排列并相加。`I/X/C/M` 可以重复，`I/X/C` 连续最多出现三次，`V/L/D` 不重复；4、9、40、90、400、900 分别使用 `IV`、`IX`、`XL`、`XC`、`CD`、`CM`。

### 接口与输出

实现 `intToRoman(num: int) -> str`，返回完整的罗马数字字符串，不返回各位数字的列表。

### 合法输入与约束

`1 <= num <= 3999`。输入在这个范围内，不需要处理零、负数或其他记数扩展。

### 示例

```text
输入：num = 3749
输出："MMMDCCXLIX"
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/integer-to-roman/description/)。

## 解题思路与参考答案

## 题意

给你一个 $1$ 到 $3999$ 的整数，转成罗马数字。减法那种写法就是 `CM`、`CD`、`XC`、`XL`、`IX`、`IV`。

## 思路

我会用贪心查表，把 $900$、$400$ 这种减法写法也当成普通面值放进表里，这样 $4$、$9$ 和普通面值一起处理，不用额外写分支。做法是从最大的面值开始，只要当前数 $\ge$ 面值，就减掉它、拼上对应符号。

拿 $1994$ 走一遍：先减 $1000$ 拼 `M`，剩 $994$；$900$ 放得下，拼 `CM`，剩 $94$；$90$ 拼 `XC`，剩 $4$；最后 $4$ 直接命中 `IV`，结果是 `MCMXCIV`。

按千、百、十、个位各查一张表也能做，不过白板上我一般还是写贪心表，更短。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert intToRoman(3749) == "MMMDCCXLIX"
assert intToRoman(58) == "LVIII"
assert intToRoman(1994) == "MCMXCIV"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间和空间都是 $O(1)$。输入最大 $3999$，输出长度也有常数上限。

## 边界

$1$ 和 $3999$ 都要过一遍。减法档 $4/9/40/90/400/900$ 也得覆盖到，表里必须有 `IV`、`IX`、`XL`、`XC`、`CD`、`CM`，漏一个就会拼出 `IIII` 这种非法串。

## 追问

**输入超出 $3999$，或者要写更大的整数怎么办？**
先问清范围。标准罗马数字一般只约定到 $3999$（`MMMCMXCIX`），再大没有统一的面试约定：有的体系用上划线表示 $\times 1000$，有的直接拒绝。如果允许扩展，就把更大的面值做成新表项，贪心照样从大到小减，时间和表长度成正比；标准范围内表长固定，所以是 $O(1)$。别把 `MMMM` 说成合法的标准写法。

**反过来，罗马转整数（LC 13）怎么写？**
建一张 `I,V,X,L,C,D,M` 的符号表，从左往右扫，当前值比右边小就减当前值，否则加，最后一位只能加。这样不用枚举六种减法对，相邻比一下就行，时间 $O(n)$，额外空间 $O(1)$。比如 `IV` 就是 $-1+5=4$；从右往左扫、「比左边大就减」也对。独立卡见 `lc-13-roman-to-integer`。

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
