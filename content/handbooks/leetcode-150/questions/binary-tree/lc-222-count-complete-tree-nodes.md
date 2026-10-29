---
id: lc-222-count-complete-tree-nodes
section: binary-tree
order: 13
level: A
title: LC 222 · 完全二叉树的节点个数
quick: >-
  沿最左和最右路径各量一次高度，相等说明当前子树是满树，节点数直接是 $2^h-1$；不等就递归统计左右子树再加根。左右必有一侧是满的，所以时间
  $O(h^2)$，额外空间 $O(h)$。
tags:
  - Tree
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 222. 完全二叉树的节点个数
    url: 'https://leetcode.cn/problems/count-complete-tree-nodes/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一棵完全二叉树，返回节点总数。完全二叉树是指除最后一层外每层都填满，最后一层的节点从左侧连续排列。可以利用输入具有这个性质，但不能把任意二叉树都当作完全二叉树。

### 输入与输出

实现 `countNodes(root) -> int`，root 为 TreeNode 或 None。示例使用层序数组表示树；空树的节点数为 0。

### 约束与约定

- 节点数在 0 到 50000 之间，节点值在 `[0,50000]`。
- 输入保证为完全二叉树。
- 原题要求时间复杂度优于逐个访问所有节点的 `O(n)`。

### 示例

```text
输入：root = [1,2,3,4,5,6]
输出：6
```

示例层序数组包含六个真实节点，因此返回 6。

[官方原题与完整题面](https://leetcode.com/problems/count-complete-tree-nodes/description/)。

## 解题思路与参考答案

## 题意

给一棵完全二叉树，返回节点个数。完全二叉树指除最后一层外全满，最后一层的节点都靠左。

## 思路

普通 DFS 计数 $O(n)$ 也能过，但这题要利用完全性。我会沿左孩子一路量出左高、沿右孩子一路量出右高，这里的高按节点个数算。两个高度相等，说明是满树，直接返回 $2^h-1$。不相等，就是根加一，再递归左右；左右子树里必有一侧是满的，那一侧一次量高就收掉，递归很快结束。

拿示例走一遍：根 $1$，第二层 $2$、$3$，第三层是 $4$、$5$、$6$。从根往左量高是 $3$，往右量是 $2$，不相等，于是递归。左子树 $2$ 带着 $4$、$5$，左右高都是 $2$，直接得 $3$；右子树 $3$ 只有左孩子 $6$，左高 $2$、右高 $1$，再递归一层得 $2$。加上根，$1+3+2=6$。

也可以对最后一层编号二分，看某个位置的路径是否存在，时间同样 $O(h^2)$，写法放在追问里。

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


def countNodes(root: Optional[TreeNode]) -> int:
    def height(node: Optional[TreeNode], go_left: bool) -> int:
        h = 0
        while node:
            h += 1
            node = node.left if go_left else node.right
        return h

    if root is None:
        return 0
    lh, rh = height(root, True), height(root, False)
    if lh == rh:
        return (1 << lh) - 1
    return 1 + countNodes(root.left) + countNodes(root.right)


if __name__ == "__main__":
    root = TreeNode(
        1,
        TreeNode(2, TreeNode(4), TreeNode(5)),
        TreeNode(3, TreeNode(6)),
    )
    assert countNodes(root) == 6
    assert countNodes(None) == 0
    assert countNodes(TreeNode(1)) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(
    1,
    TreeNode(2, TreeNode(4), TreeNode(5)),
    TreeNode(3, TreeNode(6)),
)
assert countNodes(root) == 6
assert countNodes(None) == 0
assert countNodes(TreeNode(1)) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每层量高 $O(h)$，递归深度 $O(h)$，总共 $O(h^2)$；整棵是满树时，一次量高就结束。额外空间 $O(h)$。

## Edge Cases

空树返回 $0$。$n=1$ 时满树公式给出 $2^1-1=1$。最后一层刚好满时，左右高相等，一次公式结束。最后一层只有最左一个节点时，左右高差 $1$，递归下去左边是满的，右边几乎为空。

## 追问

**如果是普通二叉树，不保证完全呢？**
满树公式就失效了，只能 $O(n)$ 遍历：`1 + count(left) + count(right)`。完全性保证了缺口只出现在最后一层靠右，才能用左右高相等来判定满树。

**对最后一层二分怎么写？**
先沿左孩子量出高度 $h$，这里按边数算。上面几层是满的，共 $2^h-1$ 个节点，最后一层的下标范围是 $[0, 2^h-1]$。`exists(idx)` 从根往下走 $h$ 步，每步把区间对半，`idx` 落在左半就走左，否则走右。对下标二分，找到第一个不存在的位置，存在的个数加上上层节点数就是答案。每次判定 $O(h)$，二分 $O(h)$ 次，总共仍是 $O(h^2)$。

```python
def countNodes(root):
    if root is None:
        return 0
    h, node = 0, root
    while node.left:
        h += 1
        node = node.left

    def exists(idx):
        left, right, cur = 0, (1 << h) - 1, root
        for _ in range(h):
            mid = (left + right) // 2
            if idx <= mid:
                cur = cur.left
                right = mid
            else:
                cur = cur.right
                left = mid + 1
        return cur is not None

    lo, hi = 0, (1 << h) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if exists(mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return ((1 << h) - 1) + lo
```
