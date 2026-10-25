---
id: lc-101-symmetric-tree
section: binary-tree
order: 4
level: S
title: LC 101 · 对称二叉树
quick: "从根的左右子树开始成对比较。值要相同，还要交叉递归，左侧的左孩子对右侧的右孩子，左侧的右孩子对右侧的左孩子。两个都空算对称，只有一个空就失败。时间 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 101. 对称二叉树
    url: https://leetcode.cn/problems/symmetric-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一棵二叉树，判断它是否关于根节点左右镜像对称。对称不仅要求对应节点值相同，也要求左右子节点的位置互为镜像：一侧存在而对应位置缺失时就不对称。

### 输入与输出

实现 `isSymmetric(root: Optional[TreeNode]) -> bool`，对称返回 `True`，否则返回 `False`。示例使用层序列表描述树，`null` 表示缺失节点；实际输入是根节点对象。

### 约束

- 原题节点数为 1 到 1000，节点值在 `[-100,100]`。
- 本手册接口也接受空根节点，并将空树视为对称。

### 示例

```text
输入：root = [1,2,2,3,4,4,3]
输出：true
```

## 解题思路与参考答案

## 题意

判断二叉树是否轴对称：左子树是右子树的镜像。

## 思路

我会写一个 `mirror(a, b)`，比较两个应当互为镜像的节点，整棵树从 `mirror(root.left, root.right)` 开始。两个都空就对称；只有一个空，或者值不同，就不对称；否则交叉比较 `a.left` 与 `b.right`、`a.right` 与 `b.left`，因为镜像会把左右交换。

拿测试里的 `ok` 看。根下面两个 2，左边的 2 挂着 3、4，右边的 2 挂着 4、3。外侧是左边的 3 对右边的 3，内侧是左边的 4 对右边的 4，都对得上，所以对称。

常见的错是把左右子树当「相同树」去比。对称要比的是镜像，追问里有个左右结构相同却不对称的例子。

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


def isSymmetric(root: Optional[TreeNode]) -> bool:
    def mirror(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:
        if a is None or b is None:
            return a is b
        return (
            a.val == b.val
            and mirror(a.left, b.right)
            and mirror(a.right, b.left)
        )

    return root is None or mirror(root.left, root.right)


if __name__ == "__main__":
    ok = TreeNode(
        1,
        TreeNode(2, TreeNode(3), TreeNode(4)),
        TreeNode(2, TreeNode(4), TreeNode(3)),
    )
    assert isSymmetric(ok)
    bad = TreeNode(1, TreeNode(2, None, TreeNode(3)), TreeNode(2, None, TreeNode(3)))
    assert not isSymmetric(bad)
    assert isSymmetric(None)
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
ok = TreeNode(
        1,
        TreeNode(2, TreeNode(3), TreeNode(4)),
        TreeNode(2, TreeNode(4), TreeNode(3)),
    )
assert isSymmetric(ok)
bad = TreeNode(1, TreeNode(2, None, TreeNode(3)), TreeNode(2, None, TreeNode(3)))
assert not isSymmetric(bad)
assert isSymmetric(None)
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个节点最多看一次；额外空间 $O(h)$。

## 边界

空树没有不对称的一对，判真。单节点左右都空，对称。左右值相同但孩子朝向一样，比如两边都只有右孩子，外侧对不上，不对称。

## 追问

**改成迭代怎么写？**
队列里成对放「应当对称」的两个节点。弹出 `(a, b)`，都空就跳过；一个空或者值不同就返回否；否则按镜像顺序入队，外侧对外侧 `(a.left, b.right)`，内侧对内侧 `(a.right, b.left)`。用层序还是随便什么队列都行，配对顺序必须交叉。时间 $O(n)$，额外空间 $O(w)$。

```python
from collections import deque

def isSymmetric(root):
    if root is None:
        return True
    q = deque([(root.left, root.right)])
    while q:
        a, b = q.popleft()
        if a is None or b is None:
            if a is not b:
                return False
            continue
        if a.val != b.val:
            return False
        q.append((a.left, b.right))
        q.append((a.right, b.left))
    return True
```

**直接判断「左右子树相同」可以吗？**
不可以，那是 LC 100 的 `isSameTree(left, right)`，比的是同构拷贝。`[1,2,2,3,null,null,3]` 左右结构相同，但不对称；`[1,2,2,null,3,3,null]` 才是对称的。所以必须交叉比，`a.left` 对 `b.right`。独立卡见 `lc-100-same-tree`。
