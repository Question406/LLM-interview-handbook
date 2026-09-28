---
id: lc-173-binary-search-tree-iterator
section: binary-tree
order: 12
level: A
title: LC 173 · 二叉搜索树迭代器
quick: >-
  实现 `BSTIterator`：用栈做受控中序，初始化把左链压栈。`next` 弹栈并压入右孩子的左链；`next` /
  `hasNext` 均摊 $O(1)$，空间 $O(h)$。
tags:
  - Tree
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 173. 二叉搜索树迭代器
    url: https://leetcode.cn/problems/binary-search-tree-iterator/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

对 BST 实现迭代器：`next()` 返回中序下一个最小元素，`hasNext()` 判断是否还有。初始化时不要一次性遍历整棵树。

## 思路

栈里始终放「还未吐出的祖先左链」。构造时从根一路向左压栈。`next` 弹出栈顶即当前最小值，若它有右孩子，把右孩子及其左链压入。`hasNext` 看栈是否非空。

一次性中序进数组也正确，但空间 $O(n)$，不是受控迭代。均摊：每个节点入栈出栈各一次。

## 参考代码

```python
from __future__ import annotations

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


class BSTIterator:
    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        self._push_left(root)

    def _push_left(self, node: Optional[TreeNode]) -> None:
        while node:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

    def hasNext(self) -> bool:
        return bool(self.stack)


if __name__ == "__main__":
    root = TreeNode(7, TreeNode(3), TreeNode(15, TreeNode(9), TreeNode(20)))
    it = BSTIterator(root)
    assert it.hasNext()
    assert [it.next() for _ in range(5)] == [3, 7, 9, 15, 20]
    assert not it.hasNext()
    empty = BSTIterator(None)
    assert not empty.hasNext()
    print("ok")
```

## 复杂度

`next` / `hasNext` 均摊 $O(1)$，单次 `next` 最坏 $O(h)$。空间 $O(h)$。

## 边界

- 空树：`hasNext` 为假，不要调 `next`。
- 只有左链：构造时栈先到 $h$，随后每次 `next` 几乎 $O(1)$。
- 只有右链：栈里几乎总是 $1$ 个节点。

## 追问

- **`hasNext` 之后不调用 `next`？** 栈状态不变，可以反复问，必须一直返回同一布尔值。`hasNext` 只读 `len(stack)`，不要在里面 `pop`。实现时把「找下一个」全部放进 `next`。

- **反向迭代（从大到小 / 第 $k$ 大）？** 中序反向：构造时沿右链压栈；`next` 弹出当前最大，再把它的左孩子及其右链压入。均摊仍 $O(1)$，空间 $O(h)$。第 $k$ 大就是反向迭代 $k$ 次。

```python
class BSTIteratorReverse:
    def __init__(self, root):
        self.stack = []
        self._push_right(root)

    def _push_right(self, node):
        while node:
            self.stack.append(node)
            node = node.right

    def next(self):
        node = self.stack.pop()
        self._push_right(node.left)
        return node.val

    def hasNext(self):
        return bool(self.stack)
```
