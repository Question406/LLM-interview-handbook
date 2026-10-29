---
id: lc-450-delete-node-in-a-bst
section: bst
order: 2
level: S
title: LC 450 · 删除二叉搜索树中的节点
quick: >-
  先按值走到目标节点。缺一个孩子就让另一个孩子顶上来；两个孩子都在，就拿右子树最小值（后继）覆盖当前值，再去右子树删掉那个后继。递归返回新子树根，时间
  $O(h)$，额外空间 $O(h)$。
tags:
  - Tree
  - BST
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 450. Delete Node in a BST
    url: 'https://leetcode.com/problems/delete-node-in-a-bst/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定有效二叉搜索树的根节点 root 和整数 key，从树中删除值为 key 的节点，并让剩余节点仍构成有效 BST。如果 key 不存在，树中的元素保持不变。

### 接口与输出

实现 `deleteNode(root: Optional[TreeNode], key: int) -> Optional[TreeNode]`，返回删除后可能改变的根节点。结果必须恰好保留原树中除 key 外的全部值；允许不同但同样有效的 BST 形状。目标时间复杂度为 `O(h)`，h 为树高。

### 合法输入与约束

节点数为 0 到 10000，`-100000 <= Node.val,key <= 100000`，节点值互不相同。空树和删除根节点都是合法情况。示例层序输出只展示一种合法结果。

### 示例

```text
输入：root = [5,3,6,2,4,null,7], key = 3
输出：[5,4,6,2,null,null,7]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/delete-node-in-a-bst/description/)。

## 解题思路与参考答案

## 题意

给 BST 的根和 `key`，删除值为 `key` 的节点（可能不存在），保持 BST 性质，返回可能变化的根。节点数 $[0, 10^4]$，值互异。进阶要求 $O(h)$。

## 思路

我会写递归，函数的意思定成「在这棵子树里删掉 `key`，返回删完后的子树根」。父节点用 `root.left = deleteNode(root.left, key)` 接住返回值，就不用单独维护父指针。

定位和搜索一样，`key` 比当前小往左走，大往右走。命中之后分三种情况。叶子直接返回 `None`。只有一个孩子，就把那个孩子返回上去顶替自己。左右都在的时候，找右子树最左的节点，也就是后继，比当前值大的数里最小的那个；把它的值写到当前节点，再到右子树里递归删掉这个后继。后继没有左孩子，所以第二次删除一定落在前两种简单情况里。

拿 `[5,3,6,2,4,null,7]` 删 `3` 走一遍：`3` 比 `5` 小，往左走就命中了。它左右都有孩子，右子树最左的是 `4`，于是把 `3` 改成 `4`，再去右子树删掉原来的 `4`，那是个叶子，直接摘掉。结果是 `[5,4,6,2,null,null,7]`。

为什么这样还是 BST？后继顶上来以后，左子树原本就都小于被删的值，自然也小于后继；右子树剩下的都比后继大。用左子树最大值（前驱）来顶也对，删出来的树形不同，但都合法。

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


def to_level_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    out: List[Optional[int]] = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def inorder(root: Optional[TreeNode]) -> List[int]:
    return inorder(root.left) + [root.val] + inorder(root.right) if root else []


def deleteNode(root: Optional[TreeNode], key: int) -> Optional[TreeNode]:
    if root is None:
        return None
    if key < root.val:
        root.left = deleteNode(root.left, key)
    elif key > root.val:
        root.right = deleteNode(root.right, key)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        succ = root.right
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = deleteNode(root.right, succ.val)
    return root


if __name__ == "__main__":
    assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 3)) == [
        5,
        4,
        6,
        2,
        None,
        None,
        7,
    ]
    assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 0)) == [
        5,
        3,
        6,
        2,
        4,
        None,
        7,
    ]
    assert to_level_list(deleteNode(build_tree([]), 0)) == []
    assert to_level_list(deleteNode(build_tree([5]), 5)) == []
    assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 5)) == [
        6,
        3,
        7,
        2,
        4,
    ]
    t = deleteNode(
        build_tree([50, 30, 70, 20, 40, 60, 80, None, None, 35, 45, 55, 65]), 30
    )
    assert inorder(t) == [20, 35, 40, 45, 50, 55, 60, 65, 70, 80]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 3)) == [
    5,
    4,
    6,
    2,
    None,
    None,
    7,
]
assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 0)) == [
    5,
    3,
    6,
    2,
    4,
    None,
    7,
]
assert to_level_list(deleteNode(build_tree([]), 0)) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(h)$：定位走一条路径，找后继再删除又是一条往下的路径。额外空间 $O(h)$，是递归栈。

## Edge Cases

`key` 不存在时，一路走到 `None` 返回，树原样不动。

删的是根时，递归的返回值就是新根，调用方一定要用这个返回值，别假设根没变。

删叶子时，`left` 为空的那个分支返回 `right`，也就是 `None`，叶子就自然被摘掉了。

## 追问

**不允许改节点值，只能改指针怎么办？**
把后继节点从原位置摘下来，让它接管被删节点的左右子树。摘后继的时候，它的右子树要接回后继的父节点；后继恰好就是 `root.right` 时，只需把 `root.left` 挂到它左边。

```python
def deleteNodeRelink(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = deleteNodeRelink(root.left, key)
        return root
    if key > root.val:
        root.right = deleteNodeRelink(root.right, key)
        return root
    if root.left is None:
        return root.right
    if root.right is None:
        return root.left
    parent, succ = root, root.right
    while succ.left:
        parent, succ = succ, succ.left
    if parent is not root:
        parent.left = succ.right
        succ.right = root.right
    succ.left = root.left
    return succ
```

**还有更短的写法吗？**
有。两个孩子都在时，把左子树整个挂到右子树最左节点的左边，然后返回右子树。这样写是对的，但树会变高，删几次之后退化得很快。面试里我会提一句，主写后继替换。

相关：搜索定位的走法见 `lc-700-search-in-a-binary-search-tree`。
