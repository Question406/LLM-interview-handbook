---
id: lc-700-search-in-a-binary-search-tree
section: bst
order: 1
level: A
title: LC 700 · 二叉搜索树中的搜索
quick: "从根开始比较：目标更小走左子树，更大走右子树，相等就返回这个节点。BST 搜索只走一条路径，写成循环时间 $O(h)$，额外空间 $O(1)$。"
tags:
  - Tree
  - BST
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 700. Search in a Binary Search Tree
    url: https://leetcode.com/problems/search-in-a-binary-search-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定一棵二叉搜索树的根和目标值 val，查找值恰好等于 val 的节点。如果找到，返回以该节点为根的原子树；如果不存在，返回空节点。二叉搜索树满足每个节点左子树所有值更小、右子树所有值更大。

### 输入与输出

实现 `searchBST(root, val) -> TreeNode | None`。返回的是树中的节点对象，不是值列表，也无需复制或修改树；示例用层序数组显示返回子树的结构，null 表示空孩子。

### 约束与约定

- 树中有 1 到 5000 个节点。
- 节点值与 val 都在 `[1,10000000]`，输入保证是合法二叉搜索树。

### 示例

```text
输入：root = [4,2,7,1,3], val = 2
输出：[2,1,3]
```

示例找到值为 2 的节点，其左右孩子为 1、3，因此返回子树展示为 [2,1,3]。

[官方原题与完整题面](https://leetcode.com/problems/search-in-a-binary-search-tree/description/)。

## 解题思路与参考答案

## 题意

给 BST 的根和整数 `val`，找到值等于 `val` 的节点，返回以它为根的子树；不存在返回 `None`。节点数 $[1, 5000]$，值互异。

## 思路

利用 BST 的性质，每比较一次就能扔掉一边子树，只沿一条路往下走。左子树的值都比根小，右子树都比根大，所以 `val` 更小只可能在左边，更大只可能在右边，走到 `None` 就说明不存在。

拿 `[4,2,7,1,3]` 找 `2`：`2` 比 `4` 小，往左走一步就碰到 `2`，返回以它为根的子树 `[2,1,3]`。找 `5` 的话，`5` 比 `4` 大往右到 `7`，再比 `7` 小往左，左边是空的，返回 `None`。

普通二叉树要 DFS 整棵树，$O(n)$。BST 只走一条根到叶的路径，$O(h)$，平衡时 $O(\log n)$，退化成链还是 $O(n)$。递归写法是尾递归，我直接写成 `while` 循环，省掉栈。

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


def to_level_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    out: List[Optional[int]] = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def searchBST(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    while root and root.val != val:
        root = root.left if val < root.val else root.right
    return root


if __name__ == "__main__":
    root = build_tree([4, 2, 7, 1, 3])
    assert to_level_list(searchBST(root, 2)) == [2, 1, 3]
    assert searchBST(root, 5) is None
    assert searchBST(root, 4) is root
    assert to_level_list(searchBST(root, 7)) == [7]
    assert searchBST(build_tree([1]), 0) is None
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = build_tree([4, 2, 7, 1, 3])
assert to_level_list(searchBST(root, 2)) == [2, 1, 3]
assert searchBST(root, 5) is None
assert searchBST(root, 4) is root
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(h)$，平衡时 $O(\log n)$，最坏 $O(n)$。额外空间 $O(1)$。

## 边界

目标就是根时，循环一次都不进，直接返回根。

目标不存在时，走到 `None` 返回。

树退化成链也照样正确，只是变成 $O(n)$。

## 追问

**插入一个新值怎么做（LC 701）？**
同样按值走单路，走到空位置就把新节点挂上去。题目保证新值不存在，插成叶子就行，不需要旋转，时间 $O(h)$。

```python
def insertIntoBST(root, val):
    node = TreeNode(val)
    if root is None:
        return node
    cur = root
    while True:
        if val < cur.val:
            if cur.left is None:
                cur.left = node
                break
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = node
                break
            cur = cur.right
    return root
```

**找不到时要返回最接近的值呢（LC 270）？**
在同一条搜索路径上边走边更新 `abs(node.val - target)` 最小的节点就行。最接近的值一定在这条路径上，因为离开某个节点往一侧走的时候，另一侧整棵子树离目标更远。

相关：删除节点（`lc-450-delete-node-in-a-bst`）也是先用这套走法定位。
