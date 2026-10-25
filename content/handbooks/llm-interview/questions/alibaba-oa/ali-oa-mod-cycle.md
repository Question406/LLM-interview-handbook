---
id: ali-oa-mod-cycle
section: alibaba-oa
order: 13
level: B
title: 淘天研发 0411：模乘循环会出现多少个不同数？
quick: >-
  从 $1$ 出发反复做 $x\leftarrow (x\cdot k)\bmod m$，用集合记下见过的值，第一次撞上旧值就停，集合大小就是答案。$m=1$ 时 $1$ 和 $0$ 都算，答案是 $2$。
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

## 题目描述

一个整数状态 x 从 1 开始，重复执行“把 x 乘以 k 后对 m 取模”。在某个状态第一次重复出现之前，统计总共访问过多少个不同状态。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `distinct_mod_mul(k, m)`。本卡令 k 为非负整数、m 为至少 2 的整数，初始状态 1 也计入。main 可读取多组 k、m，每组输出一行。

### 输出与约束

返回不同状态的数量。进入 0 后也把 0 计入；序列可能先经过一段不循环的前缀，不能只统计最后循环的长度。不要求输出状态序列。

### 示例

```text
k=2, m=7：1 -> 2 -> 4 -> 1，返回 3
k=2, m=4：1 -> 2 -> 0 -> 0，返回 3
k=1, m=5：1 -> 1，返回 1
```

## 解题思路与参考答案

直接模拟就行：从 $1$ 开始反复乘 $k$ 取模，用集合记下见过的值，第一次碰到见过的值就停，集合大小就是答案。余数最多 $m$ 种，所以一定会停，最坏 $O(m)$。

## 真题记录

淘天研发 / AI 研发 2026.04.11 第 1 题。样例是 $k=2,m=10$，依次得到 $1,2,4,8,6$，答案 $5$；再下一步是 $2$，开始循环。

## 题面

$x$ 初始为 $1$，反复执行 $x\leftarrow (x\cdot k)\bmod m$。一旦某个 $x$ 第二次出现，之后状态必然循环。求从初始状态开始一共出现过多少个不同的 $x$。

输入是 $k,m$，可能有多组。公开复盘没有写死范围；状态空间大小是 $m$，按 $O(m)$ 模拟。每组输出一个整数，表示不同状态的数量。

## 思路

映射 $x\mapsto (xk)\bmod m$ 定义在有限集上，从任何起点出发走出来的都是「一条链 + 一个环」。不同值的个数，就是第一次重复之前走过的长度。

做法是从 $x=1$ 开始，把当前值计入并标记，再走到下一步；下一步已经见过就停。记录用集合，因为初始的 $1$ 可能 $\ge m$，集合可以同时装下它和余数 $0\ldots m-1$。$m$ 很大而环很快出现时，集合也比开长度为 $m$ 的布尔数组省。

第一次撞上旧值以后只会在环里转，不会再出现新值。题目要的是整条轨迹去重后的个数，环长不够用，所以不用推闭式，也不用 Floyd 判圈。

有几种特殊情况要单独想清楚。$m=1$ 时任何正整数模 $1$ 都是 $0$；初始的 $1$ 不在 $\{0\}$ 里，下一步到 $0$，之后一直是 $0$，不同的数是 $1$ 和 $0$，答案 $2$。$k=0$ 且 $m\gt 1$ 时序列是 $1,0,0,\ldots$，答案 $2$。$k=1$ 时序列是 $1,1\bmod m, (1\bmod m),\ldots$，$m\gt 1$ 就一直是 $1$，答案 $1$。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

2 的幂模 7 会循环为 1、2、4；模 4 则经过 1、2、0 后进入固定点。第二个例子专门覆盖不是纯循环的前导部分。

```python
assert distinct_mod_mul(2, 7) == 3
assert distinct_mod_mul(2, 4) == 3
assert distinct_mod_mul(1, 5) == 1
print("simple tests passed")
```

## 复杂度

时间 $O(\min(m,T_{\mathrm{loop}}))$，最坏 $O(m)$；空间最坏 $O(m)$。

## 边界

$m=1$、$k=0$ 在上面已经覆盖。同一组数据重复读入时，答案应该稳定。

## 追问

**$m=1$ 时答案为什么是 $2$？**
初始的 $1$ 也算一个不同的数。只数到 $0$、写成 $1$，就漏了它。

**用 `visited[x]` 开 $[0,m)$ 的数组行吗？**
$m=1$ 时第一步 $x=1$ 就越界了，所以代码用集合。

**能推 $\mathrm{ord}_m(k)$ 这类闭式吗？**
闭式算的是环，前缀链上还有不在环里的值，很容易漏掉。

**如果从 $x=s$ 出发呢？**
同一套模拟，只改初值；$s\ge m$ 时先决定要不要先取模。本题初值 $1$ 不先取模。
