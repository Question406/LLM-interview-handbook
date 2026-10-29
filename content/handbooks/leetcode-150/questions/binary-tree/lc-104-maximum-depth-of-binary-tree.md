---
id: lc-104-maximum-depth-of-binary-tree
section: binary-tree
order: 1
level: S
title: LC 104 · 二叉树的最大深度
quick: >-
  用后序 DFS：空树返回 $0$，否则深度是 $1+\max(\text{左深},\text{右深})$，层序 BFS 数层数也行。每个节点看一次，时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 104. 二叉树的最大深度
    url: 'https://leetcode.cn/problems/maximum-depth-of-binary-tree/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定二叉树根节点 root，返回树的最大深度。深度按从根到某个叶子的一条路径所经过的节点数计量，叶子是没有左右孩子的节点；取所有这种路径中的最大值。

### 接口与输出

实现 `maxDepth(root: Optional[TreeNode]) -> int`。节点包含 `val`、`left`、`right`。空树深度为 0，只有根节点的树深度为 1。

### 合法输入与约束

节点数为 0 到 10000，`-100 <= Node.val <= 100`。节点值不影响深度，树可以只有左链或只有右链。示例层序数组中的 `null` 表示空孩子。

### 示例

```text
输入：root = [3,9,20,null,null,15,7]
输出：3
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/maximum-depth-of-binary-tree/description/)。

## 解题思路与参考答案

## 题意

给一棵二叉树的根节点，返回它的最大深度，也就是根到最远叶子那条路径上的节点个数。空树深度为 $0$。

## 思路

我会直接写后序 DFS，因为一棵树有多深只取决于左右子树有多深：先求左右子树各自的深度，当前深度就是 $1$ 加上较大的那个。空节点返回 $0$，叶子自然就返回 $1$。

拿示例那棵树走一遍。根是 $3$，左孩子 $9$ 是叶子，深度 $1$；右孩子 $20$ 下面挂着 $15$ 和 $7$，两个都是叶子，所以 $20$ 这棵子树深度是 $2$。回到根，$1+\max(1,2)=3$。

层序 BFS 数层数也能做。面试里我会先写递归，再补一句：链状树上递归栈最坏会到 $O(n)$。

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


def maxDepth(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert maxDepth(root) == 3
    assert maxDepth(None) == 0
    assert maxDepth(TreeNode(1, None, TreeNode(2))) == 2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
assert maxDepth(root) == 3
assert maxDepth(None) == 0
assert maxDepth(TreeNode(1, None, TreeNode(2))) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每个节点只访问一次，时间 $O(n)$。额外空间是递归栈 $O(h)$，$h$ 是树高，最坏链状时是 $O(n)$。

## Edge Cases

空树直接返回 $0$。只有根一个节点时深度是 $1$。只有左链或只有右链的树，深度就等于节点数。

## 追问

**改成最小深度（LC 111）怎么写？**
把 $\max$ 直接换成 $\min$ 是错的。空孩子返回 $0$，单侧树上 `min(左, 0)+1` 会得到 $1$，等于把缺失的那一边当成了叶子。最小深度是根到最近叶子的节点数，所以只有一侧孩子时必须走进那一侧，两侧都有才取较小。用 BFS 的话，第一次碰到叶子就是答案，偏斜树上往往比 DFS 早停。

```python
from collections import deque


def minDepth(root):
    if root is None:
        return 0
    q = deque([(root, 1)])
    while q:
        node, d = q.popleft()
        if node.left is None and node.right is None:
            return d
        if node.left:
            q.append((node.left, d + 1))
        if node.right:
            q.append((node.right, d + 1))
```

```python
def minDepth_dfs(root):
    if root is None:
        return 0
    if root.left is None:
        return 1 + minDepth_dfs(root.right)
    if root.right is None:
        return 1 + minDepth_dfs(root.left)
    return 1 + min(minDepth_dfs(root.left), minDepth_dfs(root.right))
```

**能不能用迭代求最大深度？**
能。DFS 版用栈存 `(node, depth)`，弹出时用当前深度更新答案，左右孩子带着 `depth+1` 入栈。BFS 版按层切，每处理完一层 `ans += 1`，队列掏空时就是最大深度。两种时间都是 $O(n)$；BFS 额外空间是 $O(w)$，链状树上栈或递归是 $O(n)$。
