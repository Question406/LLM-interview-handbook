---
id: lc-199-binary-tree-right-side-view
section: binary-tree-bfs
order: 1
level: S
title: LC 199 · 二叉树的右视图
quick: 层序 BFS，每层取最后一个节点就是右视图；如果先右后左入队，就取每层第一个。时间 $O(n)$，额外空间 $O(w)$。
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 199. 二叉树的右视图
    url: 'https://leetcode.cn/problems/binary-tree-right-side-view/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定二叉树根节点 root。假想站在树的右侧观察，每一层只能看到这一层最靠右的节点。按照从根所在层到最深层的顺序，返回这些可见节点的值。

### 接口与输出

实现 `rightSideView(root: Optional[TreeNode]) -> List[int]`。节点包含 `val`、`left`、`right`；返回的是每层可见节点的值，不是节点对象。空树返回 `[]`。

### 合法输入与约束

节点数为 0 到 100，`-100 <= Node.val <= 100`。示例用层序数组描述树，`null` 表示相应孩子不存在；实际函数输入是已经构造好的根节点。

### 示例

```text
输入：root = [1,2,3,null,5,null,4]
输出：[1,3,4]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/binary-tree-right-side-view/description/)。

## 解题思路与参考答案

## 题意

从右侧看二叉树，返回每层最右边那个节点的值，自上而下。

## 思路

我会用标准的层序 BFS，每层最后弹出的那个节点就是从右边能看到的。每轮先记下 `size`，正好弹出一层，边弹边更新 `last`，这一层结束时 `last` 就是答案。

拿 `[1,2,3,null,5,null,4]` 看。第一层只有 1；第二层是 2、3，取 3；第三层是 5、4，取 4，结果是 `[1,3,4]`。5 虽然在最底层，但它那一层右边还有 4，所以看不到它。

DFS 也能做，先递归右再递归左，每个深度第一次见到的节点就是右侧。这题和 102、103 是同一个骨架，我会优先写 BFS。

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


def rightSideView(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    q = deque([root])
    ans: List[int] = []
    while q:
        last = 0
        for _ in range(len(q)):
            node = q.popleft()
            last = node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(last)
    return ans


if __name__ == "__main__":
    root = TreeNode(1, TreeNode(2, None, TreeNode(5)), TreeNode(3, None, TreeNode(4)))
    assert rightSideView(root) == [1, 3, 4]
    only_left = TreeNode(1, TreeNode(2, TreeNode(3)))
    assert rightSideView(only_left) == [1, 2, 3]
    assert rightSideView(None) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(1, TreeNode(2, None, TreeNode(5)), TreeNode(3, None, TreeNode(4)))
assert rightSideView(root) == [1, 3, 4]
only_left = TreeNode(1, TreeNode(2, TreeNode(3)))
assert rightSideView(only_left) == [1, 2, 3]
assert rightSideView(None) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，$w$ 是最宽一层。

## Edge Cases

空树返回 `[]`。只有左链时每层只有一个节点，从右边也能看到它，所以整条链都在右视图里。某层右孩子缺失时，这一层最右的会是左侧露出来的节点。

## 追问

**左视图呢？**
同一个层序骨架，每层取第一个；先右后左入队的话就取每层最后一个。DFS 就先左后右，每个深度第一次见到的是左侧。时间 $O(n)$。

```python
from collections import deque


def leftSideView(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        first = None
        for i in range(len(q)):
            node = q.popleft()
            if i == 0:
                first = node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(first)
    return ans
```

**锯齿和层均值也是这个骨架吗？**
是，切层 BFS 不变，只换层内怎么收集，这三题常串着考。锯齿是已有奇数层时当前层 `reverse`，或者用双端 `appendleft`，独立卡见 `lc-103-binary-tree-zigzag-level-order-traversal`。均值是求和再除以本层个数，独立卡见 `lc-637-average-of-levels-in-binary-tree`。右视图就是「每层最后一个」。

```python
from collections import deque


def zigzagLevelOrder(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        if len(ans) % 2 == 1:
            level.reverse()
        ans.append(level)
    return ans


def averageOfLevels(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        total, size = 0, len(q)
        for _ in range(size):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(total / size)
    return ans
```
