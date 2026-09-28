---
id: lc-108-convert-sorted-array-to-binary-search-tree
section: divide-conquer
order: 1
level: A
title: LC 108 · 将有序数组转换为二叉搜索树
quick: >-
  有序数组中点做根，左右半段递归建子树，高度自动平衡。时间 $O(n)$，递归栈
  $O(\log n)$。
tags:
  - Tree
  - Divide and Conquer
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 108. 将有序数组转换为二叉搜索树
    url: https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

升序数组 `nums` 转成一棵高度平衡的二叉搜索树：任意结点左右子树高度差不超过 $1$。

## 思路

有序数组的中序就是 BST 的中序。每次取闭区间中点做根，左半建左子树、右半建右子树。中点把两边规模差控制在 $1$ 以内，整棵树自然平衡。

偶数长度时中点可偏左或偏右，只要全程一致。不要每次都选左端或右端当根，那样会退化成链。

## 参考代码

```python
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def sortedArrayToBST(nums: List[int]) -> Optional[TreeNode]:
    def build(lo: int, hi: int) -> Optional[TreeNode]:
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi))

    return build(0, len(nums) - 1)


if __name__ == "__main__":
    def inorder(root):
        return inorder(root.left) + [root.val] + inorder(root.right) if root else []

    def height(root):
        return 0 if not root else 1 + max(height(root.left), height(root.right))

    def balanced(root):
        if not root:
            return True
        return abs(height(root.left) - height(root.right)) <= 1 and balanced(root.left) and balanced(root.right)

    root = sortedArrayToBST([-10, -3, 0, 5, 9])
    assert inorder(root) == [-10, -3, 0, 5, 9] and balanced(root)
    root = sortedArrayToBST([1, 3])
    assert inorder(root) == [1, 3] and balanced(root)
    print("ok")
```

## 复杂度

时间 $O(n)$，每个元素恰好建一次结点。递归深度 $O(\log n)$。

## 边界

- $n=1$：`lo == hi`，中点就是唯一结点，左右递归立刻空。
- 长度为偶数：`(lo+hi)//2` 偏左，左右子树规模差 $1$，高度差仍 $\le 1$。全程改成偏右（`(lo+hi+1)//2`）同样平衡，不要混用。

## 追问

- **链表版（LC 109）？** 链表不能 $O(1)$ 取中点。切中点递归：快慢指针找中点、断开左半，根是中点，左右再递归，时间 $O(n\log n)$（每层找中点 $O(n)$、$\log n$ 层）。要 $O(n)$：先数长度 $n$，再按中序建树。递归先建左子树，当前链表头就是中序下一个结点，读值后指针右移，再建成右子树。长度保证平衡，栈 $O(\log n)$。独立卡见 `lc-109`。

```python
def sortedListToBST(head):
    def length(p):
        n = 0
        while p:
            n += 1
            p = p.next
        return n

    def build(lo, hi):
        nonlocal head
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        left = build(lo, mid - 1)
        node = TreeNode(head.val)
        head = head.next
        node.left = left
        node.right = build(mid + 1, hi)
        return node

    return build(0, length(head) - 1)
```

- **不必平衡？** 任意元素当根、其余按大小分到左右，仍是 BST，但每次取端点会退化成链，高度 $O(n)$。本题明确要求高度差 $\le 1$，必须取区间中点。转成链表后再平衡是 AVL/红黑那套，到这就停。
