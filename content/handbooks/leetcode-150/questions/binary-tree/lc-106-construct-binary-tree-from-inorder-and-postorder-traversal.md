---
id: lc-106-construct-binary-tree-from-inorder-and-postorder-traversal
section: binary-tree
order: 6
level: A
title: LC 106 · 从中序与后序遍历序列构造二叉树
quick: >-
  后序最后一个 `post[-1]` 是根，拿它在中序里切开左右子树；后序末尾那一段的长度等于右子树大小，递归下去。中序下标用哈希定位。时间
  $O(n)$，额外空间 $O(n)$。
tags:
  - Tree
  - Hash Table
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 106. 从中序与后序遍历序列构造二叉树
    url: >-
      https://leetcode.cn/problems/construct-binary-tree-from-inorder-and-postorder-traversal/
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定同一棵二叉树的中序遍历数组 `inorder` 和后序遍历数组 `postorder`，构造并返回这棵树。中序指左子树、根、右子树；后序指左子树、右子树、根。每个节点值在树中只出现一次，输入保证来自一棵合法的树。

### 输入与输出

实现 `buildTree(inorder, postorder) -> TreeNode`。返回新构造的根节点，必须还原正确的左右孩子连接关系，而不是只返回节点值列表。

### 约束

- `1 <= len(inorder) <= 3000`，两数组长度相同。
- 两个数组包含相同的一组互不相同的整数。
- 各节点值在 -3000 到 3000 之间。
- 示例的输出用层序序列展示返回的树，null 表示缺失的孩子。

### 示例

```text
输入：inorder = [9,3,15,20,7], postorder = [9,15,7,20,3]
输出：[3,9,20,null,null,15,7]
```

[LeetCode 原题](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/description/)

## 解题思路与参考答案

## 题意

给出一棵树的中序遍历和后序遍历，节点值互不相同，要求还原这棵二叉树。

## 思路

我会用递归加哈希，做法和 LC 105 对称：前序的根在头，后序的根在尾。后序最后一个是根；中序里根左边是左子树，右边是右子树。右子树如果有 $k$ 个节点，后序里倒数第 $2$ 到倒数第 $k+1$ 个就是右子树，更前面是左子树。

用示例走一遍：中序 `[9, 3, 15, 20, 7]`，后序 `[9, 15, 7, 20, 3]`。根是 $3$，中序里它右边有 $15$、$20$、$7$ 三个，所以右子树大小是 $3$；后序里根前面的 `[15, 7, 20]` 是右子树，剩下的 `[9]` 是左子树。右子树再递归，后序最后一个 $20$ 就是它的根。

## 参考代码

```python
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional


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


def buildTree(inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
    idx: Dict[int, int] = {v: i for i, v in enumerate(inorder)}

    def build(in_l: int, in_r: int, post_l: int, post_r: int) -> Optional[TreeNode]:
        if post_l > post_r:
            return None
        root_val = postorder[post_r]
        root = TreeNode(root_val)
        mid = idx[root_val]
        right_size = in_r - mid
        root.left = build(in_l, mid - 1, post_l, post_r - right_size - 1)
        root.right = build(mid + 1, in_r, post_r - right_size, post_r - 1)
        return root

    n = len(inorder)
    return build(0, n - 1, 0, n - 1)


def to_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    if root is None:
        return []
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


if __name__ == "__main__":
    root = buildTree([9, 3, 15, 20, 7], [9, 15, 7, 20, 3])
    assert to_list(root) == [3, 9, 20, None, None, 15, 7]
    assert to_list(buildTree([-1], [-1])) == [-1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = buildTree([9, 3, 15, 20, 7], [9, 15, 7, 20, 3])
assert to_list(root) == [3, 9, 20, None, None, 15, 7]
assert to_list(buildTree([-1], [-1])) == [-1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，哈希 $O(n)$，递归栈 $O(h)$。

## Edge Cases

单节点时中序、后序都是同一个值。只有左子树时，后序的根仍在最后，中序的根在最右，右段长度为 $0$。只有右子树时，中序的根在最左，后序里除根之外整段都是右子树。

## 追问

**只给前序和后序、没有中序，能还原吗？**
一般不能唯一确定。前序是 `根|左|右`，后序是 `左|右|根`，左右的交界在哪里不知道。比如前序 `[1,2]` 配后序 `[2,1]`，$2$ 既可以在左也可以在右。满二叉树，或者另给一种遍历，才能唯一还原。

**和前序加中序（LC 105）怎么对照着讲？**
中序都负责切开左右，长度算法相同，差别只在根的位置。前序取 `pre[pre_l]`，左子树占前序接下来的 $k$ 个；后序取 `post[post_r]`，右子树占后序末尾的 $k$ 个。独立卡见 `lc-105-construct-binary-tree-from-preorder-and-inorder-traversal`。

```python
def buildTree(preorder, inorder):
    idx = {v: i for i, v in enumerate(inorder)}

    def build(pre_l, pre_r, in_l, in_r):
        if pre_l > pre_r:
            return None
        root = TreeNode(preorder[pre_l])
        mid = idx[root.val]
        k = mid - in_l
        root.left = build(pre_l + 1, pre_l + k, in_l, mid - 1)
        root.right = build(pre_l + k + 1, pre_r, mid + 1, in_r)
        return root

    n = len(preorder)
    return build(0, n - 1, 0, n - 1)
```
