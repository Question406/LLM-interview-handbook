---
id: lc-101-symmetric-tree
section: binary-tree
order: 4
level: S
title: LC 101 · 对称二叉树
quick: >-
  比左右镜像：外侧对外侧、内侧对内侧，值相等且结构对称。不是 `isSameTree(left,
  right)`。时间 $O(n)$，额外空间 $O(h)$。
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

## 题意

判断二叉树是否轴对称：左子树是右子树的镜像。

## 思路

单独写 `mirror(a, b)`：都空为真；一个空或值不同为假；否则 `a.left` 对 `b.right`、`a.right` 对 `b.left`。根调用 `mirror(root.left, root.right)`。

错法：拿左右子树当「相同树」比。对称比的是镜像，不是同构拷贝。

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

## 复杂度

时间 $O(n)$，每个节点最多看一次。额外空间 $O(h)$。

## 边界

- 空树：没有不对称的一对，判真。
- 单节点：左右都空，对称。
- 左右值相同，但孩子朝向一样（都只有右孩子）：外侧对不上，不对称。

## 追问

- **改成迭代？** 队列里成对放「应对称」的两个节点。弹出 `(a, b)`：都空跳过；一个空或值不同则否；否则按镜像顺序入队，外侧对外侧 `(a.left, b.right)`，内侧对内侧 `(a.right, b.left)`。层序或随便的队列都行，配对顺序必须交叉。时间 $O(n)$，额外空间 $O(w)$。

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

- **直接判断「左右子树相同」？** 那是 LC 100 的 `isSameTree(left, right)`：比的是同构拷贝，不是镜像。`[1,2,2,3,null,null,3]` 左右结构相同但不对称；`[1,2,2,null,3,3,null]` 才对称。必须交叉：`a.left` 对 `b.right`。独立卡见 `lc-100-same-tree`。
