---
id: lc-198-house-robber
section: dp-1d
order: 3
level: S
title: LC 198 · 打家劫舍
quick: 每家只有抢和不抢两种选择：不抢就保留此前的最大金额，抢就接上前前一家为止的最大金额，两者取大。只要存前两个状态，时间 $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 198. House Robber
    url: 'https://leetcode.com/problems/house-robber/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

街道一侧有一排房屋，nums[i] 表示第 i 间房存放的金额。选择若干间房取得其中的金额，但不能同时选择相邻两间，否则会触发警报。请返回在不触发警报的前提下能取得的最大总金额。

### 输入与输出

实现 `rob(nums: List[int]) -> int`。下标体现房屋的先后位置；首尾房屋不额外相邻，这里是一条直线而不是环。只返回金额，不需要返回房屋下标。

### 约束

- `1 <= len(nums) <= 100`。
- `0 <= nums[i] <= 400`。

### 示例

```text
输入：nums = [1,2,3,1]
输出：4
```

示例可以选择第 0 和第 2 间房，合计 1+3=4；不能同时选择第 1 和第 2 间。

## 解题思路与参考答案

## 题意

一排房屋，`nums[i]` 是第 $i$ 家的金额（非负），相邻两家不能同时抢。求能抢到的最大金额。$1\le n\le 100$。

## 思路

这是一维 DP，因为每家的决定只和前两家的最优结果有关。$dp[i]$ 表示只考虑前 $i$ 家（下标 $0..i-1$）能抢到的最大值。轮到第 $i-1$ 家时只有两种选择：不抢，就继承 $dp[i-1]$；抢，上一家必须空着，得到 $dp[i-2]+nums[i-1]$。

$dp[i]=\max(dp[i-1],\ dp[i-2]+nums[i-1])$，$dp[0]=0$，$dp[1]=nums[0]$。

算当前值只用到前两个状态，所以不用存整个数组。`prev1` 记此前能抢到的最大金额，`prev2` 记再往前一家的最大金额，读到下一家时比一比抢和不抢哪个好，再更新这两个值。

拿 `[2,7,9,3,1]` 走一遍：前两家最多抢到 7。看到 9，抢它可以和第一家的 2 相加得 11，比不抢的 7 好。看到 3，抢它只能接前两家的 7，得 10，比 11 小，保留 11。最后一家是 1，接上此前的 11，最终是 12。

「隔一家抢一家」的贪心是错的，比如 `[2,1,1,2]` 最优是抢首尾，中间隔了 $3$。

## 参考代码

```python
from typing import List


def rob(nums: List[int]) -> int:
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1


if __name__ == "__main__":
    assert rob([1, 2, 3, 1]) == 4
    assert rob([2, 7, 9, 3, 1]) == 12
    assert rob([5]) == 5
    assert rob([2, 1]) == 2
    assert rob([2, 1, 1, 2]) == 4
    assert rob([0, 0, 0]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert rob([1, 2, 3, 1]) == 4
assert rob([2, 7, 9, 3, 1]) == 12
assert rob([5]) == 5
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

只有 $1$ 间时，答案就是这间的金额。

两间时取较大的，$\max(nums[0], nums[1])$。

最优解间隔超过 $2$ 的情况，比如 `[2,1,1,2]`，DP 会自己选择连续跳过两家，按奇偶分组的贪心会算错。

## 追问

**房子围成一圈怎么办（LC 213）？**
首尾相邻，不能同时抢，就拆成两次线性：`nums[:-1]`（不抢最后一家）和 `nums[1:]`（不抢第一家），取较大的。$n=1$ 单独返回，时间还是 $O(n)$。

```python
def robII(nums):
    def rob_line(a):
        prev2 = prev1 = 0
        for x in a:
            prev2, prev1 = prev1, max(prev1, prev2 + x)
        return prev1

    if len(nums) == 1:
        return nums[0]
    return max(rob_line(nums[:-1]), rob_line(nums[1:]))
```

**相邻关系换成树呢（LC 337）？**
每个结点返回 `(不抢该点, 抢该点)` 两个值。不抢等于左右儿子各取 $\max$ 再相加；抢等于该点值加上左儿子不抢、右儿子不抢。后序遍历一遍，时间 $O(n)$。

```python
def robIII(root):
    def dfs(node):
        if not node:
            return (0, 0)
        ls, lt = dfs(node.left)
        rs, rt = dfs(node.right)
        return (max(ls, lt) + max(rs, rt), node.val + ls + rs)

    return max(dfs(root))
```
