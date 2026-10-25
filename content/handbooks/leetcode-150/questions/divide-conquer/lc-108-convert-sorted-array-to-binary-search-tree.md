---
id: lc-108-convert-sorted-array-to-binary-search-tree
section: divide-conquer
order: 1
level: A
title: LC 108 · 将有序数组转换为二叉搜索树
quick: "取有序数组的中点做根，左半段递归建左子树、右半段递归建右子树；中点让两边规模差不超过 $1$，高度自动平衡。时间 $O(n)$，递归栈 $O(\\log n)$。"
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

## 题目描述

给定严格递增的整数数组，把其中每个元素恰好使用一次，构造一棵高度平衡的二叉搜索树。搜索树中每个节点的左子树所有值较小、右子树所有值较大；高度平衡表示每个节点两侧子树的高度差不超过 1。

### 输入与输出

实现 `sortedArrayToBST(nums) -> TreeNode`。返回满足条件的任意一棵树的根节点；示例输出用层序数组表示结构，null 表示空孩子，并不是唯一正确的形状。

### 约束与约定

- `1 <= len(nums) <= 10000`。
- 数值在 `[-10000,10000]`，数组严格递增。

### 示例

```text
输入：nums = [-10,-3,0,5,9]
输出：[0,-3,9,-10,null,5]
```

示例是一个合法结果；只要搜索树次序正确且每个节点满足平衡条件，其他结构也可接受。

[官方原题与完整题面](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/description/)。

## 解题思路与参考答案

## 题意

把升序数组 `nums` 转成一棵高度平衡的二叉搜索树，也就是任意结点左右子树的高度差不超过 $1$。

## 思路

我会用分治，每次取闭区间的中点做根，因为有序数组本身就是 BST 的中序，中点左边的数都比它小、右边都比它大，正好分给左右子树。中点把两边的规模差控制在 $1$ 以内，整棵树自然平衡。

拿示例 `[-10, -3, 0, 5, 9]` 走一遍：中点 $0$ 做根；左半 `[-10, -3]` 的中点偏左取 $-10$，$-3$ 挂在它右边；右半 `[5, 9]` 同样取 $5$，$9$ 挂在它右边。左右子树高度都是 $2$。

偶数长度时中点可以偏左也可以偏右，只要全程一致。每次都选左端或右端当根，树会退化成链。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每个元素恰好建一个结点，时间 $O(n)$。递归深度 $O(\log n)$。

## 边界

$n=1$ 时 `lo == hi`，中点就是唯一的结点，左右递归立刻返回空。长度为偶数时 `(lo+hi)//2` 偏左，左右子树规模差 $1$，高度差仍然 $\le 1$；全程改成偏右（`(lo+hi+1)//2`）同样平衡，只是别混用。

## 追问

**换成链表（LC 109）呢？**
链表没法 $O(1)$ 取中点。直接的做法是切中点递归：快慢指针找中点、断开左半，中点做根，左右再递归，每层找中点 $O(n)$、一共 $\log n$ 层，时间 $O(n\log n)$。想要 $O(n)$，就先数出长度 $n$，再按中序建树：递归先建左子树，这时链表头正好是中序的下一个结点，读出值后指针右移，再建右子树。长度保证了平衡，栈 $O(\log n)$。独立卡见 `lc-109`。

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

**不要求平衡呢？**
那任意元素当根、其余按大小分到左右，仍然是 BST，但每次取端点会退化成链，高度 $O(n)$。本题明确要求高度差 $\le 1$，所以必须取区间中点。转成链表后再平衡是 AVL / 红黑树那一套，讲到这里就可以停了。
