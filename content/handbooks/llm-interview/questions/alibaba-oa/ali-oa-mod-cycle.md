---
id: ali-oa-mod-cycle
section: alibaba-oa
order: 13
level: B
title: 淘天研发 0411：模乘循环会出现多少个不同数？
quick: >-
  从 $1$ 出发反复做 $x\leftarrow (x\cdot k)\bmod m$，用访问数组判重。第一次撞上已见值就停。$m=1$ 时 $1$ 和 $0$ 都算，答案是 $2$。
tags:
  - Alibaba
  - OA
  - 模拟
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 淘天研发 2026.04.11 改编真题
    url: https://www.nowcoder.com/discuss/872969146470887424
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天研发 / AI 研发 2026.04.11 T1
- 样例：$k=2,m=10$ 得到 $1,2,4,8,6$，答案 $5$。下一次 $2$，开始循环。

## 题面

$x$ 初始为 $1$，反复执行 $x\leftarrow (x\cdot k)\bmod m$。一旦某个 $x$ 第二次出现，之后状态必然循环。求从初始状态开始一共出现过多少个不同的 $x$。

输入：$k,m$（可能多组）。公开复盘未写死范围；状态空间大小是 $m$，按 $O(m)$ 模拟。

输出：每组一个整数，表示不同状态数量。

## 思路

映射 $x\mapsto (xk)\bmod m$ 定义在有限集上，从任意起点出发都是「一条链 + 一个环」。不同值的个数等于第一次重复之前走过的长度。

算法：从 $x=1$ 开始，用长度为 $m$ 的布尔数组（再额外记住初始 $1$，因为 $1$ 可能 $\ge m$）记录见过的值。每次把当前值计入答案并标记，再走到下一步；若下一步已见过则停止。

第一次撞上已访问值时，之后只会在环里转，不会再产生新值。这里要的是整条轨迹的去重个数，不是环长，所以不用推闭式，也不用 Floyd 判圈。

特殊情形：

- $m=1$：任何正整数模 $1$ 都是 $0$。初始 $1$ 本身不在 $\{0\}$ 里，下一步到 $0$，再下一步还是 $0$。不同数是 $1$ 和 $0$，答案 $2$
- $k=0$ 且 $m\gt 1$：序列 $1,0,0,\ldots$，答案 $2$
- $k=1$：序列 $1,1\bmod m, (1\bmod m),\ldots$。若 $m\gt 1$ 则一直是 $1$，答案 $1$

## 参考代码

```python
import sys


def distinct_mod_mul(k, m):
    seen = set()
    x = 1
    while x not in seen:
        seen.add(x)
        x = (x * k) % m
    return len(seen)


def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    i = 0
    if len(data) >= 3 and data[0] * 2 + 1 == len(data):
        t = data[0]
        i = 1
    else:
        t = len(data) // 2
    out = []
    for _ in range(t):
        k, m = data[i], data[i + 1]
        i += 2
        out.append(str(distinct_mod_mul(k, m)))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

`seen` 用集合即可同时容纳初始 $1$ 和余数 $0\ldots m-1$。若 $m$ 很大而环很快出现，集合比开 $m$ 布尔数组更省。

边界：上面 $m=1$、$k=0$ 已覆盖。同一组数据重复读入时答案应稳定。

## 复杂度

时间 $O(\min(m,T_{\mathrm{loop}}))$，最坏 $O(m)$；空间最坏 $O(m)$。

## 易错 / 面试追问

- $m=1$ 时把答案写成 $1$（只看见 $0$），漏掉初始 $1$。
- 用 `visited[x]` 只开了 $[0,m)$，第一步 $x=1$ 在 $m=1$ 时越界。
- 推 $\mathrm{ord}_m(k)$ 一类闭式，却忘了前缀链上还有不在环里的值。
- 追问「从 $x=s$ 出发」：同一套模拟，只改初值；若 $s\ge m$ 先决定要不要先取模。本题初值 $1$ 不先取模。
