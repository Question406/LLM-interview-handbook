---
id: lc-637-average-of-levels-in-binary-tree
section: binary-tree-bfs
order: 2
level: A
title: LC 637 · 二叉树的层平均值
quick: 层序 BFS 切层，每层求和再除以这一层的节点数，结果用浮点。时间 $O(n)$，额外空间 $O(w)$。
tags:
  - Tree
  - BFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 637. 二叉树的层平均值
    url: 'https://leetcode.cn/problems/average-of-levels-in-binary-tree/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一棵二叉树，计算从根所在层到最深层每一层节点值的算术平均数，按层次顺序返回结果。平均数只统计该层真实存在的节点，不把空孩子计为 0。

### 输入与输出

实现 `averageOfLevels(root) -> list[float]`，root 为 `TreeNode` 根节点。示例采用层序数组表示树，null 表示缺失的孩子；代码中对应 None。

### 约束与约定

- 原题树中有 1 到 10000 个节点。
- 节点值属于 32 位有符号整数范围。
- 每个平均值允许相对或绝对误差在 `1e-5` 内。

### 示例

```text
输入：root = [3,9,20,null,null,15,7]
输出：[3.00000,14.50000,11.00000]
```

示例三层的值分别为 [3]、[9,20]、[15,7]，均值为 3、14.5、11。

[官方原题与完整题面](https://leetcode.com/problems/average-of-levels-in-binary-tree/description/)。

## 解题思路与参考答案

## 题意

返回二叉树每一层节点值的平均值，自上而下，用浮点数。

## 思路

我会用切层 BFS，和右视图是同一个骨架。每轮先记下 `size=len(q)`，只处理这一层，把值累加起来，最后除以 `size` 写进答案。

拿 `[3,9,20,null,null,15,7]` 看。第一层只有 3，均值 3.0；第二层 9 和 20，和是 29，除以 2 得 14.5；第三层 15 和 7，均值 11.0。

DFS 按深度把值放进桶、最后再平均，也能做，但我会先写切层 BFS。

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


def averageOfLevels(root: Optional[TreeNode]) -> List[float]:
    if root is None:
        return []
    q = deque([root])
    ans: List[float] = []
    while q:
        total = 0
        size = len(q)
        for _ in range(size):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(total / size)
    return ans


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert averageOfLevels(root) == [3.0, 14.5, 11.0]
    assert averageOfLevels(TreeNode(1)) == [1.0]
    assert averageOfLevels(None) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
assert averageOfLevels(root) == [3.0, 14.5, 11.0]
assert averageOfLevels(TreeNode(1)) == [1.0]
assert averageOfLevels(None) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(w)$。Python 的 `int` 不会溢出；其他语言用 `long` 再除。

## Edge Cases

空树返回 `[]`。单节点时返回 `[root.val]` 的浮点。某层只有一个很大的数时，Python `int` 是安全的，其他语言先用 `long` 再除。

## 追问

**只要层和、不要均值呢？**
把除法去掉，每层累加完直接写进答案，骨架还是 `size=len(q)` 切层。这时要留意求和溢出；均值那题是除以 `size` 之后才得到浮点。

```python
from collections import deque


def levelSums(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        total = 0
        for _ in range(len(q)):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(total)
    return ans
```

**每层中位数怎么求？**
光累加就不够了，层内要先把值收集起来排序，取中间那个；偶数层是取两个平均还是别的，看题面。也可以在层内维护两个堆（对顶堆）在线求中位数，单层 $O(w\log w)$，整体 $O(n\log w)$。切层 BFS 还是负责决定谁和谁在同一层。

```python
from collections import deque


def medianOfLevels(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        vals = []
        for _ in range(len(q)):
            node = q.popleft()
            vals.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        vals.sort()
        m = len(vals)
        ans.append(vals[m // 2] if m % 2 else (vals[m // 2 - 1] + vals[m // 2]) / 2)
    return ans
```
