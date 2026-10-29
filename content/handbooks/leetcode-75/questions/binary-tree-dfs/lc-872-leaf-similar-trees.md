---
id: lc-872-leaf-similar-trees
section: binary-tree-dfs
order: 2
level: A
title: LC 872 · 叶子相似的树
quick: >-
  两棵树各做一次先左后右的 DFS，收集叶子值，再比较两个序列。时间 $O(n_1+n_2)$，额外空间
  $O(n_1+n_2)$；改用生成器边走边比，可以降到 $O(h_1+h_2)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 872. Leaf-Similar Trees
    url: 'https://leetcode.com/problems/leaf-similar-trees/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

把一棵二叉树的所有叶子节点按从左到右的顺序取出其值，得到这棵树的叶值序列。给定两棵二叉树 root1、root2，判断它们的叶值序列是否完全相同，包括顺序和重复值的次数。

### 接口与输出

实现 `leafSimilar(root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool`。只有没有左右孩子的节点才算叶子；两棵树的整体形状不必相同。

### 合法输入与约束

每棵树均有 1 到 200 个节点，节点值为 0 到 200。示例中的数组是层序树表示，不是已经排列好的叶值序列。

### 示例

```text
输入：root1 = [3,5,1,6,2,9,8,null,null,7,4], root2 = [3,5,1,6,7,4,2,null,null,null,null,null,null,9,8]
输出：true
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/leaf-similar-trees/description/)。

## 解题思路与参考答案

## 题意

一棵二叉树所有叶子从左到右排成的值序列叫叶值序列。给两棵树 `root1`、`root2`，判断它们的叶值序列是否相同。每棵树节点数在 $[1, 200]$，值在 $[0, 200]$。

## 思路

我会对两棵树各做一次先左后右的 DFS，把叶子按顺序收集出来再比列表。前序、中序、后序只要都是先左后右，访问叶子的相对顺序就一样，都是从左到右，所以写哪种都行。遇到左右孩子都为空的节点就记下值。

拿测试里的 `[1, 2, 3]` 和 `[1, 3, 2]` 来比：前者叶子序列是 `[2, 3]`，后者是 `[3, 2]`，不相等。`[1, 2]` 和 `[2, 2]` 根值不同，叶子都是 `[2]`，判相等。

判叶子要看两个孩子都为空，只看一边会把单孩子节点当成叶子。两棵树的形状、深度可以完全不同，只比叶子序列。

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


def leafSimilar(root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
    def leaves(root: Optional[TreeNode]) -> List[int]:
        out: List[int] = []
        stack = [root] if root else []
        while stack:
            node = stack.pop()
            if node.left is None and node.right is None:
                out.append(node.val)
                continue
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)
        return out

    return leaves(root1) == leaves(root2)


if __name__ == "__main__":
    t1 = build_tree([3, 5, 1, 6, 2, 9, 8, None, None, 7, 4])
    t2 = build_tree([3, 5, 1, 6, 7, 4, 2, None, None, None, None, None, None, 9, 8])
    assert leafSimilar(t1, t2) is True
    assert leafSimilar(build_tree([1, 2, 3]), build_tree([1, 3, 2])) is False
    assert leafSimilar(build_tree([1]), build_tree([1])) is True
    assert leafSimilar(build_tree([1, 2]), build_tree([2, 2])) is True
    assert leafSimilar(build_tree([1, 2, 3]), build_tree([1, 2, None, 3])) is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
t1 = build_tree([3, 5, 1, 6, 2, 9, 8, None, None, 7, 4])
t2 = build_tree([3, 5, 1, 6, 7, 4, 2, None, None, None, None, None, None, 9, 8])
assert leafSimilar(t1, t2) is True
assert leafSimilar(build_tree([1, 2, 3]), build_tree([1, 3, 2])) is False
assert leafSimilar(build_tree([1]), build_tree([1])) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n_1+n_2)$。额外空间 $O(n_1+n_2)$，来自栈和叶子列表。

## Edge Cases

- 单节点树的根本身就是叶子。
- 叶子数量不同时，列表长度不同，直接不等。
- 形状完全不同但叶子序列一致，判相等，本题不关心结构。

## 追问

**能不能不存完整序列、提前停？**
能，用生成器惰性产出叶子，`zip_longest` 逐个比较，第一个不等就返回 `False`。额外空间只剩两棵树的递归栈 $O(h_1+h_2)$，适合叶子很多、差异出现得早的情况。

```python
from itertools import zip_longest


def leafSimilarLazy(root1, root2):
    def gen(node):
        if node is None:
            return
        if node.left is None and node.right is None:
            yield node.val
            return
        yield from gen(node.left)
        yield from gen(node.right)

    sentinel = object()
    return all(
        a == b for a, b in zip_longest(gen(root1), gen(root2), fillvalue=sentinel)
    )
```

**为什么迭代栈先压右再压左？**
因为栈后进先出，先压右孩子，弹出时左孩子先处理，叶子顺序才是从左到右。反过来压，得到的是从右到左的序列；两棵树都反着也能比对，但和题意定义不一致，追问时容易说错。
