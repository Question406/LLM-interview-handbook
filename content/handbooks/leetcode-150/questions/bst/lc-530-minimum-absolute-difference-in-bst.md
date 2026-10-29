---
id: lc-530-minimum-absolute-difference-in-bst
section: bst
order: 1
level: A
title: LC 530 · 二叉搜索树的最小绝对差
quick: BST 中序是递增序列，最小差一定出现在中序相邻的两个值之间，所以中序扫一遍、维护前驱就够了。时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - BST
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 530. 二叉搜索树的最小绝对差
    url: 'https://leetcode.cn/problems/minimum-absolute-difference-in-bst/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一棵二叉搜索树，在任意两个不同节点之间，找出节点值之差的绝对值能够取得的最小值。两个节点不必直接相连，也不要求一个是另一个的祖先。

### 输入与输出

实现 `getMinimumDifference(root: Optional[TreeNode]) -> int`。返回差值本身；输入保证至少有两个节点。示例用层序列表表示树，实际接口接收根节点对象。

### 约束

- 节点数为 2 到 `10^4`。
- 节点值在 0 到 `10^5`，整棵树满足二叉搜索树的顺序约束。

### 示例

```text
输入：root = [4,2,6,1,3]
输出：1
```

示例中节点值 1 与 2 的差为 1，已经达到所有节点对的最小差值。

## 解题思路与参考答案

## 题意

给一棵至少有两个节点的二叉搜索树，返回任意两个节点值之差的绝对值的最小值。

## 思路

我会用中序遍历加前驱，因为有序数组里的最小差一定出现在相邻两个数之间，而 BST 的中序正好有序，所以不用枚举所有点对。维护上一个访问的值 `prev`，每到一个节点就做 `min(ans, node.val - prev)`。值非负、中序又是递增的，减法不用再取绝对值。LC 783 是同一题。

拿示例 `[4, 2, 6, 1, 3]` 走一遍：中序是 $1, 2, 3, 4, 6$，相邻差依次是 $1, 1, 1, 2$，答案是 $1$。

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


def getMinimumDifference(root: Optional[TreeNode]) -> int:
    prev: Optional[int] = None
    ans = 10**18

    def dfs(node: Optional[TreeNode]) -> None:
        nonlocal prev, ans
        if node is None:
            return
        dfs(node.left)
        if prev is not None:
            ans = min(ans, node.val - prev)
        prev = node.val
        dfs(node.right)

    dfs(root)
    return ans


if __name__ == "__main__":
    root = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6))
    assert getMinimumDifference(root) == 1
    root2 = TreeNode(1, None, TreeNode(3, TreeNode(2)))
    assert getMinimumDifference(root2) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6))
assert getMinimumDifference(root) == 1
root2 = TreeNode(1, None, TreeNode(3, TreeNode(2)))
assert getMinimumDifference(root2) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(h)$；用 Morris 中序可以做到 $O(1)$。

## Edge Cases

只有两个节点时，答案就是二者之差。父子之间差很大、跨层的两个节点差更小时，中序相邻照样能抓到，比如 $1$ 与 $3$ 分居根的两侧。树退化成链时，中序就是这条链的递增序，扫相邻即可。

## 追问

**如果是普通二叉树，不是 BST 呢？**
中序不再有序，最小差可能出现在中序里不相邻的位置。可以收集全部值排序后扫相邻，时间 $O(n\log n)$；值域不大时也可以用桶。只比父子边是不够的，最优的一对可以隔代。

```python
def getMinimumDifference(root):
    vals = []

    def dfs(node):
        if node is None:
            return
        vals.append(node.val)
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    vals.sort()
    return min(vals[i] - vals[i - 1] for i in range(1, len(vals)))
```

**要求第 $k$ 小的相邻差呢？**
先中序得到有序数组 $a$，把相邻差 $a[i]-a[i-1]$ 放进列表排序，取第 $k$ 个，时间 $O(n\log n)$。如果问的是任意两点差的第 $k$ 小，那是另一道题，要对差二分再用双指针数对，不再只看中序相邻。
