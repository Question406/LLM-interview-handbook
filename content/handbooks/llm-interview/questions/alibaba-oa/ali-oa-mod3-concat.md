---
id: ali-oa-mod3-concat
section: alibaba-oa
order: 22
level: A
title: 淘天 0403：哪些区间拼接后能被 3 整除？
quick: >-
  $10\equiv 1\pmod 3$，所以十进制数模 $3$ 等于数位和模 $3$，拼接时的移位也不改变余数。用前缀和算出每段的数位和 $p_r-p_{l-1}$，各段加起来看是否 $\equiv 0\pmod 3$ 就行。
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

## 题目描述

给定仅包含十进制数字的字符串 s。每个询问指定若干个区间，把这些区间在 s 中对应的子串按询问给定的顺序连接起来，判断连接结果代表的十进制整数能否被 3 整除。各区间可以重叠，前导零不需要去掉。

### 输入与输出

本卡采用 `main()` 标准输入接口：先输入 s，再输入询问数 q。每个询问先给区间数 t，再给 t 对端点。端点从 1 开始，区间包含两端；若一对端点倒序，按二者的最小值与最大值确定区间。

每个询问输出一行 `YES` 或 `NO`。t 为正整数，端点均位于 s 内；公开复盘未完整披露长度及询问数上界，以上输入输出格式是手册练习约定。

### 示例

```text
输入：
123
3
1 1 3
1 1 1
2 1 1 2 2

输出：
YES
NO
YES
```

三个询问分别得到整数 123、1 和 12。

## 解题思路与参考答案

不用真的拼数字。因为 $10\equiv 1\pmod 3$，一个数模 $3$ 就等于它的数位和模 $3$，拼接只是把各段的数位和加起来。预处理数位前缀和，每段 $O(1)$ 算出来，累加后看能不能被 $3$ 整除。

## 真题记录

淘天笔试 0403 的公开回忆：判断若干区间拼出的数字（或数值）是否为 $3$ 的倍数。

## 题面

（公开回忆等价转述）给定数字串 $s$（每位是 `0` 到 `9`）。有 $q$ 次询问，每次给出 $t$ 个闭区间 $[l_i,r_i]$（$1$-based），按给定顺序把这些子串拼接成一个大整数（或只关心它的数值）。问这个数能否被 $3$ 整除。

公开回忆没有写死 $n,q,t$ 和输出格式。下面每个询问输出一行 `YES` / `NO`，前导零仍参与数位和。

输入假设第一行是 $s$，第二行是 $q$，随后每行先给 $t$，再给 $2t$ 个端点。

## 思路

$10\equiv 1\pmod 3$，因此任何十进制数

$$
x=\sum d_i 10^{w_i}\equiv \sum d_i \pmod 3
$$

也就是数位和模 $3$。把几段按顺序拼起来时，左边的旧段要乘上 $10^{\mathrm{len}(\mathrm{new})}$，模 $3$ 下这个因子是 $1$，余数不变。所以总余数就是各段数位和相加再模 $3$，不必真的拼接大整数，也不用管各段长度。比如 `12` 和 `3` 拼成 `123`，数位和 $1+2+3=6$，能被 $3$ 整除。

做法是预处理前缀和 $p[i]=d_1+\cdots+d_i$，区间 $[l,r]$ 的数位和是 $p[r]-p[l-1]$。每次询问把各段的和累加，看是否 $\equiv 0\pmod 3$。

移位不改变余数这一点来自 $10\equiv 1$，所以模 $9$ 同样成立；模 $11$ 要交替加减，就不能这么做了。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

字符串 123 的全部数字和为 6，能被 3 整除；单取 1 不能；把区间 [1,1] 与 [2,2] 拼起来得到 12，可以。 用 StringIO 模拟标准输入，redirect_stdout 捕获输出；finally 恢复 stdin，避免影响后续测试。

```python
import io
from contextlib import redirect_stdout

previous_stdin = sys.stdin
try:
    sys.stdin = io.StringIO('123\n3\n1 1 3\n1 1 1\n2 1 1 2 2\n')
    output = io.StringIO()
    with redirect_stdout(output):
        main()
    assert output.getvalue().strip() == 'YES\nNO\nYES'
finally:
    sys.stdin = previous_stdin
print("simple tests passed")
```

## 复杂度

预处理 $O(n)$，每段询问 $O(1)$，总时间 $O(n+\sum t)$，空间 $O(n)$。

## 边界

单段 `[1,n]` 就是整个数字；$t=0$ 的空拼接视为 $0$，能被 $3$ 整除（如果现场保证 $t\ge 1$，就不会出现）；全 `0` 是 $0$，输出 `YES`。

## 追问

**真的把区间拼成字符串再转 `int` 行吗？**
长串会溢出或超时，也没必要。

**拼接后要不要乘 $10^{len}$？**
模 $3$ 下不用，这一步乘的相当于 $1$，多做一次移位是白算。

**前导零要去掉吗？**
不用去。零位贡献 $0$，在模 $3$ 题里通常要算进和里。

**换成模 $9$ 或模 $11$ 呢？**
模 $9$ 还是同一套数位和；模 $11$ 要改成交替和，或者带长度的前缀加权。
