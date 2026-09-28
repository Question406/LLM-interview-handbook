---
id: lc-112-path-sum
section: binary-tree
order: 9
level: A
title: LC 112 · 路径总和
quick: >-
  DFS 往下减：到达叶子且剩余等于节点值则为真。空树假。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 112. 路径总和
    url: https://leetcode.cn/problems/path-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断是否存在一条根到叶的路径，节点值之和等于 `targetSum`。必须走到叶子。

## 思路

递归带剩余和。当前是叶子时，判断 `remain == node.val`。否则左右只要有一侧能走通即可。空节点返回假。

非叶子上剩余为 $0$ 仍要继续往下走，题目要根到叶整条路径。节点可负，剩余已负也不能剪枝。

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


def hasPathSum(root: Optional[TreeNode], targetSum: int) -> bool:
    if root is None:
        return False
    if root.left is None and root.right is None:
        return targetSum == root.val
    remain = targetSum - root.val
    return hasPathSum(root.left, remain) or hasPathSum(root.right, remain)


if __name__ == "__main__":
    root = TreeNode(
        5,
        TreeNode(4, TreeNode(11, TreeNode(7), TreeNode(2))),
        TreeNode(8, TreeNode(13), TreeNode(4, None, TreeNode(1))),
    )
    assert hasPathSum(root, 22)
    assert not hasPathSum(TreeNode(1, TreeNode(2), TreeNode(3)), 5)
    assert not hasPathSum(None, 0)
    print("ok")
```

## 复杂度

时间 $O(n)$，最坏看完整棵树。额外空间 $O(h)$。

## 边界

- 空树：假，即使 `targetSum=0`。
- 单节点：等于目标和为真，否则假。
- 含负数：剩余可能先变小再变大，不能因「已负」剪枝。

## 追问

- **列出所有根到叶路径（LC 113）？** 同一 DFS 骨架改成回溯：往下走时把节点推进 `path`、减去值；到叶子且剩余为 $0$ 就拷一份进答案；回溯必须 `pop`。不要在非叶子提前收集。时间 $O(n)$ 遍历，输出额外按路径条数和长度计。

```python
def pathSum(root, targetSum):
    ans, path = [], []

    def dfs(node, remain):
        if node is None:
            return
        path.append(node.val)
        remain -= node.val
        if node.left is None and node.right is None and remain == 0:
            ans.append(path[:])
        else:
            dfs(node.left, remain)
            dfs(node.right, remain)
        path.pop()

    dfs(root, targetSum)
    return ans
```

- **任意向下路径、不必从根也不必到叶（LC 437）？** 前缀和 + 哈希。DFS 维护根到当前的累加 `acc`，答案加上「已经出现过 `acc - target` 的次数」，再把 `acc` 放进计数；左右递归完回撤 `cnt[acc] -= 1`，避免串到另一枝。空节点不计。时间 $O(n)$。注意路径是向下的，不是任意两点；节点可负，所以哈希里同一前缀可能多次。

```python
from collections import defaultdict

def pathSum(root, targetSum):
    cnt = defaultdict(int)
    cnt[0] = 1
    ans = 0

    def dfs(node, acc):
        nonlocal ans
        if node is None:
            return
        acc += node.val
        ans += cnt[acc - targetSum]
        cnt[acc] += 1
        dfs(node.left, acc)
        dfs(node.right, acc)
        cnt[acc] -= 1

    dfs(root, 0)
    return ans
```
