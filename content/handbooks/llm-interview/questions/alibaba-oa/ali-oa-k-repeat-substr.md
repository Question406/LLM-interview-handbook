---
id: ali-oa-k-repeat-substr
section: alibaba-oa
order: 25
level: S
title: 淘天 0515：01 串里出现至少 $k$ 次的不同子串有多少？
quick: >-
  说白了就是「出现次数 $\ge k$ 的不同子串个数」。用后缀自动机 / 后缀数组统计 `endpos` 大小，把满足阈值的状态或高度区间加起来。
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

## 真题记录

- 公司 / 场次：淘天笔试 0515（公开回忆）
- 题意：$01$ 串，统计出现次数 $\ge k$ 的不同子串个数。

## 题面

给定 $01$ 串 $s$ 和正整数 $k$，统计有多少个**不同**的非空子串（连续子串）在 $s$ 中出现次数至少为 $k$。出现位置可以重叠。

输入假设：第一行 $n,k$，第二行 $s$。公开回忆常按 $n$ 到 $10^5$ 量级理解，因此不能把所有子串丢进 `set`。

输出：一个整数。

## 思路

不同子串最多 $n(n+1)/2$ 个，枚举会爆。需要按「出现次数」批量统计。

后缀自动机（SAM）里，每个状态代表一段结束位置集合 `endpos` 相同的子串，这些子串的长度是连续区间 $(\mathrm{len}(\mathrm{link}(v)),\,\mathrm{len}(v)]$。该状态对应子串的出现次数就是 $|\mathrm{endpos}(v)|$。

算法：

1. 把 $s$ 建 SAM。新建实节点 `cnt=1`，clone 节点 `cnt=0`。
2. 按 `len` 降序把 `cnt` 加到 `link` 上，得到每个状态的出现次数。
3. 若 `cnt[v] >= k`，把该状态代表的 $\mathrm{len}[v]-\mathrm{len}[\mathrm{link}[v]]$ 个子串全部计入答案。

这样写是对的：同一 `endpos` 的子串出现次数相同；长度区间互不重叠且覆盖全部本质不同子串。$k=1$ 时退化为不同子串总数，也可写成 $\binom{n+1}{2}-\sum \mathrm{height}$。

后缀数组做法：对 `height` 分组，组内后缀数 $\ge k$ 的那段 LCP 贡献长度。和 SAM 同复杂度量级。

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

边界：$k=1$ 得到全部不同子串数；$k\gt n$ 答案 $0$（任何子串出现次数 $\le n$）；单字符 `0` 在 $k=1$ 时答案 $1$。重叠如 `aaa` 的 `aa` 出现 $2$ 次，SAM 的 `endpos` 会计入。

## 复杂度

SAM 节点数 $O(n)$，对 $01$ 字母表转移 $O(1)$。建自动机 $O(n)$，按长度排序 $O(n\log n)$，也可用桶排做到 $O(n)$。空间 $O(n)$。

## 易错 / 面试追问

- 把所有子串丢进 `set`，$n=10^5$ 内存与时间都爆。
- clone 节点初始 `cnt` 写成 $1$，出现次数翻倍。
- $k=1$ 时用 $\binom{n+1}{2}$ 却忘了减相同子串，或把「出现至少 $k$ 次」理解成「长度至少 $k$」。
- 追问「不重叠出现」：`endpos` 不再够，要改成贪心选点或 DP，不是本题。
