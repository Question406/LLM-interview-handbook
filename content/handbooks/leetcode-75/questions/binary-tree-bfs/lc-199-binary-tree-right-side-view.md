---
id: lc-199-binary-tree-right-side-view
section: binary-tree-bfs
order: 1
level: S
title: LC 199 · 二叉树的右视图
quick: 层序 BFS，每层取最后一个节点；从右往左入队的话就取每层第一个。时间 $O(n)$，额外空间 $O(w)$。
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 199. Binary Tree Right Side View
    url: 'https://leetcode.com/problems/binary-tree-right-side-view/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定二叉树根节点 `root`。想象从树的右侧向左观察，每一层只能看到这一层最靠右的那个节点。请按从上到下的顺序，返回这些可见节点的值。某层没有右孩子时，左子树中的节点也可能成为这一层最靠右的节点。

### 输入与输出

实现 `rightSideView(root) -> List[int]`。输入是 TreeNode 根对象或 None；空树返回 `[]`。不需要修改树，也不返回节点对象。

### 约束

- 节点数在 0 到 100 之间。
- `-100 <= Node.val <= 100`。
- 示例用层序序列描述树，null 表示缺失的孩子，不是值为0的节点。

### 示例

```text
输入：root = [1,2,3,null,5,null,4]
输出：[1,3,4]
```

[LeetCode 原题](https://leetcode.com/problems/binary-tree-right-side-view/description/)

## 解题思路与参考答案

## 题意

从右侧看二叉树，返回每层最右边那个节点的值，自上而下。节点数 $[0, 100]$。

## 思路

我会用层序 BFS，每层最后弹出的那个节点就是从右边看到的。每轮先记下 `size`，正好弹出一层，把这一层最后一个节点的值收进答案。

拿 `[1, 2, 3, None, 5, None, 4]` 走一遍：第一层只有 1；第二层是 2、3，取 3；第三层是 5、4，取 4，结果是 `[1, 3, 4]`。

只沿右孩子链取值会出错。某层右侧缺失时，最右节点可能来自左子树，比如测试里的 `[1, 2, 3, 4, None, None, None, 5]`，第三层的 4 和第四层的 5 都在左子树里。

DFS 也可以：先递归右再递归左，每个深度第一次见到的就是最右侧。这和最大层内元素和（`lc-1161-maximum-level-sum-of-a-binary-tree`）是同一骨架，我会优先写 BFS。

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


def build_tree(vals: List[Optional[int]]) -> Optional[TreeNode]:
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    q = deque([root])
    i = 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root


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
    assert rightSideView(build_tree([1, 2, 3, None, 5, None, 4])) == [1, 3, 4]
    assert rightSideView(build_tree([1, 2, 3, 4, None, None, None, 5])) == [1, 3, 4, 5]
    assert rightSideView(build_tree([1, None, 3])) == [1, 3]
    assert rightSideView(build_tree([])) == []
    assert rightSideView(build_tree([1, 2, None, 3])) == [1, 2, 3]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert rightSideView(build_tree([1, 2, 3, None, 5, None, 4])) == [1, 3, 4]
assert rightSideView(build_tree([1, 2, 3, 4, None, None, None, 5])) == [1, 3, 4, 5]
assert rightSideView(build_tree([1, None, 3])) == [1, 3]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，$w$ 是最宽一层。

## Edge Cases

- 空树返回 `[]`。
- 只有左链时，右侧看不见别的节点，每层最右就是这条链上的节点。
- 某层右孩子缺失时，该层最右会落到左侧露出来的节点。

## 追问

**DFS 怎么写？**
先右后左递归，带深度 `d`。`d == len(ans)` 说明这一层第一次到达，先右后左保证第一次到达的是最右节点。时间 $O(n)$，额外空间 $O(h)$。

```python
def rightSideViewDFS(root):
    ans = []

    def dfs(node, d):
        if node is None:
            return
        if d == len(ans):
            ans.append(node.val)
        dfs(node.right, d + 1)
        dfs(node.left, d + 1)

    dfs(root, 0)
    return ans
```

**左视图呢？**
同一层序骨架，每层取第一个，或者先右后左入队、取每层末尾。DFS 版把递归顺序换成先左后右就行。

```python
from collections import deque


def leftSideView(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        for i in range(len(q)):
            node = q.popleft()
            if i == 0:
                ans.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return ans
```
