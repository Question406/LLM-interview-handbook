---
id: lc-124-binary-tree-maximum-path-sum
section: binary-tree
order: 11
level: S
title: LC 124 · 二叉树中的最大路径和
quick: >-
  后序 DFS，每个节点向父节点返回单边贡献
  $\max(0,\text{左},\text{右})+\text{根}$，因为往上接的路径不能分叉；同时用「左贡献 $+$ 右贡献 $+$
  根」更新全局答案，完整路径可以在当前节点连接两侧。负贡献当 $0$ 不选。时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 124. 二叉树中的最大路径和
    url: 'https://leetcode.cn/problems/binary-tree-maximum-path-sum/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定非空二叉树，找出节点值之和最大的路径。路径由至少一个节点组成，相邻节点之间必须有树边连接，并且每个节点至多出现一次。起点和终点可以是任意节点，路径不必经过根，也不要求端点是叶节点。

### 输入与输出

实现 `maxPathSum(root) -> int`。输入是二叉树根节点，返回最大路径和，不需要返回路径本身。节点值可以全为负数，但不能选择空路径。

### 约束

- 节点数在 1 到 `3 * 10^4` 之间。
- `-1000 <= Node.val <= 1000`。
- 示例用层序序列表示树，null 表示缺失的孩子。

### 示例

```text
输入：root = [1,2,3]
输出：6
```

[LeetCode 原题](https://leetcode.com/problems/binary-tree-maximum-path-sum/description/)

## 解题思路与参考答案

## 题意

路径是树上从任意节点到任意节点的一条无环链，可以不经过根。返回路径上节点值之和的最大值。节点值可以是负数。

## 思路

我会用后序 DFS，让每个节点同时做两件事。一件是给父节点返回单边贡献：根值加上左右贡献里非负的较大者，因为父节点那条路径往下只能走一边，不能同时走左右。另一件是在本节点把左右两边都接上，用「左贡献 $+$ 右贡献 $+$ 根」更新全局答案，最优路径在这里拐弯的情况就记下来了。

负贡献直接当 $0$，等于不走那条边。全是负数时，答案就是最大的那个节点值。

拿示例 `[-10, 9, 20, null, null, 15, 7]` 算一下。$15$ 和 $7$ 是叶子，贡献就是自己。到 $20$ 时，全局候选是 $15+7+20=42$，往上返回 $20+\max(15,7)=35$。到根 $-10$ 时，候选是 $9+35-10=34$，比 $42$ 小，所以答案是 $42$，这条路径没有经过根。

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


def maxPathSum(root: Optional[TreeNode]) -> int:
    ans = -(10**18)

    def dfs(node: Optional[TreeNode]) -> int:
        nonlocal ans
        if node is None:
            return 0
        left = max(0, dfs(node.left))
        right = max(0, dfs(node.right))
        ans = max(ans, left + right + node.val)
        return node.val + max(left, right)

    dfs(root)
    return ans


if __name__ == "__main__":
    assert maxPathSum(TreeNode(1, TreeNode(2), TreeNode(3))) == 6
    root = TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert maxPathSum(root) == 42
    assert maxPathSum(TreeNode(-3)) == -3
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert maxPathSum(TreeNode(1, TreeNode(2), TreeNode(3))) == 6
root = TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
assert maxPathSum(root) == 42
assert maxPathSum(TreeNode(-3)) == -3
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

后序遍历每个节点常数次，时间 $O(n)$，额外空间 $O(h)$。

## Edge Cases

单节点（包括负数）时答案就是这个值。全是负数时，负的边都被丢掉，全局取的仍是最大的那个节点，不会拼出更负的路径。最优路径不过根时，它已经在某棵子树内部以「左贡献 $+$ 右贡献 $+$ 子根」的形式写进全局了。

## 追问

**如果路径必须从根出发呢？**
那父节点不能同时接左右，只保留单边贡献 `node.val + max(0, 左, 右)`。DFS 一遍，全局记这些单边返回值的最大值就行，不再算 `left+right+val`。空树另行约定。

```python
def maxPathFromRoot(root):
    ans = -(10**18)

    def dfs(node):
        nonlocal ans
        if node is None:
            return 0
        gain = node.val + max(0, dfs(node.left), dfs(node.right))
        ans = max(ans, gain)
        return gain

    dfs(root)
    return ans
```

**只统计根到叶的路径呢？**
和 LC 129 同一个骨架：往下累加，到叶子才用当前和更新答案，非叶子不结算。节点可负，所以不能半路剪枝。独立卡见 `lc-129-sum-root-to-leaf-numbers`。

```python
def maxRootToLeaf(root):
    ans = -(10**18)

    def dfs(node, acc):
        nonlocal ans
        if node is None:
            return
        acc += node.val
        if node.left is None and node.right is None:
            ans = max(ans, acc)
            return
        dfs(node.left, acc)
        dfs(node.right, acc)

    dfs(root, 0)
    return ans
```
