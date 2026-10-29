---
id: lc-236-lowest-common-ancestor-of-a-binary-tree
section: binary-tree-dfs
order: 6
level: S
title: LC 236 · 二叉树的最近公共祖先
quick: >-
  普通二叉树没法按值走单路，用后序递归两边都搜：碰到 `p`/`q` 或空就返回自己，左右都非空则当前就是 LCA，只有一侧非空答案就在那一侧。时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 236. Lowest Common Ancestor of a Binary Tree
    url: 'https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定一棵普通二叉树的根节点 `root`，以及树中两个不同的节点对象 `p`、`q`，找出它们的最近公共祖先。一个节点的祖先包含它自己；最近公共祖先是所有同时包含 p、q 的子树根中，距离根最深的那个节点。树不保证是二叉搜索树。

### 输入与输出

实现 `lowestCommonAncestor(root, p, q) -> TreeNode`，返回树中原有的那个祖先节点对象，而不是只返回其值或创建新节点。示例为了展示方便以 p、q 的节点值标识它们，输出也展示返回节点的值；实际接口传入节点引用。

### 约束

- 节点数在 2 到 `10^5` 之间。
- `-10^9 <= Node.val <= 10^9`，所有节点值互不相同。
- p、q 保证存在于树中，且是两个不同的节点。
- 示例的 root 是层序序列，null 表示缺失的孩子。

### 示例

```text
输入：root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
输出：3
```

[LeetCode 原题](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/description/)

## 解题思路与参考答案

## 题意

在普通二叉树里找 `p` 和 `q` 的最近公共祖先。题保证节点都在树上；一个节点可以是自己的祖先。值互异。

## 思路

我会用后序递归，因为一个节点是不是 LCA，要等左右子树都报告完才知道。当前节点是 `None`、`p` 或 `q` 就直接返回自己。否则左右都递归：两侧都找到了，说明 `p`、`q` 分居两边，当前就是 LCA；只有一侧非空，答案在那一侧。

拿测试里的树 `[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]` 找 7 和 4：节点 2 的左子树返回 7、右子树返回 4，两边都非空，2 就是 LCA；往上传，5 只收到右侧的 2，原样返回；根 3 只有左侧非空，最终答案是 2。

常见误区是当成 BST，用值比较只走一条路，那是 LC 235 的做法。这题值的大小和树的结构无关，两边都得看。

## 参考代码

```python
from __future__ import annotations

from collections import deque
from typing import List, Optional


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


def build_tree(vals: List[Optional[int]]) -> Optional[TreeNode]:
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    q = deque([root])
    i = 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root


def find(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    if root is None or root.val == val:
        return root
    return find(root.left, val) or find(root.right, val)


def lowestCommonAncestor(
    root: Optional[TreeNode],
    p: TreeNode,
    q: TreeNode,
) -> Optional[TreeNode]:
    if root is None or root is p or root is q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right:
        return root
    return left or right


if __name__ == "__main__":
    root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    n = lambda v: find(root, v)
    assert lowestCommonAncestor(root, n(5), n(1)) is root
    assert lowestCommonAncestor(root, n(5), n(4)) is n(5)
    assert lowestCommonAncestor(root, n(7), n(4)) is n(2)
    assert lowestCommonAncestor(root, n(6), n(4)) is n(5)
    small = build_tree([1, 2])
    assert lowestCommonAncestor(small, small, small.left) is small
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
n = lambda v: find(root, v)
assert lowestCommonAncestor(root, n(5), n(1)) is root
assert lowestCommonAncestor(root, n(5), n(4)) is n(5)
assert lowestCommonAncestor(root, n(7), n(4)) is n(2)
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，最坏扫完整棵。额外空间 $O(h)$。

## Edge Cases

- `p` 是 `q` 的祖先时，碰到 `p` 就返回，不必再往下找 `q`。
- `p`、`q` 是根的左右孩子时，根就是 LCA。
- 链状树里，LCA 是更靠上的那个。

## 追问

**树是 BST（LC 235）呢？**
按值分流就行，不必两边都搜。从根往下，二者都小于当前值就走左，都大于就走右，否则当前就是分叉点（其中一个就是当前节点也算）。平均 $O(h)$，可以写成迭代。BST 按值走单路的套路也见 `lc-700-search-in-a-binary-search-tree`。

```python
def lowestCommonAncestorBST(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
```

**`p` 或 `q` 可能不在树里呢？**
那就不能碰到一个就返回，因为另一侧可能根本没有目标。本题保证都在，换成不保证的版本，后序要改成返回「找到了几个」：左右加上自身的命中数，恰好 $2$ 个且还没记过时，当前才是 LCA；最终命中不足 $2$ 就返回空。

```python
def lca_maybe_absent(root, p, q):
    found = [None]

    def dfs(node):
        if node is None:
            return 0
        n = dfs(node.left) + dfs(node.right) + (node is p or node is q)
        if n == 2 and found[0] is None:
            found[0] = node
        return n

    dfs(root)
    return found[0]
```
