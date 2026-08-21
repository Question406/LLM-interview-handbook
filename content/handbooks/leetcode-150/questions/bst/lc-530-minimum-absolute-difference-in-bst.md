---
id: lc-530-minimum-absolute-difference-in-bst
section: bst
order: 1
level: A
title: LC 530 · 二叉搜索树的最小绝对差
quick: >-
  BST 中序是递增序列，最小差一定出现在相邻两个中序值之间。扫一遍维护前驱即可。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - BST
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 530. 二叉搜索树的最小绝对差
    url: https://leetcode.cn/problems/minimum-absolute-difference-in-bst/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

二叉搜索树至少两个节点，返回任意两节点值差的绝对值的最小值。

## 思路

有序数组里最小相邻差就是全局最小差。BST 中序恰好有序，所以只需比中序相邻。维护 `prev`，每次 `min(ans, node.val - prev)`。

不要枚举所有点对。值非负，减法不用再取绝对。LC 783 是同一题。

## 参考代码

```python
from __future__ import annotations

from typing import Optional


class TreeNode:
    def __init__(
        self,
        val: int = 0,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ):
        self.val = val
        self.left = left
        self.right = right


def getMinimumDifference(root: Optional[TreeNode]) -> int:
    prev: Optional[int] = None
    ans = 10**18

    def dfs(node: Optional[TreeNode]) -> None:
        nonlocal prev, ans
        if node is None:
            return
        dfs(node.left)
        if prev is not None:
            ans = min(ans, node.val - prev)
        prev = node.val
        dfs(node.right)

    dfs(root)
    return ans


if __name__ == "__main__":
    root = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6))
    assert getMinimumDifference(root) == 1
    root2 = TreeNode(1, None, TreeNode(3, TreeNode(2)))
    assert getMinimumDifference(root2) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(h)$；Morris 中序可到 $O(1)$。

## 边界

- 只有两个节点：答案就是二者之差。
- 父子差很大、跨层更小：中序相邻仍能抓到，例如 $1$ 与 $3$ 分居根的两侧。
- 退化成链：中序就是这条链的递增序，扫相邻即可。

## 追问

- **普通二叉树、不是 BST？** 中序不再有序，最小差可能出现在不相邻的中序位置。收集全部值排序后扫相邻，时间 $O(n\log n)$；或值域不大时桶。不要只比父子边——最优对可以隔代。

```python
def getMinimumDifference(root):
    vals = []

    def dfs(node):
        if node is None:
            return
        vals.append(node.val)
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    vals.sort()
    return min(vals[i] - vals[i - 1] for i in range(1, len(vals)))
```

- **第 $k$ 小的相邻差？** 先中序得到有序数组 $a$，相邻差 $a[i]-a[i-1]$ 放进列表再排序取第 $k$ 个，时间 $O(n\log n)$。若问任意两点差的第 $k$ 小，那是另一题（对差二分 + 双指针数对），不再是「只看中序相邻」。LC 783 与本题相同，讲最小相邻差即可。
