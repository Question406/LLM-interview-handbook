---
id: lc-98-validate-binary-search-tree
section: bst
order: 3
level: S
title: LC 98 · 验证二叉搜索树
quick: "递归时带上下界：左子树的值必须 $\\lt$ 当前值，右子树必须 $\\gt$ 当前值，边界沿路径往下收紧；也可以检查中序是否严格递增。时间 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - BST
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 98. 验证二叉搜索树
    url: https://leetcode.cn/problems/validate-binary-search-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定二叉树，判断它是否满足严格的二叉搜索树规则：对每个节点，左子树中所有节点的值都必须小于该节点，右子树中所有节点的值都必须大于该节点，并且左右子树自身也满足同样规则。

### 接口与输出

实现 `isValidBST(root: Optional[TreeNode]) -> bool`。返回整棵树是否合法，不能只判断一个节点与它的直接孩子；重复值不符合严格大小关系。

### 合法输入与约束

官方输入树有 1 到 10000 个节点，值为 32 位有符号整数。节点使用 `val/left/right` 字段；示例以层序数组表示，`null` 为空孩子。

### 示例

```text
输入：root = [2,1,3]
输出：true
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/validate-binary-search-tree/description/)。

## 解题思路与参考答案

## 题意

判断一棵二叉树是不是有效的 BST：每个节点左子树里所有值都严格小于它，右子树里所有值都严格大于它。

## 思路

我会用带上下界的递归，因为只比较节点和左右孩子不够，每个节点还要满足所有祖先留下来的约束。递归时带着 `(lo, hi)`，当前值必须落在这个开区间里；左孩子继承 `(lo, val)`，右孩子继承 `(val, hi)`。

拿 `[5, 4, 6, null, null, 3, 7]` 看：$4 \lt 5$、$6 \gt 5$、$3 \lt 6$、$7 \gt 6$，每一对父子都合法。但 $3$ 在根的右子树里，它的区间是 $(5, 6)$，$3$ 不在里面，所以返回假。

另一种写法是检查中序是否严格递增，维护前驱就行。节点值可能是 `INT_MIN` / `INT_MAX`，边界用空值或 `None` 表示，别写成 `node.val > INT_MIN` 这种硬编码。

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


def isValidBST(root: Optional[TreeNode]) -> bool:
    def dfs(node: Optional[TreeNode], lo: Optional[int], hi: Optional[int]) -> bool:
        if node is None:
            return True
        if lo is not None and node.val <= lo:
            return False
        if hi is not None and node.val >= hi:
            return False
        return dfs(node.left, lo, node.val) and dfs(node.right, node.val, hi)

    return dfs(root, None, None)


if __name__ == "__main__":
    assert isValidBST(TreeNode(2, TreeNode(1), TreeNode(3)))
    bad = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))
    assert not isValidBST(bad)
    sneak = TreeNode(5, TreeNode(4), TreeNode(6, TreeNode(3), TreeNode(7)))
    assert not isValidBST(sneak)
    assert isValidBST(TreeNode(1))
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert isValidBST(TreeNode(2, TreeNode(1), TreeNode(3)))
bad = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))
assert not isValidBST(bad)
sneak = TreeNode(5, TreeNode(4), TreeNode(6, TreeNode(3), TreeNode(7)))
assert not isValidBST(sneak)
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(h)$。

## 边界

单节点是有效的 BST。有重复值时，本题要求严格，相等就无效。右子树里藏着比祖先还小的节点，就是上面那个例子，只比父子会漏掉。

## 追问

**只检查左右孩子的大小行不行？**
不行，会漏掉隔代的约束。反例就是 `[5,4,6,null,null,3,7]`：根的左右孩子都合法，但 $3$ 在右子树里却小于 $5$。所以要把祖先的上下界沿路径收紧，或者检查中序严格递增。

```python
def isValidBST_inorder(root):
    prev = None

    def dfs(node):
        nonlocal prev
        if node is None:
            return True
        if not dfs(node.left):
            return False
        if prev is not None and node.val <= prev:
            return False
        prev = node.val
        return dfs(node.right)

    return dfs(root)
```

**允许等于（非严格 BST）怎么改？**
把开区间改成闭区间：左界改成 `node.val < lo` 才失败，右界改成 `node.val > hi` 才失败；中序版改成非严格递增，`node.val < prev` 才失败。本题题面是严格的，动手前先确认。值可能是 $32$ 位的最值，边界照样用 `None`。
