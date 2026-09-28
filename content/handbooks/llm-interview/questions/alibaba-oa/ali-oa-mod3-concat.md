---
id: ali-oa-mod3-concat
section: alibaba-oa
order: 22
level: A
title: 淘天 0403：哪些区间拼接后能被 3 整除？
quick: >-
  一个数 $\bmod 3$ 等于各位/区间数字和 $\bmod 3$。用前缀和 $p_r-p_{l-1}\equiv 0\pmod 3$ 判断单段；多段拼接把各段余数相加。
tags:
  - Alibaba
  - OA
  - 前缀和
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天笔试 0403（公开回忆）
- 题意：判断若干区间拼出的数字（或数值）是否为 $3$ 的倍数。

## 题面

（公开回忆等价转述）给定数字串 $s$（每位是 `0` 到 `9`）。有 $q$ 次询问，每次给出 $t$ 个闭区间 $[l_i,r_i]$（$1$-based），按给定顺序把这些子串拼接成一个大整数（或只关心它的数值）。问这个数能否被 $3$ 整除。

公开回忆未写死 $n,q,t$ 与输出格式。下面：`YES` / `NO` 每询问一行。前导零仍参与数位和。

输入假设：第一行 $s$，第二行 $q$，随后每行先 $t$ 再 $2t$ 个端点。

## 思路

$10\equiv 1\pmod 3$，因此任何十进制数

$$
x=\sum d_i 10^{w_i}\equiv \sum d_i \pmod 3
$$

也就是数位和模 $3$。把若干段按顺序拼起来，总余数等于各段数位和模 $3$ 再相加。不必真的拼接大整数，也不必关心各段的长度，因为 $10^w\equiv 1$，左边旧段乘上 $10^{\mathrm{len}(\mathrm{new})}$ 余数不变。

算法：预处理前缀和 $p[i]=d_1+\cdots+d_i$。区间 $[l,r]$ 的数位和是 $p[r]-p[l-1]$。询问把各段余数累加，看是否 $\equiv 0\pmod 3$。

模 $3$ 下移位不改变已有余数，来自 $10\equiv 1$。对模 $9$ 同样成立；对模 $11$ 要交替加减，不能这么干。

## 参考代码

```python
import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    s = data[0].strip()
    n = len(s)
    p = [0] * (n + 1)
    for i, ch in enumerate(s, 1):
        p[i] = p[i - 1] + (ord(ch) - 48)

    idx = 1
    q = int(data[idx])
    idx += 1
    out = []
    for _ in range(q):
        t = int(data[idx])
        idx += 1
        total = 0
        for _ in range(t):
            l = int(data[idx])
            r = int(data[idx + 1])
            idx += 2
            if l > r:
                l, r = r, l
            total += p[r] - p[l - 1]
        out.append("YES" if total % 3 == 0 else "NO")
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

边界：单段 `[1,n]` 就是整个数字；$t=0$ 的空拼接视为 $0$，能被 $3$ 整除（若现场保证 $t\ge 1$ 则不会出现）；全 `0` 是 $0$，`YES`。

## 复杂度

预处理 $O(n)$，每段询问 $O(1)$，总时间 $O(n+\sum t)$，空间 $O(n)$。

## 易错 / 面试追问

- 真的把区间拼成字符串再 `int`，长串溢出或超时。
- 以为拼接后要乘 $10^{len}$，对模 $3$ 多做了移位。
- 前导零直接丢掉；模 $3$ 题里零位仍是 $0$，通常要算进和。
- 追问模 $9$：同一套数位和。追问模 $11$：改成交替和或带长度的前缀加权。
