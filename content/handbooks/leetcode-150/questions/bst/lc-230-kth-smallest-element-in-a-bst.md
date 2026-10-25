---
id: lc-230-kth-smallest-element-in-a-bst
section: bst
order: 2
level: S
title: LC 230 · 二叉搜索树中第K小的元素
quick: "BST 的中序遍历按值递增，用栈做中序，数到第 $k$ 个弹出的节点就返回。只遍历需要的前缀，时间约 $O(h+k)$、最坏 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - BST
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 230. 二叉搜索树中第K小的元素
    url: https://leetcode.cn/problems/kth-smallest-element-in-a-bst/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一棵二叉搜索树的根节点 `root` 和正整数 `k`，返回树中按节点值从小到大排列后的第 k 个值。k 从 1 开始计数，因此 k=1 表示最小值。二叉搜索树满足左子树所有值小于根值、右子树所有值大于根值。

### 输入与输出

实现 `kthSmallest(root, k) -> int`，返回节点值，而不是节点对象。输入保证 k 在树的节点数量范围内，不需要修改树。

### 约束

- 设树有 n 个节点，`1 <= k <= n <= 10^4`。
- `0 <= Node.val <= 10^4`。
- 示例用层序序列描述树，null 表示缺失的孩子。

### 示例

```text
输入：root = [3,1,4,null,2], k = 1
输出：1
```

[LeetCode 原题](https://leetcode.com/problems/kth-smallest-element-in-a-bst/description/)

## 解题思路与参考答案

## 题意

给一棵 BST 和正整数 $k$，返回第 $k$ 小的节点值，$k$ 从 $1$ 开始数。

## 思路

我会用栈做迭代中序，因为 BST 的中序就是按值从小到大访问，而迭代写法可以在第 $k$ 个时直接停下，不用先保存完整序列。每弹出一个节点就把 $k$ 减一，减到 $0$ 就返回这个值。

拿示例 `[3, 1, 4, null, 2]` 求 $k=3$：先沿左链压入 $3$、$1$；弹出 $1$，这是第 $1$ 个；转到它的右孩子 $2$，压栈再弹出，第 $2$ 个；接着弹出 $3$，第 $3$ 个，返回 $3$。

如果节点带着子树规模，还可以按左子树大小二分往下走，这个放到追问里讲。

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


def kthSmallest(root: Optional[TreeNode], k: int) -> int:
    stack = []
    cur = root
    while True:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(1, None, TreeNode(2)), TreeNode(4))
    assert kthSmallest(root, 1) == 1
    assert kthSmallest(root, 3) == 3
    root2 = TreeNode(5, TreeNode(3, TreeNode(2, TreeNode(1)), TreeNode(4)), TreeNode(6))
    assert kthSmallest(root2, 3) == 3
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(3, TreeNode(1, None, TreeNode(2)), TreeNode(4))
assert kthSmallest(root, 1) == 1
assert kthSmallest(root, 3) == 3
root2 = TreeNode(5, TreeNode(3, TreeNode(2, TreeNode(1)), TreeNode(4)), TreeNode(6))
assert kthSmallest(root2, 3) == 3
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间最坏 $O(n)$，树平衡时约 $O(h+k)$。额外空间 $O(h)$。

## 边界

$k=1$ 是最左节点，也就是最小值；$k=n$ 是最右节点，也就是最大值。左链很深时，栈或递归是 $O(h)$，最坏 $O(n)$。

## 追问

**改成第 $k$ 大呢？**
把中序反过来：一直向右压栈，弹出后走左孩子的右链，数到 $k$ 停。也可以先数出节点总数 $n$，再求第 $n-k+1$ 小，代价是多一次 $O(n)$ 计数；反向中序不需要先知道 $n$。

```python
def kthLargest(root, k):
    stack, cur = [], root
    while True:
        while cur:
            stack.append(cur)
            cur = cur.right
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.left
```

**查询很频繁、树还会插入删除，怎么办？**
给每个节点维护子树规模 `size`。查询时 `leftSize = root.left.size if root.left else 0`；如果 $k \le leftSize$ 就走左，$k = leftSize+1$ 就返回根，否则 $k \gets k-leftSize-1$ 再走右。每次 $O(h)$，插入删除时同步改 `size`。它和 BST 迭代器是同一个中序思想，迭代器适合按顺序一个个吐出，`size` 适合随机查第 $k$ 个。独立卡见 `lc-173-binary-search-tree-iterator`。

```python
def kthSmallest_with_size(root, k):
    while root:
        left = root.left.size if root.left else 0
        if k <= left:
            root = root.left
        elif k == left + 1:
            return root.val
        else:
            k -= left + 1
            root = root.right
```
