---
id: lc-1448-count-good-nodes-in-binary-tree
section: binary-tree-dfs
order: 3
level: A
title: LC 1448 · 统计二叉树中好节点的数目
quick: >-
  前序 DFS，把「根到父节点路径上的最大值」往下传。当前值不小于它就计一个好节点，再用 $\max$ 更新后传给孩子。时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1448. Count Good Nodes in Binary Tree
    url: https://leetcode.com/problems/count-good-nodes-in-binary-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

在二叉树中，如果从根节点到某个节点 X 的整条路径上，没有任何节点的值大于 X 的值，就称 X 为好节点。路径包括根和 X 本身，相同的值不会使 X 失去好节点资格。统计整棵树中好节点的总数。

### 输入与输出

实现 `goodNodes(root) -> int`。root 是非空二叉树的根；示例采用层序数组，null 表示缺失的孩子。每个节点按自己的根到节点路径独立判断。

### 约束与约定

- 节点数在 1 到 100000 之间。
- 节点值在 `[-10000,10000]`。
- 根节点本身始终是好节点。

### 示例

```text
输入：root = [3,1,4,3,null,1,5]
输出：4
```

示例中的根 3、左侧路径末尾的 3、右孩子 4 和其右孩子 5 共四个节点满足要求。

[官方原题与完整题面](https://leetcode.com/problems/count-good-nodes-in-binary-tree/description/)。

## 解题思路与参考答案

## 题意

二叉树中，若从根到节点 $X$ 的路径上没有任何节点的值大于 $X$，则 $X$ 是好节点。返回好节点个数。根一定是好节点。节点数在 $[1, 10^5]$，值在 $[-10^4, 10^4]$。

## 思路

我会用前序 DFS 往下传一个数。「路径上没有比我大的」等价于「我 $\ge$ 路径上的最大值」，所以只要知道这条路径的最大值就够了。往下传的 `mx` 是根到父节点的最大值。到节点时若 `node.val >= mx` 就计数，然后把 `max(mx, node.val)` 传给左右孩子。根调用时传 `-inf` 或根自己的值。

拿 `[3, 1, 4, 3, None, 1, 5]` 走一遍：根 3 是好节点；左孩子 1 小于 3，不算，它下面的 3 等于路径最大值 3，算；右孩子 4 算，4 下面的 1 不算，5 算。一共 4 个。

条件是「不大于」，所以等于也算好节点。朴素做法是每个节点回头扫整条路径，最坏 $O(n \cdot h)$；前序传参让每条路径的信息只算一次。

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


def goodNodes(root: Optional[TreeNode]) -> int:
    def dfs(node: Optional[TreeNode], mx: int) -> int:
        if node is None:
            return 0
        good = 1 if node.val >= mx else 0
        mx = max(mx, node.val)
        return good + dfs(node.left, mx) + dfs(node.right, mx)

    return dfs(root, float("-inf"))


if __name__ == "__main__":
    assert goodNodes(build_tree([3, 1, 4, 3, None, 1, 5])) == 4
    assert goodNodes(build_tree([3, 3, None, 4, 2])) == 3
    assert goodNodes(build_tree([1])) == 1
    assert goodNodes(build_tree([-1, -2, -1])) == 2
    assert goodNodes(build_tree([5, 4, 3, 2, 1])) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert goodNodes(build_tree([3, 1, 4, 3, None, 1, 5])) == 4
assert goodNodes(build_tree([3, 3, None, 4, 2])) == 3
assert goodNodes(build_tree([1])) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。额外空间 $O(h)$，链状最坏 $O(n)$。

## 边界

- 只有根时答案是 $1$。
- 和路径最大值相等也算好节点，比较用 `>=`。
- 有负数值时 `mx` 初值用 $-\infty$，用 $0$ 的话负数根会被漏掉。

## 追问

**树退化成 $10^5$ 的链，递归爆栈怎么办？**
改成显式栈，栈里存 `(node, mx)`，逻辑不变。Python 默认递归上限是 $1000$，链状输入必爆，除非调 `sys.setrecursionlimit`。

```python
def goodNodesIter(root):
    if root is None:
        return 0
    ans = 0
    stack = [(root, root.val)]
    while stack:
        node, mx = stack.pop()
        if node.val >= mx:
            ans += 1
        mx = max(mx, node.val)
        if node.left:
            stack.append((node.left, mx))
        if node.right:
            stack.append((node.right, mx))
    return ans
```

**要求「严格大于路径上所有祖先」呢？**
比较换成 `node.val > mx`，根要单独算一个，因为根没有祖先。只改判断条件，传参方式不变。
