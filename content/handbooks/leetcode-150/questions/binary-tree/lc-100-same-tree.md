---
id: lc-100-same-tree
section: binary-tree
order: 2
level: A
title: LC 100 · 相同的树
quick: "两棵树同步 DFS。都空算相同；一个空、或者值不同就不同；否则继续比左右子树。时间 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 100. 相同的树
    url: https://leetcode.cn/problems/same-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定两棵二叉树的根节点 `p` 和 `q`，判断它们是否相同。相同必须同时满足：每个位置有没有节点完全一致，并且每一对对应节点的值相等。只有节点值集合相同或遍历序列的一部分相同，并不算相同的树。

### 输入与输出

实现 `isSameTree(p, q) -> bool`。输入分别是 TreeNode 根对象或 None；两棵树都为空时返回 True。此函数只比较，不需要修改输入树。

### 约束

- 每棵树的节点数均在 0 到 100 之间。
- `-10^4 <= Node.val <= 10^4`。
- 示例用层序序列描述树，null 代表缺失的孩子。

### 示例

```text
输入：p = [1,2,3], q = [1,2,3]
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/same-tree/description/)

## 解题思路与参考答案

## 题意

判断两棵二叉树是否结构相同且对应节点值相等。

## 思路

我会同步递归两棵树，结构和值一起比。`p`、`q` 都是 `None` 就相同；恰好一个是 `None`，或者 `val` 不同，就不同；否则继续比左边和右边。代码里的 `p is q` 一句同时处理了都空和只有一个空两种情况。

拿测试里的 `c` 和 `d` 看。根都是 1，`c` 的 2 挂在左边，`d` 的 2 挂在右边。比左孩子时一个是 2、一个是 `None`，直接返回假。

用层序遍历、两边同时出队也可以做。

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


def isSameTree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if p is None or q is None:
        return p is q
    return (
        p.val == q.val
        and isSameTree(p.left, q.left)
        and isSameTree(p.right, q.right)
    )


if __name__ == "__main__":
    a = TreeNode(1, TreeNode(2), TreeNode(3))
    b = TreeNode(1, TreeNode(2), TreeNode(3))
    assert isSameTree(a, b)
    c = TreeNode(1, TreeNode(2), None)
    d = TreeNode(1, None, TreeNode(2))
    assert not isSameTree(c, d)
    assert isSameTree(None, None)
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
a = TreeNode(1, TreeNode(2), TreeNode(3))
b = TreeNode(1, TreeNode(2), TreeNode(3))
assert isSameTree(a, b)
c = TreeNode(1, TreeNode(2), None)
d = TreeNode(1, None, TreeNode(2))
assert not isSameTree(c, d)
assert isSameTree(None, None)
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\min(n_p,n_q))$，一旦出现分叉就可以停；额外空间 $O(h)$。

## 边界

两棵都空，没有节点，判为相同。恰好一棵空，结构已经不同。结构相同但某个节点值不同，也要判否。镜像树（一边挂左、一边挂右）看起来值一样，结构不同，应判否。

## 追问

**只比值、不管结构行吗？**
不行。只收集非空值时，`[1,2]` 和 `[1,null,2]` 都会得到 $1,2$，但一棵是左孩子、一棵是右孩子。所以要同步走两个指针：都空才算同，一个空一个非空直接否，值不等也否，再同时比左右。真要用序列化，就得带上空位标记，例如 `val,#`，这样结构和值还是一起编进去了。

**怎么判断一棵是另一棵的子树（LC 572）？**
在 `root` 上把每个节点当起点，调用本题的「相同树」。外层 DFS 枚举起点，内层 `same` 同步比结构和值，最坏 $O(nm)$。空的 `subRoot` 视为真；`root` 空而子树非空为假。

```python
def isSubtree(root, subRoot):
    def same(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    if root is None:
        return subRoot is None
    return (
        same(root, subRoot)
        or isSubtree(root.left, subRoot)
        or isSubtree(root.right, subRoot)
    )
```
