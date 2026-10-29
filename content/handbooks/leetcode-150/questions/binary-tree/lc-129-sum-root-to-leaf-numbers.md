---
id: lc-129-sum-root-to-leaf-numbers
section: binary-tree
order: 10
level: A
title: LC 129 · 求根节点到叶节点数字之和
quick: >-
  DFS 带着当前前缀往下走，每进一层做 `acc = acc * 10 + val`，到叶子把 `acc` 加进答案，和 LC 112 是同一个骨架。时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 129. 求根节点到叶节点数字之和
    url: 'https://leetcode.cn/problems/sum-root-to-leaf-numbers/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一棵每个节点只存一位十进制数字的二叉树。从根到任意叶节点的数字依次拼接，形成一个非负整数。求所有根到叶路径所表示整数的总和；每条路径按它在树中的出现分别计算。

### 输入与输出

实现 `sumNumbers(root: Optional[TreeNode]) -> int`。叶节点没有孩子；路径中的下一位是拼接到前一位之后，不是把沿途数字直接相加。示例用层序列表描述树，实际接收节点对象。

### 约束

- 节点数为 1 到 1000，树深度不超过 10。
- 每个节点值在 0 到 9；题目保证最终总和能用 32 位整数表示。

### 示例

```text
输入：root = [1,2,3]
输出：25
```

树中两条路径形成 12 与 13，返回 `12+13=25`。

## 解题思路与参考答案

## 题意

每个节点的值是 $0$ 到 $9$，根到叶的每条路径表示一个十进制数。返回所有这些数的和。

## 思路

我会用深度优先，带着当前的前缀数往下传，因为往下走一层就相当于在数字末尾添一位。进入节点先做 `acc = acc * 10 + node.val`；如果是叶子，就把 `acc` 加进总和，否则继续递归左右。

拿示例 `[4, 9, 0, 5, 1]` 走一遍：走到 $9$ 时前缀是 $49$，再到叶子 $5$ 和 $1$，得到 $495$ 和 $491$；根的右孩子 $0$ 是叶子，得到 $40$。合起来 $495+491+40=1026$。

和 LC 112 是同一个骨架，那题判断路径和，这里收集的是路径数字。空树的和是 $0$。

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


def sumNumbers(root: Optional[TreeNode]) -> int:
    def dfs(node: Optional[TreeNode], acc: int) -> int:
        if node is None:
            return 0
        acc = acc * 10 + node.val
        if node.left is None and node.right is None:
            return acc
        return dfs(node.left, acc) + dfs(node.right, acc)

    return dfs(root, 0)


if __name__ == "__main__":
    assert sumNumbers(TreeNode(1, TreeNode(2), TreeNode(3))) == 25
    root = TreeNode(4, TreeNode(9, TreeNode(5), TreeNode(1)), TreeNode(0))
    assert sumNumbers(root) == 1026
    assert sumNumbers(None) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert sumNumbers(TreeNode(1, TreeNode(2), TreeNode(3))) == 25
root = TreeNode(4, TreeNode(9, TreeNode(5), TreeNode(1)), TreeNode(0))
assert sumNumbers(root) == 1026
assert sumNumbers(None) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(h)$。路径长度受题面约束，`acc` 用 `int` 即可。

## Edge Cases

单节点时答案就是那一位数字。值为 $0$ 的节点也合法，前缀乘十再加 $0$，比如 $10$。只有一侧孩子时，不要在空的那一侧把当前 `acc` 当成叶子加进去。

## 追问

**能不能用链表或数组存下每一位再算？**
能做，但从叶子往回乘 $10^k$ 要先知道深度，或者额外存一个数组再 `int(''.join(...))`。DFS 带着 `acc = acc * 10 + val` 已经是同样的信息，还少一次拼装。回溯时只有改的是 `acc` 的引用才需要还原；本题 `acc` 按值传递，回到上一层自然就是旧值。

**换成二进制路径和（LC 1022）呢？**
每一位是 $0/1$，把十进制的 $10$ 换成 $2$ 就行：`acc = (acc << 1) | node.val`，到叶子把 `acc` 加入总和，其余骨架不变，时间 $O(n)$。

```python
def sumRootToLeaf(root):
    def dfs(node, acc):
        if node is None:
            return 0
        acc = (acc << 1) | node.val
        if node.left is None and node.right is None:
            return acc
        return dfs(node.left, acc) + dfs(node.right, acc)

    return dfs(root, 0)
```
