---
id: lc-114-flatten-binary-tree-to-linked-list
section: binary-tree
order: 8
level: A
title: LC 114 · 二叉树展开为链表
quick: "按前序把树原地摊成一条右链，所有 `left` 置空。后序递归：先摊平左右子树，把左链接到根的右边，再把原来的右链接到左链尾部。时间 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 114. 二叉树展开为链表
    url: https://leetcode.cn/problems/flatten-binary-tree-to-linked-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定二叉树根节点 root，把它原地展开成一条单链。展开后的节点顺序必须等于原树的前序遍历顺序，即每个节点先于自己的左子树和右子树出现。链上仍使用原来的 TreeNode 节点。

### 接口与输出

实现 `flatten(root: Optional[TreeNode]) -> None`。只使用 `right` 指针连接后继，所有节点的 `left` 必须为 `None`，最后一个节点的 `right` 也为 `None`；不返回新链表，调用后从原 root 沿 right 读取结果。

### 合法输入与约束

节点数为 0 到 2000，`-100 <= Node.val <= 100`。空树合法。示例输出的层序表示反映原树被修改后的结构，不是函数返回值。

### 示例

```text
输入：root = [1,2,5,3,4,null,6]
输出：[1,null,2,null,3,null,4,null,5,null,6]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/description/)。

## 解题思路与参考答案

## 题意

把二叉树原地展开成单链表，顺序和前序遍历一样，只用 `right` 指针连接，所有 `left` 都是 `None`。

## 思路

我会先写后序递归，因为左右子树摊平之后都变成了现成的右链，当前节点只要把两段拼起来。具体是先递归展开左右子树，保存原来的右链，把展开好的左链接到 `root.right`，清空 `left`，再走到左链尾部，接上原来的右链。这样顺序就是根、左子树、右子树，和前序遍历一致。

拿示例走一遍：根 $1$ 的左子树是 $2$（挂着 $3$、$4$），右子树是 $5$（右孩子 $6$）。递归回来时左边已经是 `2→3→4`，右边是 `5→6`。把 `2→3→4` 挂到 $1$ 的右边，走到尾部 $4$，再接上 `5→6`，得到 `1→2→3→4→5→6`。

另外两种写法也可以提一句：先序遍历用栈，或者 Morris，把右子树接到左子树的最右节点，再把整段左子树旋到右边。

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


def flatten(root: Optional[TreeNode]) -> None:
    if root is None:
        return
    flatten(root.left)
    flatten(root.right)
    right = root.right
    root.right = root.left
    root.left = None
    cur = root
    while cur.right:
        cur = cur.right
    cur.right = right


def right_chain(root: Optional[TreeNode]) -> List[int]:
    vals: List[int] = []
    while root:
        assert root.left is None
        vals.append(root.val)
        root = root.right
    return vals


if __name__ == "__main__":
    root = TreeNode(
        1,
        TreeNode(2, TreeNode(3), TreeNode(4)),
        TreeNode(5, None, TreeNode(6)),
    )
    flatten(root)
    assert right_chain(root) == [1, 2, 3, 4, 5, 6]
    empty = None
    flatten(empty)
    assert empty is None
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(
        1,
        TreeNode(2, TreeNode(3), TreeNode(4)),
        TreeNode(5, None, TreeNode(6)),
    )
flatten(root)
assert right_chain(root) == [1, 2, 3, 4, 5, 6]
empty = None
flatten(empty)
assert empty is None
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。递归版找左链尾会重复走一些节点，但每条边只走常数次，最坏仍是 $O(n)$。额外空间是递归栈 $O(h)$；Morris 可以做到 $O(1)$。

## 边界

空树直接返回。只有右链的树本来就是答案，左指针全空。只有左链的树，整段旋到 `right` 上，`left` 清空。

## 追问

**不允许用 $O(h)$ 的栈或递归呢？**
用 Morris。如果当前节点有左子树，先找到左子树的最右节点（前驱），把它的 `right` 接到当前节点原来的右子树，再把左子树整体接到 `cur.right`，`left` 置空，然后 `cur` 沿右链走下一步。每个节点的右指针最多被改常数次，时间 $O(n)$，额外空间 $O(1)$。

```python
def flatten(root):
    cur = root
    while cur:
        if cur.left:
            pred = cur.left
            while pred.right:
                pred = pred.right
            pred.right = cur.right
            cur.right = cur.left
            cur.left = None
        cur = cur.right
```

**可以新开一个链表吗？**
可以当备选写法。先前序遍历把节点放进数组（或者边走边串新节点），再按顺序把 `right` 指向下一个、`left` 置空。时间 $O(n)$，额外空间 $O(n)$。题面要求原地时，还是用后序拼接或 Morris。
