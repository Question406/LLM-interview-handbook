---
id: lc-102-binary-tree-level-order-traversal
section: binary-tree-bfs
order: 3
level: S
title: LC 102 · 二叉树的层序遍历
quick: "用队列做 BFS，每一层开始时先记下队列长度 `size`，只弹出这么多个，正好是一层。空根返回空列表。时间 $O(n)$，额外空间 $O(w)$。"
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 102. 二叉树的层序遍历
    url: https://leetcode.cn/problems/binary-tree-level-order-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定二叉树根节点 `root`，按从上到下的层次收集节点值。同一层中的节点按从左到右的顺序排列，每一层单独构成一个列表。空树没有任何层。

### 输入与输出

实现 `levelOrder(root) -> List[List[int]]`，返回按层组织的二维列表；空树返回 `[]`。接口接收 TreeNode 对象或 None，不直接接收序列化数组。

### 约束

- 节点数在 0 到 2000 之间。
- `-1000 <= Node.val <= 1000`。
- 示例中的树采用层序序列表示，null 表示缺失的孩子；该表示只用于描述输入。

### 示例

```text
输入：root = [3,9,20,null,null,15,7]
输出：[[3],[9,20],[15,7]]
```

[LeetCode 原题](https://leetcode.com/problems/binary-tree-level-order-traversal/description/)

## 解题思路与参考答案

## 题意

按层返回二叉树节点值，每一层一个列表，从根到叶、每层从左到右。

## 思路

我会用队列 BFS，关键是每轮开始先记下 `size=len(q)`。队列先放根；每一轮只弹出 `size` 个节点，收成一层，同时把它们的左右孩子入队。这一轮新入队的都属于下一层，不会混进当前层。空根直接返回 `[]`。

拿 `[3,9,20,null,null,15,7]` 看。第一轮队列里只有 3，`size` 是 1，收 `[3]`，入队 9 和 20；第二轮 `size` 是 2，收 `[9,20]`，入队 15 和 7；第三轮收 `[15,7]`。

常见的写错是一次把队列掏空、事后再切层。用当轮的 `size` 切开就不会乱。

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


def levelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []
    q = deque([root])
    ans: List[List[int]] = []
    while q:
        level: List[int] = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(level)
    return ans


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert levelOrder(root) == [[3], [9, 20], [15, 7]]
    assert levelOrder(TreeNode(1)) == [[1]]
    assert levelOrder(None) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
assert levelOrder(root) == [[3], [9, 20], [15, 7]]
assert levelOrder(TreeNode(1)) == [[1]]
assert levelOrder(None) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，$w$ 是最宽一层，完全二叉树最宽在底层。

## 边界

空树返回 `[]`，别返回 `[[]]`。单节点时一层一个值。只有左链时，每层恰好一个节点。

## 追问

**自底向上层序（LC 107）呢？**
先按本题从根到叶收集，最后把外层列表反转，或者每层 `appendleft` / 插到下标 $0$。层内还是从左到右，只是层的顺序反过来，时间 $O(n)$。别想着在队列里从叶往根走，没有父指针做不到。

```python
from collections import deque

def levelOrderBottom(root):
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
        ans.append(level)
    ans.reverse()
    return ans
```

**能改成 DFS 吗？**
能，按深度把值塞进对应的桶。进入节点时如果 `d == len(ans)` 就新开一层，然后先左后右递归，结果和 BFS 一样。不过白板上的标准答法还是切层 BFS。DFS 栈深最坏 $O(n)$；BFS 的空间取决于宽度，树很宽时才占得多。

```python
def levelOrder_dfs(root):
    ans = []

    def dfs(node, d):
        if node is None:
            return
        if d == len(ans):
            ans.append([])
        ans[d].append(node.val)
        dfs(node.left, d + 1)
        dfs(node.right, d + 1)

    dfs(root, 0)
    return ans
```
