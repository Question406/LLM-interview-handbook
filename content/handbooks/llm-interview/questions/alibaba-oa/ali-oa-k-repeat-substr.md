---
id: ali-oa-k-repeat-substr
section: alibaba-oa
order: 25
level: S
title: 淘天 0515：01 串里出现至少 $k$ 次的不同子串有多少？
quick: >-
  用后缀自动机：每个状态代表一批 `endpos` 相同的子串，出现次数就是 `endpos` 的大小。把 `cnt` 沿 `link` 累加后，凡是 `cnt` $\ge k$ 的状态，就把它代表的子串个数加进答案；后缀数组按 `height` 分组也能做。
tags:
  - Alibaba
  - OA
  - 字符串
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

给定一个二进制字符串 s 和正整数 k，统计其中有多少种不同的非空连续子串至少出现 k 次。出现位置可以重叠；内容相同而位置不同的子串算同一种。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

本卡接口为 `SAM()` 新建对象，按原顺序对每个字符调用 `extend(c)`，最后调用一次 `count_at_least(k)`。也可通过 main 输入 n、k、s，其中 n 为字符串长度。

### 输出与约束

返回不同子串的数量，而不是满足条件的出现位置数。k=1 时统计全部不同非空子串；k 大于任一子串的出现次数时结果为 0。每次独立查询重新构建对象，当前计数接口会累计内部状态。

### 示例

```text
s="000", k=2 -> 2
满足要求的内容为 "0"（出现3次）、"00"（出现2次）。
s="01", k=1 -> 3
```

## 解题思路与参考答案

我会用后缀自动机（SAM）按出现次数批量统计。SAM 的每个状态代表一组结束位置完全相同的子串，它们出现次数相同，所以只要算出每个状态的 `endpos` 大小，把满足 $\ge k$ 的状态所代表的子串个数加起来就行。

## 真题记录

淘天笔试 0515 的公开回忆：$01$ 串，统计出现次数 $\ge k$ 的不同子串个数。

## 题面

给定 $01$ 串 $s$ 和正整数 $k$，统计有多少个不同的非空子串（连续子串）在 $s$ 中出现次数至少为 $k$。出现位置可以重叠。

输入假设第一行是 $n,k$，第二行是 $s$。公开回忆常按 $n$ 到 $10^5$ 量级理解，因此不能把所有子串丢进 `set`。输出一个整数。

## 思路

不同子串最多有 $n(n+1)/2$ 个，一个个枚举会爆，需要按「出现次数」批量统计。

SAM 里每个状态对应一批 `endpos`（结束位置集合）相同的子串，它们的长度是一段连续区间 $(\mathrm{len}(\mathrm{link}(v)),\,\mathrm{len}(v)]$，出现次数都等于 $|\mathrm{endpos}(v)|$。重叠的出现也算，比如 `aaa` 里的 `aa` 出现 $2$ 次，SAM 的 `endpos` 会把两次都计入。

具体分三步。先把 $s$ 建成 SAM，新建的实节点 `cnt=1`，clone 节点 `cnt=0`。然后按 `len` 降序把 `cnt` 加到 `link` 上，得到每个状态的出现次数。最后凡是 `cnt[v] >= k`，就把这个状态代表的 $\mathrm{len}[v]-\mathrm{len}[\mathrm{link}[v]]$ 个子串全部计入答案。

这样不重不漏：同一 `endpos` 的子串出现次数相同，各状态的长度区间互不重叠，合起来正好覆盖所有本质不同的子串。$k=1$ 时退化成不同子串总数，也可以写成 $\binom{n+1}{2}-\sum \mathrm{height}$。

后缀数组也能做：对 `height` 分组，组内后缀数 $\ge k$ 的那段 LCP 贡献长度，复杂度和 SAM 在同一个量级。

## 参考代码

```python
import sys


class SAM:
    def __init__(self):
        self.next = [{}]
        self.link = [-1]
        self.length = [0]
        self.cnt = [0]
        self.last = 0

    def extend(self, c):
        cur = len(self.next)
        self.next.append({})
        self.link.append(0)
        self.length.append(self.length[self.last] + 1)
        self.cnt.append(1)
        p = self.last
        while p != -1 and c not in self.next[p]:
            self.next[p][c] = cur
            p = self.link[p]
        if p == -1:
            self.link[cur] = 0
        else:
            q = self.next[p][c]
            if self.length[p] + 1 == self.length[q]:
                self.link[cur] = q
            else:
                clone = len(self.next)
                self.next.append(self.next[q].copy())
                self.link.append(self.link[q])
                self.length.append(self.length[p] + 1)
                self.cnt.append(0)
                while p != -1 and self.next[p].get(c) == q:
                    self.next[p][c] = clone
                    p = self.link[p]
                self.link[q] = self.link[cur] = clone
        self.last = cur

    def count_at_least(self, k):
        order = sorted(range(len(self.next)), key=lambda v: self.length[v], reverse=True)
        for v in order:
            if self.link[v] != -1:
                self.cnt[self.link[v]] += self.cnt[v]
        ans = 0
        for v in range(1, len(self.next)):
            if self.cnt[v] >= k:
                parent = self.length[self.link[v]] if self.link[v] != -1 else 0
                ans += self.length[v] - parent
        return ans


def main():
    data = sys.stdin.read().split()
    if len(data) >= 3:
        n, k, s = int(data[0]), int(data[1]), data[2]
        s = s[:n]
    elif len(data) == 2:
        k, s = int(data[0]), data[1]
    else:
        return
    sam = SAM()
    for ch in s:
        sam.extend(ch)
    print(sam.count_at_least(k))


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

aaa 的不同非空子串是 a、aa、aaa，其中至少出现两次的只有 a 与 aa，计数包含重叠出现。计数会修改 SAM 内部累计值，每个场景重新构建。

```python
for k, expected in [(1, 3), (2, 2), (4, 0)]:
    sam = SAM()
    for ch in "aaa":
        sam.extend(ch)
    assert sam.count_at_least(k) == expected
print("simple tests passed")
```

## 复杂度

SAM 节点数 $O(n)$，对 $01$ 字母表转移 $O(1)$。建自动机 $O(n)$，按长度排序 $O(n\log n)$，用桶排可以做到 $O(n)$。空间 $O(n)$。

## 边界

$k=1$ 得到全部不同子串数；$k\gt n$ 时答案是 $0$，因为任何子串出现次数都 $\le n$；单字符 `0` 在 $k=1$ 时答案是 $1$。

## 追问

**把所有子串丢进 `set` 行吗？**
$n=10^5$ 时内存和时间都会爆。

**clone 节点的 `cnt` 初值写成 $1$ 会怎样？**
出现次数会翻倍。clone 节点初值必须是 $0$，只有新建的实节点是 $1$。

**$k=1$ 时直接用 $\binom{n+1}{2}$ 可以吗？**
不行，要减去重复的子串，也就是减 $\sum \mathrm{height}$。另外别把「出现至少 $k$ 次」看成「长度至少 $k$」。

**如果要求不重叠地出现呢？**
`endpos` 就不够用了，要改成贪心选点或 DP，那不是本题。
