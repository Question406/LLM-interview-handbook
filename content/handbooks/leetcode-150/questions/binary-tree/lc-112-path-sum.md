---
id: lc-112-path-sum
section: binary-tree
order: 9
level: A
title: LC 112 · 路径总和
quick: >-
  DFS 带着剩余和往下减，走到叶子时看剩余是否等于叶子的值，左右只要有一侧走通就为真，空树返回假。节点可负，所以中途不剪枝。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 112. 路径总和
    url: 'https://leetcode.cn/problems/path-sum/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定二叉树和目标整数，判断是否存在一条从根节点出发、到某个叶节点结束的路径，其经过的所有节点值之和恰好等于目标。叶节点是没有左右孩子的节点，不能把停在内部节点的路径算成答案。

### 输入与输出

实现 `hasPathSum(root: Optional[TreeNode], targetSum: int) -> bool`。有满足条件的路径返回 `True`，没有则返回 `False`；空树没有根到叶路径。示例的列表是树的层序表示，`null` 表示缺失节点。

### 约束

- 节点数为 0 到 5000。
- 节点值与 `targetSum` 均在 `[-1000,1000]`，允许负值。

### 示例

```text
输入：root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22
输出：true
```

示例存在节点值为 `5 -> 4 -> 11 -> 2` 的根到叶路径，其和为 22。

## 解题思路与参考答案

## 题意

判断是否存在一条从根到叶子的路径，节点值之和等于 `targetSum`。路径必须走到叶子。

## 思路

我会用递归 DFS，每往下走一层就把目标减掉当前节点的值，这样每个节点只需要知道「还差多少」。到了叶子就判断 `remain == node.val`；不是叶子，左右只要有一侧能走通即可。空节点返回假。

拿示例算一下：目标是 $22$，从根 $5$ 往下走 $4$、$11$，剩余变成 $22-5-4-11=2$。$11$ 的左孩子 $7$ 不等于 $2$，右孩子 $2$ 等于 $2$ 而且是叶子，返回真。

有两个地方容易写错。非叶子节点上剩余已经是 $0$，也要继续往下走，因为题目要的是根到叶的整条路径。节点值可以是负数，剩余可能先变小再变大，所以剩余已经为负也不能剪枝。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(
    5,
    TreeNode(4, TreeNode(11, TreeNode(7), TreeNode(2))),
    TreeNode(8, TreeNode(13), TreeNode(4, None, TreeNode(1))),
)
assert hasPathSum(root, 22)
assert not hasPathSum(TreeNode(1, TreeNode(2), TreeNode(3)), 5)
assert not hasPathSum(None, 0)
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

最坏要看完整棵树，时间 $O(n)$，额外空间 $O(h)$。

## Edge Cases

空树返回假，即使 `targetSum=0` 也一样。单节点时，值等于目标和为真，否则为假。

## 追问

**要列出所有满足条件的根到叶路径（LC 113）呢？**
同一个 DFS 骨架改成回溯就行。往下走时把节点推进 `path`、减去值；到叶子且剩余为 $0$，就拷一份进答案；回来时必须 `pop`。不要在非叶子提前收集。遍历是 $O(n)$，输出另外按路径条数和长度计。

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

**路径可以从任意节点开始、在任意节点结束，只要向下（LC 437）呢？**
用前缀和加哈希。DFS 维护根到当前节点的累加和 `acc`，答案加上「已经出现过 `acc - target` 的次数」，再把 `acc` 计入计数；左右递归完要回撤 `cnt[acc] -= 1`，免得前缀串到另一枝上。空节点不计，时间 $O(n)$。这里的路径只能向下，任意两点之间的路径不算；节点可负，所以哈希里同一个前缀可能出现多次。

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
