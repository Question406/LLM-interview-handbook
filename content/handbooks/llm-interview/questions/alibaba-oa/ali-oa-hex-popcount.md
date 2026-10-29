---
id: ali-oa-hex-popcount
section: alibaba-oa
order: 19
level: B
title: 阿里 2022.03.14 研发：十六进制 popcount 要注意什么？
quick: >-
  每个十六进制位正好对应 $4$ 个二进制位，所以逐字符查 $0$ 到 $F$ 的二进制 $1$
  个数再累加就行，不用先转成可能溢出的整数。空串、前导零、大小写要先约定好。
tags:
  - Alibaba
  - OA
  - 模拟
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
---

## 题目描述

给定一个十六进制数字的字符串表示，返回它对应的二进制表示中有多少个 1。输入可能很长，不限定在某种固定宽度的机器整数内。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `hex_popcount(s)`。s 使用数字 0–9 和字母 a–f/A–F，可带 `0x` 或 `0X` 前缀，也可含前导零；本卡允许空字符串。

### 输出与约束

返回一个非负整数；前缀、前导零不增加计数，大小写不影响含义。输入保证是本题约定的合法表示，不要求处理任意混入的非法字符。

### 示例

```text
hex_popcount("0xF") -> 4
hex_popcount("aF") -> 6
hex_popcount("0000") -> 0
hex_popcount("10") -> 1
```

## 解题思路与参考答案

我会把十六进制串当字符串处理：每个字符查表得到它那 $4$ 位二进制里有几个 $1$，加起来就是答案。这样完全不碰大整数，也就没有溢出问题。

## 真题记录

阿里 2022.03.14 研发机试的公开回忆，题意是给定十六进制表示，统计对应二进制中 $1$ 的个数。

## 题面

给定一个十六进制数字的字符串表示（可含前导零，字母可为大小写），求它对应二进制表示中数字 `1` 的个数，即 Hamming weight / popcount。

公开回忆没有给出精确的长度上界，所以按字符串处理，避免先转成机器整数。空串按 $0$ 处理。

输入一行十六进制串，输出一个整数。

## 思路

每个十六进制位恰好对应 $4$ 个二进制位，彼此独立，所以总 popcount 等于各位 popcount 之和。比如 `F` 是 $1111_2$，贡献 $4$；`10` 是 $0001\,0000_2$，贡献 $1$。

做法是预计算 `0..15` 的二进制 $1$ 的个数，对每个字符查表累加，`A-F` / `a-f` 映射到 $10\ldots 15$。前导零的 popcount 是 $0$，写不写都不影响结果，和数值本身按 $4$ 位分组数出来的一样。

C++ / Java 里先转整数再数会溢出。Python 的 `int(s, 16)` 可以直接用，但面试时最好主动说一句「按位查表」。

## 参考代码

```python
import sys

PC = [bin(i).count("1") for i in range(16)]


def hex_value(ch):
    if "0" <= ch <= "9":
        return ord(ch) - 48
    if "A" <= ch <= "F":
        return ord(ch) - 55
    if "a" <= ch <= "f":
        return ord(ch) - 87
    return None


def hex_popcount(s):
    if s.lower().startswith("0x"):
        s = s[2:]
    ans = 0
    for ch in s.strip():
        v = hex_value(ch)
        if v is None:
            continue
        ans += PC[v]
    return ans


def main():
    tokens = sys.stdin.read().split()
    if not tokens:
        print(0)
        return
    for token in tokens:
        print(hex_popcount(token))


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

每个十六进制 F 有四个 1。检查大小写、0x 前缀、全零和前导零，预期值可以逐位手算。

```python
assert hex_popcount("0xF") == 4
assert hex_popcount("aF") == 6
assert hex_popcount("0000") == 0
assert hex_popcount("10") == 1
print("simple tests passed")
```

## 复杂度

时间 $O(|s|)$，额外空间 $O(1)$。

## Edge Cases

`0`、`00` 答案都是 $0$；`F` 是 $4$；`10` 是 $1$。代码允许前缀 `0x`，空输入输出 $0$。

## 追问

**先转成 `long` 再数行吗？**
长十六进制串会溢出，所以按字符处理。

**大小写都要处理吗？**
要。只处理大写或只处理小写，都会漏算一部分输入。

**十六进制的 `8` 怎么算？**
看它的四位二进制 $1000_2$，贡献 $1$。别把它当成十进制去模 $2$。

**位运算版本怎么写？**
`while x: x &= x - 1; ans += 1`。也可以顺带聊它和 `std::popcount` 的关系。
