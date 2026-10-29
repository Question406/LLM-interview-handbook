---
id: ali-oa-nearest-prime
section: alibaba-oa
order: 17
level: B
title: 阿里春招 0401：离 $x$ 最近的质数，同距如何破？
quick: >-
  距离从 $0$ 往外扩，每个距离先测 $x-d$ 再测 $x+d$，第一个命中的就是最近的，同距时自然取到较小的。判质用试除，只试 $6k\pm 1$，试到
  $\sqrt{v}$。
tags:
  - Alibaba
  - OA
  - 数论
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阿里系列 2026.04.01 算法岗机试
    url: >-
      https://leetcode.cn/discuss/post/3943532/chun-zhao-bi-shi-a-li-xi-lie-ji-shi-fu-p-t91w/
    type: secondary
---

## 题目描述

给定整数 x，找到距离 x 最近的质数。质数指大于 1、只有 1 和自身两个正因数的整数。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `nearest_prime(x)`；辅助接口 `is_prime(v)` 返回 v 是否为质数。x 为整数，允许 x 小于 2；若输入多组整数，分别输出答案。

### 输出与约束

返回使绝对差最小的质数；若左右两侧等距，返回较小的那个。x 已为质数时返回自身。公开复盘未给出精确数值上界，本卡不据此编造范围。

### 示例

```text
nearest_prime(7) -> 7
nearest_prime(4) -> 3（3与5等距，取较小者）
nearest_prime(1) -> 2
is_prime(25) -> False
```

## 解题思路与参考答案

我会从 $d=0$ 开始往外扩，每个距离先看左边 $x-d$、再看右边 $x+d$，第一次碰到质数就返回。$d$ 从小到大保证距离最近，先左后右保证同距时取较小的那个。

## 真题记录

阿里系列 2026.04.01 算法岗机试第 2 题：找质数 $p$ 使 $|p-x|$ 最小，并列时取更小的 $p$。

## 题面

对每个整数 $x$，找与 $x$ 距离最近的质数 $p$，使 $|p-x|$ 最小；若左右两侧存在同距离质数，取较小的那个。

输入是若干个 $x$，每个输出对应的质数。公开复盘里数值大约在常见整型范围，没有写死上界。

## 思路

同一个距离 $d$ 上最多两个候选，$x-d$ 和 $x+d$。题目要同距取小，所以先查左端 $x-d$（必须 $\gt 1$），再查右端。比如 $x=4$，$d=1$ 时左边 $3$、右边 $5$ 都是质数，先查左边，输出 $3$。

判质用试除：$\le 1$ 不是质数，$2,3$ 特判，之后只试 $6k\pm 1$ 形式的除数，试到 $\sqrt{v}$ 为止。

质数在整数轴上没有上界，所以循环一定会停。$x\le 1$ 时左边没有合法质数，只会往右找到 $2$。询问很多、而且 $x$ 落在固定上界内时，再考虑线性筛；数据范围不大，试除就够了。

## 参考代码

```python
import sys


def is_prime(v):
    if v <= 1:
        return False
    if v <= 3:
        return True
    if v % 2 == 0 or v % 3 == 0:
        return False
    i = 5
    while i * i <= v:
        if v % i == 0 or v % (i + 2) == 0:
            return False
        i += 6
    return True


def nearest_prime(x):
    d = 0
    while True:
        left = x - d
        if left > 1 and is_prime(left):
            return left
        right = x + d
        if d > 0 and is_prime(right):
            return right
        if d == 0 and is_prime(x):
            return x
        d += 1


def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    i = 0
    if len(data) > 1:
        # 兼容「先 T 再 T 个 x」以及「直接若干 x」
        if data[0] == len(data) - 1:
            xs = data[1:]
        else:
            xs = data
    else:
        xs = data
    for x in xs:
        print(nearest_prime(x))


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

选已经是质数、左右等距和小于 2 的输入。4 到 3 和 5 等距，应优先返回较小的 3。

```python
assert nearest_prime(7) == 7
assert nearest_prime(4) == 3
assert nearest_prime(1) == 2
assert not is_prime(25)
print("simple tests passed")
```

## 复杂度

单次询问的最坏代价和「到附近质数的间隙 $\times$ 试除 $\sqrt{x}$」有关，对普通 $32$ 位整数足够。多询问且值域小时，先筛到 $\mathrm{MAX}+\Delta$，再对每个 $x$ 左右各走一步。

## Edge Cases

$x=1$ 或 $x\le 0$ 得到 $2$；$x=4$ 时 $3$ 与 $5$ 同距，输出 $3$；$x=8$ 输出 $7$。$x$ 本身是质数时 $d=0$ 直接返回。

## 追问

**同距时先查了右边会怎样？**
会输出较大的那个，违反同距取小。

**`is_prime` 最容易错在哪？**
把 $1$ 判成质数，或者对偶数只排除了 $2$、忘了 $3$。

**$x$ 是负数怎么办？**
别对负数取模或开方，左侧候选必须 $\gt 1$。

**怎么说明循环一定有上界？**
可以提贝特朗-切比雪夫定理，它保证 $(x,2x)$ 内有质数，用来说明循环有上界。实现还是向外扩。
