---
id: lc-1372-longest-zigzag-path-in-a-binary-tree
section: binary-tree-dfs
order: 5
level: A
title: LC 1372 · 二叉树中的最长交错路径
quick: >-
  DFS 时给每个节点带两个状态：最后一步向左的交错长度 l，最后一步向右的长度 r。走到左孩子时延续 r，得到 r+1，另一状态归 0；走到右孩子时延续
  l。遍历中更新最大边数，时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 1372. Longest ZigZag Path in a Binary Tree
    url: 'https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定二叉树，从任意节点出发，先任选向左或向右走到它的一个孩子；之后每走一步都必须更换方向，只能沿孩子指针向下继续。这样的路径称为交错路径，长度按经过的边数计算。求整棵树中最长的交错路径长度。

### 接口与输出

实现 `longestZigZag(root: Optional[TreeNode]) -> int`。路径不要求从根出发或到叶子结束，单个节点的路径长度为 0；返回最大长度，不需要返回路径节点。

### 合法输入与约束

树有 1 到 50000 个节点，`1 <= Node.val <= 100`。节点值不参与路径合法性判定；示例用层序数组和 null 表示树结构。

### 示例

```text
输入：root = [1,null,1,1,1,null,null,1,1,null,1,null,null,null,1]
输出：3
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/description/)。

## 解题思路与参考答案

## 题意

交错路径：从任意节点出发，选一个方向（左或右）走到孩子，之后每一步必须换方向，走不动为止。长度是经过的边数，单个节点长度为 $0$。返回树中最长交错路径的长度。节点数 $[1, 5 \times 10^4]$。

## 思路

我会做一遍 DFS，每个节点带着两个状态往下传，因为一条交错路径能不能延续，只取决于上一步往哪个方向走。`l` 是到达当前节点时最后一步向左（当前节点是父的左孩子）的交错长度，`r` 是最后一步向右的长度。往左孩子走，上一步必须是向右，新长度是 `r + 1`，向右的那条链同时断了，记 $0$；往右孩子走对称，新长度是 `l + 1`。每个节点用 `max(l, r)` 更新答案，根从 `(0, 0)` 开始。

举个小例子，一条路径依次向右、向左、向右走三步。第一步到达的节点状态是 `(0, 1)`；第二步向左，`l = 1 + 1 = 2`；第三步向右，`r = 2 + 1 = 3`，答案更新成 3。

容易错的地方是「换不了方向就归零」。从父节点到这个孩子本身就是一条长度 $1$ 的新交错路径，上面的写法自动覆盖了这点：到左孩子时 `l = r + 1`，至少是 $1$。

朴素做法是以每个节点为起点、两个方向各模拟一遍，最坏 $O(n^2)$。

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


def longestZigZag(root: Optional[TreeNode]) -> int:
    ans = 0
    stack = [(root, 0, 0)] if root else []
    while stack:
        node, l, r = stack.pop()
        ans = max(ans, l, r)
        if node.left:
            stack.append((node.left, r + 1, 0))
        if node.right:
            stack.append((node.right, 0, l + 1))
    return ans


if __name__ == "__main__":
    t1 = build_tree([1, None, 1, 1, 1, None, None, 1, 1, None, 1, None, None, None, 1])
    assert longestZigZag(t1) == 3
    t2 = build_tree([1, 1, 1, None, 1, None, None, 1, 1, None, 1])
    assert longestZigZag(t2) == 4
    assert longestZigZag(build_tree([1])) == 0
    assert longestZigZag(build_tree([1, 1, None, 1, None, 1])) == 1
    chain = TreeNode(0)
    cur = chain
    for i in range(1, 50001):
        nxt = TreeNode(i)
        if i % 2:
            cur.left = nxt
        else:
            cur.right = nxt
        cur = nxt
    assert longestZigZag(chain) == 50000
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
t1 = build_tree([1, None, 1, 1, 1, None, None, 1, 1, None, 1, None, None, None, 1])
assert longestZigZag(t1) == 3
t2 = build_tree([1, 1, 1, None, 1, None, None, 1, 1, None, 1])
assert longestZigZag(t2) == 4
assert longestZigZag(build_tree([1])) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。额外空间 $O(h)$，栈里最多一条路径的节点加上兄弟。

## Edge Cases

- 单节点时答案是 $0$。
- 全左链每一步都同方向，答案是 $1$，别写成 $0$。
- 每一步左右交替的长路径，答案是 $n-1$；这里用显式栈，$5 \times 10^4$ 深也不会爆 Python 递归上限。

## 追问

**递归写法呢？**
同样把两个状态作为参数，更直观，但链状输入要调高递归上限。

```python
def longestZigZagRec(root):
    ans = 0

    def dfs(node, l, r):
        nonlocal ans
        if node is None:
            return
        ans = max(ans, l, r)
        dfs(node.left, r + 1, 0)
        dfs(node.right, 0, l + 1)

    dfs(root, 0, 0)
    return ans
```

**后序写法怎么做，让每个节点返回「从我出发先往左 / 先往右」的最长长度？**
设 `go_left(node) = 1 + go_right(node.left)`（左孩子存在时），`go_right(node) = 1 + go_left(node.right)`，空孩子方向记 $0$。答案是所有节点两者的最大值。前序是从上面带下来，后序是从下面汇上来，两种都是 $O(n)$。
