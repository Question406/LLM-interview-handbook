---
id: ali-algo-edit-distance
section: alibaba-oa
order: 32
level: A
title: 阿里手撕：编辑距离的 state 和 base cases 怎么写？
quick: >-
  用二维 DP，`dp[i][j]` 是把 $a$ 前 $i$ 个字符变成 $b$ 前 $j$ 个的最少操作数。字符相等就继承对角，不等就在删、插、改里取
  min 再加一。empty-string boundaries 就是 $i$ 或 $j$。
tags:
  - Alibaba
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 编辑距离
    url: 'https://leetcode.cn/problems/edit-distance/'
    type: primary
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
---

## 题目描述

给定两个字符串，求把第一个字符串变成第二个字符串所需的最少编辑次数。一次编辑可以插入一个字符、删除一个字符，或把一个字符替换成另一个字符，每次代价均为 1。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `min_distance(word1, word2)` 和返回同样答案的 `min_distance_1d(word1, word2)`。两个参数都是字符串，可以为空。

### 输出与约束

返回一个非负整数，不要求返回具体编辑过程；两个字符串相同时答案为 0。输入内容不得被修改。

### 示例

```text
输入：word1 = "horse", word2 = "ros"
输出：3
输入：word1 = "", word2 = "abc"
输出：3
```

## 解题思路与参考答案

## 真题 / 考点说明

- 对应：LeetCode 72，阿里校招 DP 深挖题

我会用二维 DP，状态 `dp[i][j]` 是把 $a$ 的前 $i$ 个字符变成 $b$ 的前 $j$ 个字符的最少操作数。base cases 很好记：长度为 $i$ 的前缀变成空串要删 $i$ 次，空串变成长度为 $i$ 的串就是插 $i$ 次。

## 思路

先填第 $0$ 行和第 $0$ 列。然后对每个 `(i,j)` 看最后一个字符：若 `a[i-1]==b[j-1]`，直接继承对角的 `dp[i-1][j-1]`；不相等，就在「删 $a$ 一个 / 插 $b$ 一个 / 改当前」三者里取最小再加一。

拆开写，删 = `dp[i-1][j]+1`，插 = `dp[i][j-1]+1`，改 = `dp[i-1][j-1]+[a[i-1]\neq b[j-1]]`。两个字符已经相等时，改的代价是 $0$，别多加一。合起来就是：

$$
dp[i][j]=\min\bigl(dp[i-1][j]+1,\; dp[i][j-1]+1,\; dp[i-1][j-1]+[a_{i-1}\neq b_{j-1}]\bigr)
$$

要省空间可以滚动成一维，但必须从右往左，或者留着上一行，否则对角那个还要用的值会被盖掉。

## 参考代码

```python
def min_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1],
                )
    return dp[m][n]


def min_distance_1d(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[n]


if __name__ == "__main__":
    assert min_distance("horse", "ros") == 3
    assert min_distance("intention", "execution") == 5
    assert min_distance("", "abc") == 3
    assert min_distance("abc", "") == 3
    assert min_distance("", "") == 0
    assert min_distance_1d("horse", "ros") == 3
    print("ok")
```

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert min_distance("horse", "ros") == 3` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 复杂度

二维版本时间 $O(mn)$、空间 $O(mn)$。滚动两行或一行，时间还是 $O(mn)$，空间降到 $O(\min(m,n))$。只要距离、不要路径，就不用回溯。

## 追问

**空串怎么处理？**
空串对空串是 $0$；一侧为空，答案等于另一侧的长度。

**如果只允许插入和删除呢？**
这是 LCS 的对偶，最少操作 $= m+n-2\cdot\mathrm{LCS}$。

**放到搜索纠错里怎么用？**
编辑距离只是召回候选的代价。我一般先用倒排或 ngram 召回，再算编辑距离，加上词典先验，P99 超时就截断。不要对全词典两两 DP。
