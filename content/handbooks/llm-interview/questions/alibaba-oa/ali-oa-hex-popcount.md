---
id: ali-oa-hex-popcount
section: alibaba-oa
order: 19
level: B
title: 阿里 2022.03.14 研发：十六进制 popcount 要注意什么？
quick: >-
  按十六进制字符串逐位查 $0$–$F$ 的二进制 $1$ 个数，不要先转成可能溢出的整数。空串、前导零、大小写都要约定。
tags:
  - Alibaba
  - OA
  - 模拟
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里 2022.03.14 研发机试（公开回忆）
- 题意：给定十六进制表示，统计对应二进制中 $1$ 的个数。

## 题面

给定一个十六进制数字的字符串表示（可含前导零，字母可为大小写），求它对应二进制表示中数字 `1` 的个数，即 Hamming weight / popcount。

公开回忆未给出精确长度上界。按字符串处理，避免先转成机器整数。空串按 $0$ 处理。

输入：一行十六进制串。输出：一个整数。

## 思路

观察：每个十六进制位恰好对应 $4$ 个二进制位，彼此独立。总 popcount 等于各位 popcount 之和。

算法：预计算 `0..15` 的二进制 $1$ 个数，对每个字符查表累加。`A-F` / `a-f` 映射到 $10\ldots 15$。

为什么对：$n$ 的二进制 $1$ 的个数等于把它按 $4$ 位分组后各组 $1$ 的个数之和，与书写时的前导零无关——前导零的 popcount 是 $0$，加了也不变。

不要把「先转整数再数」当成唯一写法：在 C++ / Java 里长串会溢出。Python 的 `int(s, 16)` 可以，但面试应主动说「按位查表」。

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

边界：`0`、`00` 答案都是 $0$；`F` 是 $4$；`10` 是 $1$。允许前缀 `0x`。空输入输出 $0$。

## 复杂度

时间 $O(|s|)$，额外空间 $O(1)$。

## 易错 / 面试追问

- 先转 `long` 再数，长十六进制串溢出。
- 只处理大写或只处理小写。
- 把十六进制数字 `8` 当成十进制去模 $2$，而不是看它的四位二进制 $1000_2$。
- 追问位运算版本：`while x: x &= x - 1; ans += 1`，以及和 `std::popcount` 的关系。
