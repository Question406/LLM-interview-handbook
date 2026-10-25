---
id: lc-105-construct-binary-tree-from-preorder-and-inorder-traversal
section: binary-tree
order: 5
level: S
title: LC 105 · 从前序与中序遍历序列构造二叉树
quick: "前序第一个 `pre[0]` 是根，拿它在中序里切开左右子树，再按左子树长度切前序，递归下去。中序下标先存进哈希，免得每次扫描找根。时间 $O(n)$，额外空间 $O(n)$。"
tags:
  - Tree
  - Hash Table
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 105. 从前序与中序遍历序列构造二叉树
    url: https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定同一棵二叉树的前序遍历序列 preorder 和中序遍历序列 inorder，重建并返回这棵树。前序按根、左子树、右子树的次序访问，中序按左子树、根、右子树的次序访问。

### 输入与输出

实现 `buildTree(preorder, inorder) -> TreeNode`，返回重建树的根节点。示例输出用层序数组展示结构，null 代表空孩子；实际返回节点结构而不是这个数组。

### 约束与约定

- 两个数组长度相同，长度在 1 到 3000 之间。
- 节点值在 `[-3000,3000]`，每个序列内的值都不重复，两个序列包含相同值。
- 保证这两个序列分别是某棵二叉树的合法前序与中序遍历。

### 示例

```text
输入：preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
输出：[3,9,20,null,null,15,7]
```

示例树以 3 为根，左孩子为 9，右子树以 20 为根且有孩子 15、7。

[官方原题与完整题面](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/description/)。

## 解题思路与参考答案

## 题意

给出一棵树的前序遍历和中序遍历，节点值互不相同，要求还原这棵二叉树。

## 思路

我会用递归加哈希，因为前序告诉我谁是根，中序告诉我左右子树各有多少个节点，两边合起来就能一层层切下去。前序第一个是根；中序里根左边是左子树，右边是右子树。左子树如果有 $k$ 个节点，前序里根后面紧跟的 $k$ 个就是左子树，再往后是右子树。

用示例走一遍：前序 `[3, 9, 20, 15, 7]`，中序 `[9, 3, 15, 20, 7]`。根是 $3$，它在中序里左边只有 $9$，所以左子树大小是 $1$；前序里 $3$ 后面的 $9$ 就是左子树，剩下的 `[20, 15, 7]` 是右子树。右边同样处理：根是 $20$，中序里它左边是 $15$、右边是 $7$。

找根在中序里的位置时，我会先把中序下标存进哈希，每次 $O(1)$ 定位，不用每层都扫一遍中序。

## 参考代码

```python
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional


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


def buildTree(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    idx: Dict[int, int] = {v: i for i, v in enumerate(inorder)}

    def build(pre_l: int, pre_r: int, in_l: int, in_r: int) -> Optional[TreeNode]:
        if pre_l > pre_r:
            return None
        root_val = preorder[pre_l]
        root = TreeNode(root_val)
        mid = idx[root_val]
        left_size = mid - in_l
        root.left = build(pre_l + 1, pre_l + left_size, in_l, mid - 1)
        root.right = build(pre_l + left_size + 1, pre_r, mid + 1, in_r)
        return root

    n = len(preorder)
    return build(0, n - 1, 0, n - 1)


def to_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    if root is None:
        return []
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


if __name__ == "__main__":
    root = buildTree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    assert to_list(root) == [3, 9, 20, None, None, 15, 7]
    assert to_list(buildTree([-1], [-1])) == [-1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = buildTree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
assert to_list(root) == [3, 9, 20, None, None, 15, 7]
assert to_list(buildTree([-1], [-1])) == [-1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每个节点只建一次，时间 $O(n)$。哈希占 $O(n)$，递归栈 $O(h)$。

## 边界

单节点时前序和中序都是同一个值。全是左链的树，根在中序里排在最右，前序里除根以外都属于左子树。全是右链的树，根在中序最左，左段长度为 $0$。

## 追问

**节点值有重复怎么办？**
那单靠前序加中序就不能唯一确定这棵树。中序里同一个值可能对应多个下标，根从哪里切有歧义。本题保证值互异，才能预处理 `val -> index`。如果允许重复，还要额外的约束，例如给出父指针或唯一编号。

**换成后序加中序（LC 106）呢？**
思路对称，后序最后一个才是根，中序照样切左右。右子树大小 $k=\text{in}_r-\text{mid}$，后序里 `[post_r-k, post_r-1]` 是右子树，更前面是左子树。前序的根在头，先建左；后序的根在尾，先算右段长度。独立卡见 `lc-106-construct-binary-tree-from-inorder-and-postorder-traversal`。

```python
def buildTree(inorder, postorder):
    idx = {v: i for i, v in enumerate(inorder)}

    def build(in_l, in_r, post_l, post_r):
        if post_l > post_r:
            return None
        root = TreeNode(postorder[post_r])
        mid = idx[root.val]
        k = in_r - mid
        root.left = build(in_l, mid - 1, post_l, post_r - k - 1)
        root.right = build(mid + 1, in_r, post_r - k, post_r - 1)
        return root

    n = len(inorder)
    return build(0, n - 1, 0, n - 1)
```
