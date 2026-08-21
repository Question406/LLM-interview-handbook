---
id: ali-oa-picky-eater
section: alibaba-oa
order: 6
level: S
title: 阿里 AI 研发 0325：第 $k$ 个「不含 3 且不被 3 整除」的正整数？
quick: >-
  二分答案，再数 $\le x$ 的合法数。合法十进制位只有 $9$ 种且对 $3$ 均匀，可用 $9$ 的幂按位计数，不必每轮清空数位 DP。
tags:
  - Alibaba
  - OA
  - 数位DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
---

## 真题记录

- 公司 / 场次：阿里 AI 研发 2026.03.25 · 研发 Q3
- 原始题意：挑食 / 「喜欢的整数」= 十进制不含数字 $3$，且数值不被 $3$ 整除。求从 $1$ 开始升序后的第 $k$ 个。公开版本 $k$ 可到 $10^{18}$，答案可能超过 64 位。

## 题面

定义正整数 $x$ 为「喜欢的整数」，当且仅当：

1. $x$ 不能被 $3$ 整除
2. $x$ 的十进制表示中不能出现数字字符 `3`

对每个询问给出 $k$，求第 $k$ 个喜欢的整数。

输入：$T$ 组询问，每组一个 $k$；公开版本 $k$ 可到 $10^{18}$。

输出：每组对应的第 $k$ 个整数。

## 思路

观察：合法数位集合是 $\{0,1,2,4,5,6,7,8,9\}$，共 $9$ 个。因为 $10\equiv 1\pmod 3$，所以 $x\bmod 3$ 等于各位数字和模 $3$。这 $9$ 个数对模 $3$ 恰好是 $0,1,2$ 各三个，因此「末几位自由填写」时，三种余数几乎均匀。

算法：二分答案 $x$，计算 $f(x)=$「$1\ldots x$ 中喜欢的整数个数」，找最小的 $x$ 使 $f(x)\ge k$。

$f(x)$ 用数位 DP：从高到低枚举，状态为（剩余位数、已选数位和模 $3$、是否贴上界、是否已经开始填非零）。转移只走合法数位；统计时要求已经开始、且模 $3$ 不为 $0$。

也可以先用公式数「位数更短」的全部合法数。记 $1$ 位合法数有 $6$ 个（$1,2,4,5,7,8$），$\ell\ge 2$ 位合法数有 $48\cdot 9^{\ell-2}$ 个，于是至多 $\ell$ 位的合法总数是 $6\cdot 9^{\ell-1}$。由此可知 $k\le 10^{18}$ 时答案至多约 $20$ 位，二分上界取 $10^{20}$ 足够。

为什么对：喜欢的整数按数值递增，且 $f$ 单调。数位 DP 枚举的是所有不含 `3` 的十进制表示，再滤掉和为 $3$ 的倍数，与定义一致。前导零不计入「已经开始」，因此不会把 $0$ 算成正整数。

考场递归数位 DP 若每轮 `memset` 清空，在 $T$ 较大时会 TLE；应把上界数字传入、记忆化按「剩余长度 + 模 + tight + started」缓存，或直接用公式加按位枚举。

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

上面 `count_upto` 每次新建闭包，缓存自然隔离。若把 DP 提成全局函数，必须按 $x$ 的数位重建或带上 `idx` 之外的上界信息。

边界：$k=1$ 答案是 $1$；不要输出 $0$。$x=3$ 时 $1,2$ 合法，$3$ 含数字 $3$ 且能被 $3$ 整除，故 $f(3)=2$。Python 整数无 64 位溢出；其他语言要用大整数或 `__int128`。

## 复杂度

每组询问二分约 $70$ 次，每次数位 DP 状态 $O(\mathrm{len}\cdot 3\cdot 2\cdot 2)$、转移 $9$，长度为 $20$ 量级。总时间对 $T$ 组可接受。空间为 DP 缓存规模。

## 易错 / 面试追问

- 把合法数直接当成 $9$ 进制，忘记还要剔除「能被 $3$ 整除」。
- 数位 DP 把前导零的模也当成已经开始，会把 $0$ 算进去，或把 $03$ 这种非法表示漏判。
- $k=10^{18}$ 时答案超过 `unsigned long long` 的可能，现场要用大数。
- 追问「不含数字 $3$ 但允许前导零的计数闭式」：不足 $n$ 位用 $6\cdot 9^{\ell-1}$；贴上界的最高位要单独枚举比当前位小的合法数字。
