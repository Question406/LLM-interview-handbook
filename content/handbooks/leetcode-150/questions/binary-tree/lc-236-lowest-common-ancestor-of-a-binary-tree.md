---
id: lc-236-lowest-common-ancestor-of-a-binary-tree
section: binary-tree
order: 14
level: S
title: LC 236 · 二叉树的最近公共祖先
quick: "这是普通二叉树，要两边都搜：递归碰到 `p`、`q` 或空就返回；左右都有结果，说明两个目标分居两侧，当前节点就是 LCA；只有一侧有结果，答案就在那一侧。时间 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 236. 二叉树的最近公共祖先
    url: https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一棵普通二叉树，以及树中两个不同的节点 p 和 q，返回它们的最近公共祖先。公共祖先指同时把 p 和 q 包含在自身子树中的节点；“最近”表示其中深度最大的一个。节点自身也属于自己的子树，因此一个目标节点可以是另一个目标的祖先。

### 输入与输出

实现 `lowestCommonAncestor(root, p: TreeNode, q: TreeNode) -> Optional[TreeNode]`。p、q 是原树中的节点对象，返回值也必须是原树中的那个祖先节点，而不是新建的同值节点。示例用层序列表表示 root，用唯一的节点值标识 p、q 和输出。

### 约束

- 节点数为 2 到 `10^5`，所有节点值互不相同，值范围为 `[-10^9,10^9]`。
- p 与 q 不相同，且都保证存在于树中；不假设这棵树满足二叉搜索树顺序。

### 示例

```text
输入：root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
输出：3
```

值为 5 和 1 的节点分别在根的左右子树中，最近公共祖先是原树中值为 3 的根节点。

## 解题思路与参考答案

## 题意

在一棵普通二叉树里找节点 `p` 和 `q` 的最近公共祖先。题目保证两个节点都在树上，一个节点也可以是它自己的祖先，节点值互不相同。

## 思路

我会用后序递归，让函数返回「这棵子树里找到的目标节点，或者已经确定的祖先」。当前节点是 `None`、`p` 或 `q` 时直接返回它；否则分别递归左右子树。两侧都有结果，说明目标分居左右，当前节点就是最近公共祖先（LCA）；只有一侧有结果，就把那个结果继续往上传。

拿示例那棵树走一遍：根 $3$，左 $5$、右 $1$，$5$ 下面是 $6$ 和 $2$，$2$ 下面是 $7$ 和 $4$。找 $7$ 和 $4$ 时，在 $2$ 这里左边返回 $7$、右边返回 $4$，两侧都有，$2$ 就是答案；再往上，$5$ 和 $3$ 都只收到一侧的结果，原样把 $2$ 传上去。

常见的误区是把它当成 BST，按值比较只走一条路，那是 LC 235 的做法。这题值的大小和树的结构没有关系，必须两边都看。

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
    n7, n4 = TreeNode(7), TreeNode(4)
    n2 = TreeNode(2, n7, n4)
    n6, n0, n8 = TreeNode(6), TreeNode(0), TreeNode(8)
    n5, n1 = TreeNode(5, n6, n2), TreeNode(1, n0, n8)
    root = TreeNode(3, n5, n1)
    assert lowestCommonAncestor(root, n5, n1) is root
    assert lowestCommonAncestor(root, n5, n4) is n5
    assert lowestCommonAncestor(root, n7, n4) is n2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
n7, n4 = TreeNode(7), TreeNode(4)
n2 = TreeNode(2, n7, n4)
n6, n0, n8 = TreeNode(6), TreeNode(0), TreeNode(8)
n5, n1 = TreeNode(5, n6, n2), TreeNode(1, n0, n8)
root = TreeNode(3, n5, n1)
assert lowestCommonAncestor(root, n5, n1) is root
assert lowestCommonAncestor(root, n5, n4) is n5
assert lowestCommonAncestor(root, n7, n4) is n2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

最坏要扫完整棵树，时间 $O(n)$，额外空间 $O(h)$。

## 边界

`p` 是 `q` 的祖先时，碰到 `p` 就返回，不用再往下找 `q`。`p`、`q` 是根的左右孩子时，根就是 LCA。链状树上，LCA 是更靠上的那一个。

## 追问

**如果树是 BST（LC 235）呢？**
按值分流就行，不用两边都搜。从根往下，二者都小于当前值就走左，都大于就走右，否则当前节点就是分叉点，其中一个就是当前节点也算。平均 $O(h)$，可以写成迭代。

```python
def lowestCommonAncestor(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
```

**`p` 或 `q` 可能不在树里怎么办？**
那就不能碰到一个就返回，另一侧可能根本没有目标。后序改成返回「找到了几个」：左右的命中数加上自身是否命中，恰好是 $2$ 而且还没记录过时，当前节点才是 LCA；最后命中不足 $2$ 就返回空。本题保证都在，所以不用这么写。

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
