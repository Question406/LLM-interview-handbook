---
id: ali-oa-picky-eater
section: alibaba-oa
order: 6
level: S
title: 阿里 AI 研发 0325：第 $k$ 个「不含 3 且不被 3 整除」的正整数？
quick: >-
  二分答案 $x$，用数位 DP 数出 $\le x$ 的合法数个数。合法数位只有 $9$ 种，按模 $3$ 的余数正好三三分组，也可以用 $9$ 的幂按位计数；别每轮清空数位 DP 的缓存，询问多时会超时。
tags:
  - Alibaba
  - OA
  - 数位DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
---

## 题目描述

把所有正整数按从小到大的顺序排列，只保留同时满足以下条件的数：十进制表示不含字符 `3`，并且整数本身不能被 3 整除。给定 k，返回保留下来的第 k 个数，下标从 1 开始。

### 接口与输入输出

实现 `kth_liked(k) -> int`，其中 `1 <= k <= 10^18`。本卡还提供辅助接口 `count_upto(x)`，语义是统计 1 到 x 中符合条件的正整数数量；x 为 0 时计数为 0。

标准输入第一行是询问数 T，随后给出 T 个 k，每个询问输出一行结果。结果可能超过常见 64 位整数范围，不得因整数溢出改变答案。

### 示例

```text
符合条件的开头几个数：1, 2, 4, 5, 7, 8, 10, ...
kth_liked(1) -> 1
kth_liked(3) -> 4
kth_liked(7) -> 10
count_upto(10) -> 7
```

0 不属于候选，13 虽然不能被 3 整除，但含数字 3，也不能保留。

## 解题思路与参考答案

我会二分答案：$f(x)$ 表示 $1\ldots x$ 里喜欢的整数有多少个，它随 $x$ 单调，找最小的 $x$ 使 $f(x)\ge k$。$f(x)$ 用数位 DP 算，状态里带上数位和模 $3$，只走不含 `3` 的那 $9$ 个数位。

## 真题记录

阿里 AI 研发 2026.03.25 研发第 3 题，原题叫挑食。「喜欢的整数」指十进制不含数字 $3$、且数值不被 $3$ 整除，求从 $1$ 开始升序排列后的第 $k$ 个。公开版本 $k$ 可到 $10^{18}$，答案可能超过 64 位。

## 题面

定义正整数 $x$ 为「喜欢的整数」，当且仅当：

1. $x$ 不能被 $3$ 整除
2. $x$ 的十进制表示中不能出现数字字符 `3`

对每个询问给出 $k$，求第 $k$ 个喜欢的整数。

输入是 $T$ 组询问，每组一个 $k$，公开版本 $k$ 可到 $10^{18}$。每组输出对应的第 $k$ 个整数。

## 思路

合法数位集合是 $\{0,1,2,4,5,6,7,8,9\}$，共 $9$ 个。因为 $10\equiv 1\pmod 3$，$x\bmod 3$ 等于各位数字和模 $3$。这 $9$ 个数位按模 $3$ 恰好是 $0,1,2$ 各三个，所以末几位自由填写时，三种余数几乎均匀。

喜欢的整数按数值递增，$f$ 单调，所以二分成立。$f(x)$ 用数位 DP，从高位到低位枚举，状态是剩余位数、已选数位和模 $3$、是否贴着上界、是否已经开始填非零。转移只走合法数位，计数时要求已经开始、并且模 $3$ 不为 $0$。前导零不算「已经开始」，所以不会把 $0$ 当成正整数。比如 $x=3$：$1,2$ 合法，$3$ 含数字 $3$ 且能被 $3$ 整除，所以 $f(3)=2$。

二分上界可以用公式估。$1$ 位合法数有 $6$ 个（$1,2,4,5,7,8$），$\ell\ge 2$ 位的合法数有 $48\cdot 9^{\ell-2}$ 个，于是至多 $\ell$ 位的合法数总共 $6\cdot 9^{\ell-1}$ 个。由此 $k\le 10^{18}$ 时答案至多约 $20$ 位，二分上界取 $10^{20}$ 就够。

考场上递归数位 DP 如果每轮 `memset` 清空，$T$ 较大时会 TLE。应该把上界数字传进去，按「剩余长度 + 模 + tight + started」记忆化，或者直接用公式加按位枚举。

## 参考代码

```python
import sys
from functools import lru_cache

DIGITS = (0, 1, 2, 4, 5, 6, 7, 8, 9)


def count_upto(x):
    if x <= 0:
        return 0
    s = list(map(int, str(x)))
    n = len(s)

    @lru_cache(None)
    def dfs(pos, mod, tight, started):
        if pos == n:
            return int(started and mod != 0)
        up = s[pos] if tight else 9
        ans = 0
        for d in DIGITS:
            if d > up:
                continue
            ans += dfs(
                pos + 1,
                (mod + d) % 3,
                tight and d == up,
                started or d != 0,
            )
        return ans

    return dfs(0, 0, True, False)


def kth_liked(k):
    lo, hi = 1, 10**20
    while lo < hi:
        mid = (lo + hi) // 2
        if count_upto(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    t = int(data[0])
    ks = list(map(int, data[1:1 + t]))
    for k in ks:
        print(kth_liked(k))


if __name__ == "__main__":
    main()
```

上面的 `count_upto` 每次新建闭包，缓存自然是隔离的。如果把 DP 提成全局函数，就必须按 $x$ 的数位重建，或者在 `idx` 之外带上上界信息。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

用小范围枚举作独立答案：排除含 3 和能被 3 整除的正整数，同时检查第 k 个数的计数边界。

```python
liked = [x for x in range(1, 100) if "3" not in str(x) and x % 3 != 0]
for k, expected in enumerate(liked[:10], 1):
    assert kth_liked(k) == expected
assert count_upto(0) == 0
assert count_upto(10) == 7
print("simple tests passed")
```

## 复杂度

每组询问二分约 $70$ 次，每次数位 DP 的状态是 $O(\mathrm{len}\cdot 3\cdot 2\cdot 2)$、转移 $9$，长度在 $20$ 量级。对 $T$ 组询问，总时间可以接受。空间就是 DP 缓存的规模。

## 边界

$k=1$ 答案是 $1$，不要输出 $0$。Python 整数没有 64 位溢出；其他语言要用大整数或 `__int128`。

## 追问

**直接当成 $9$ 进制数行吗？**
不行，那只处理了「不含 $3$」，还得剔除能被 $3$ 整除的。

**前导零怎么处理？**
前导零不能算已经开始。算进去的话，前导零的模也被当成已开始，会把 $0$ 算进去，或者把 $03$ 这种非法表示漏判。

**$k=10^{18}$ 时答案会有多大？**
可能超过 `unsigned long long`，现场要用大数。

**不含数字 $3$、允许前导零的计数有闭式吗？**
有。不足 $n$ 位的部分用 $6\cdot 9^{\ell-1}$；贴上界的最高位要单独枚举比当前位小的合法数字。
