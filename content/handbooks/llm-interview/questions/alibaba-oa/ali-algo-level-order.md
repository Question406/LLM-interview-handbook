---
id: ali-algo-level-order
section: alibaba-oa
order: 35
level: B
title: 阿里手撕：二叉树层序及变形要准备哪些？
quick: "用队列 BFS，每轮先记下 `size=q.size()`，只弹出这么多个，正好是一层。锯齿、右侧视图、层均值都是同一骨架，只换收集方式。"
tags:
  - Alibaba
  - BFS
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 二叉树的层序遍历
    url: https://leetcode.cn/problems/binary-tree-level-order-traversal/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 题目描述

给定一棵二叉树的根节点，分别实现三种从根到叶逐层观察树的接口。节点使用 `TreeNode(val, left, right)`，`None` 表示没有节点。

### 接口与结果

- `level_order(root)`：返回二维列表，第 0 项是根所在层，此后按深度递增；每层的节点值从左到右排列。
- `zigzag_level_order(root)`：仍按层返回，但第 0 层从左到右，第 1 层从右到左，之后交替方向。
- `right_side_view(root)`：返回从树的右侧能看到的节点值，每层只取最右侧的一个，顺序从上到下。

三个接口都不修改树；空树均返回空列表。示例中的层序数组用 `null` 标记缺失孩子，实际调用时需构造节点。

### 示例

```text
树的层序表示：[3,9,20,null,null,15,7]
level_order(root)        -> [[3],[9,20],[15,7]]
zigzag_level_order(root) -> [[3],[20,9],[15,7]]
right_side_view(root)    -> [3,20,7]
level_order(None)        -> []
```

这是根据相关算法考点整理的手册练习接口，不是某一场面试的逐字题干。

## 解题思路与参考答案

## 真题 / 考点说明

- 对应：LeetCode 102 及 103 / 199 变形

我会用队列做 BFS，每一轮开始先记下这一层有多少个节点，只弹这么多个，正好切出一层。锯齿、右侧视图、层均值都是同一个骨架，只换收集结果的方式。别把整棵树丢进一个 list 再事后切层；空根直接返回空。

## 思路

队列里先放根。每一轮开始记下 `size=len(q)`，只弹出这么多个，弹出时把左右孩子入队。拿代码里那棵树来说，第一轮只弹 3；第二轮弹 9 和 20，顺手把 15、7 放进队列；第三轮就是 15、7。

变形只改收集方式。102 每层 append 一个 list；103 偶数层再反转，或者这一层用双端队列头插、尾插；199 取每层最后一个，或者从右往左 BFS 取第一个，就是右视图。

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


def level_order(root: Optional[TreeNode]) -> List[List[int]]:
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


def zigzag_level_order(root: Optional[TreeNode]) -> List[List[int]]:
    levels = level_order(root)
    for i, level in enumerate(levels):
        if i % 2 == 1:
            level.reverse()
    return levels


def right_side_view(root: Optional[TreeNode]) -> List[int]:
    return [level[-1] for level in level_order(root)]


if __name__ == "__main__":
    #     3
    #    / \
    #   9  20
    #     /  \
    #    15   7
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert level_order(root) == [[3], [9, 20], [15, 7]]
    assert zigzag_level_order(root) == [[3], [20, 9], [15, 7]]
    assert right_side_view(root) == [3, 20, 7]
    assert level_order(None) == []
    print("ok")
```

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert level_order(root) == [[3], [9, 20], [15, 7]]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

时间 $O(n)$，空间 $O(w)$，$w$ 是最宽那一层（最坏 $O(n)$）。DFS 按深度往桶里塞也能过题，但层序我先给 BFS。

## 追问

**哪些边界容易写错？**
空树、只有左链、完全二叉树最底层最宽。切层要用当轮的 `size`，不要用 `while q` 一次掏光。

**换成图或多叉树呢？**
骨架还是 BFS，层序就是 BFS。图必须加 `visited`，否则有环会死循环；连通块计数按岛屿的思路做。
