---
id: lc-104-maximum-depth-of-binary-tree
section: binary-tree-dfs
order: 1
level: S
title: LC 104 · 二叉树的最大深度
quick: >-
  空树深度 $0$，否则是 $1+\max(\text{左深},\text{右深})$，用 DFS 或层序都行。时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 104. Maximum Depth of Binary Tree
    url: https://leetcode.com/problems/maximum-depth-of-binary-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定二叉树的根节点，返回这棵树的最大深度。深度按节点数计：从根到最远叶节点的路径包含多少个节点，最大深度就是多少；只有根时深度为 1，空树深度为 0。

### 输入与输出

实现 `maxDepth(root: Optional[TreeNode]) -> int`。示例用层序列表描述树，null 表示相应子节点不存在，实际传入根节点对象。

### 约束

- 节点数为 0 到 `10^4`。
- 节点值在 `[-100,100]`。

### 示例

```text
输入：root = [3,9,20,null,null,15,7]
输出：3
```

示例最长路径可以是 `3 -> 20 -> 15`，经过 3 个节点，因此深度为 3。

## 解题思路与参考答案

## 题意

给定二叉树根节点，返回最大深度：根到最远叶的节点个数。空树为 $0$。

## 思路

我会用后序 DFS，一个节点的深度只取决于左右子树的深度。先求左右子树深度，当前深度是 $1$ 加上较大者；空节点返回 $0$，叶节点自然得到 $1$。

拿 `[3, 9, 20, None, None, 15, 7]` 走一遍：9、15、7 都是叶子，深度 1；20 是 $1+\max(1,1)=2$；根 3 是 $1+\max(1,2)=3$。

层序 BFS 数层数也能做。我会先写递归，再补一句递归栈最坏是 $O(n)$。

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


def maxDepth(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))


if __name__ == "__main__":
    assert maxDepth(build_tree([3, 9, 20, None, None, 15, 7])) == 3
    assert maxDepth(build_tree([1, None, 2])) == 2
    assert maxDepth(build_tree([])) == 0
    assert maxDepth(build_tree([1])) == 1
    assert maxDepth(build_tree([1, 2, None, 3, None, 4])) == 4
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert maxDepth(build_tree([3, 9, 20, None, None, 15, 7])) == 3
assert maxDepth(build_tree([1, None, 2])) == 2
assert maxDepth(build_tree([])) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个节点一次。额外空间 $O(h)$，$h$ 是树高，最坏链状 $O(n)$。

## 边界

- 空树深度为 $0$。
- $n=1$ 时只有根，深度为 $1$。
- 只有左链或只有右链时，深度等于节点数。

## 追问

**改成最小深度（LC 111）呢？**
不能把 $\max$ 直接换成 $\min$。空孩子返回 $0$，单侧树 `min(左, 0)+1` 会得到 $1$，把缺失的那边当成了叶子。最小深度是根到最近叶子的节点数：只有一侧孩子时必须走进那一侧，两侧都有才取较小。用 BFS 的话，第一次碰到叶子就是答案，偏斜树往往比 DFS 早停。

```python
from collections import deque

def minDepth(root):
    if root is None:
        return 0
    q = deque([(root, 1)])
    while q:
        node, d = q.popleft()
        if node.left is None and node.right is None:
            return d
        if node.left:
            q.append((node.left, d + 1))
        if node.right:
            q.append((node.right, d + 1))
```

**迭代求最大深度怎么写？**
DFS 用栈存 `(node, depth)`，弹出时用当前深度更新答案，左右孩子以 `depth+1` 入栈。也可以 BFS 按层切，每过一层 `ans += 1`，队列掏空就是最大深度。时间都是 $O(n)$；BFS 额外空间 $O(w)$，链状时栈或递归是 $O(n)$。

```python
def maxDepthIter(root):
    ans = 0
    stack = [(root, 1)] if root else []
    while stack:
        node, d = stack.pop()
        ans = max(ans, d)
        if node.left:
            stack.append((node.left, d + 1))
        if node.right:
            stack.append((node.right, d + 1))
    return ans
```
