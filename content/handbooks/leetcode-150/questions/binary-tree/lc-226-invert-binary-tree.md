---
id: lc-226-invert-binary-tree
section: binary-tree
order: 3
level: S
title: LC 226 · 翻转二叉树
quick: 我会在每个节点把左右孩子交换，再递归翻转两边子树，前序后序都行。每个节点只换一次，时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 226. 翻转二叉树
    url: 'https://leetcode.cn/problems/invert-binary-tree/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定二叉树根节点 `root`，把整棵树变为左右镜像：每一个节点原本的左孩子位置与右孩子位置都要互换。节点值保持不变，缺失孩子仍可为空。

### 输入与输出

实现 `invertTree(root) -> TreeNode | None`。本卡接口原地修改树的连接，并返回原来的根对象；输入为空树时返回 None。示例输出描述的是修改后的结构。

### 约束

- 节点数在 0 到 100 之间。
- `-100 <= Node.val <= 100`。
- 示例用层序序列表示树，null 表示缺失的孩子。

### 示例

```text
输入：root = [4,2,7,1,3,6,9]
输出：[4,7,2,9,6,3,1]
```

[LeetCode 原题](https://leetcode.com/problems/invert-binary-tree/description/)

## 解题思路与参考答案

## 题意

把整棵二叉树左右镜像翻转，返回的仍是原来那个根对象。

## 思路

我会直接递归，因为翻转整棵树就是在每个节点上把左右孩子对调一次。碰到一个节点，先交换 `left` 和 `right`，再对两个孩子递归；空节点直接返回。

拿示例走一遍：根 $4$，左边 $2$（挂着 $1$、$3$），右边 $7$（挂着 $6$、$9$）。在根上交换后，$7$ 到了左边、$2$ 到了右边；再分别在 $7$ 和 $2$ 上交换，层序就变成 `[4, 7, 2, 9, 6, 3, 1]`。

先换再递归，或者先翻子树再换，结果一样，每个节点都只交换一次。

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


def invertTree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None
    root.left, root.right = root.right, root.left
    invertTree(root.left)
    invertTree(root.right)
    return root


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
    root = TreeNode(
        4,
        TreeNode(2, TreeNode(1), TreeNode(3)),
        TreeNode(7, TreeNode(6), TreeNode(9)),
    )
    assert to_list(invertTree(root)) == [4, 7, 2, 9, 6, 3, 1]
    assert invertTree(None) is None
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(
    4,
    TreeNode(2, TreeNode(1), TreeNode(3)),
    TreeNode(7, TreeNode(6), TreeNode(9)),
)
assert to_list(invertTree(root)) == [4, 7, 2, 9, 6, 3, 1]
assert invertTree(None) is None
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每个节点换一次，时间 $O(n)$，额外空间 $O(h)$。

## Edge Cases

空树返回 `None`。单节点左右都为空，换了等于没换。只有一个孩子时，换完它会挂到另一侧。

## 追问

**必须原地吗？**
上面的写法已经是原地改指针，不用新建节点。如果不许改原树，就递归新建：`return TreeNode(root.val, invert(root.right), invert(root.left))`，额外多出 $O(n)$ 个节点。动手前先问清要不要返回原对象。

**用层序怎么翻？**
队列弹出当前节点，交换 `left`/`right`，再把交换后的非空孩子入队。每个节点仍只处理一次，时间 $O(n)$，额外空间 $O(w)$。结果和 DFS 一样，只是遍历顺序不同。

```python
from collections import deque


def invertTree(root):
    if root is None:
        return None
    q = deque([root])
    while q:
        node = q.popleft()
        node.left, node.right = node.right, node.left
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    return root
```
