---
id: lc-103-binary-tree-zigzag-level-order-traversal
section: binary-tree-bfs
order: 4
level: A
title: LC 103 · 二叉树的锯齿形层序遍历
quick: "先按普通 BFS 切层收集，根层从左到右，下一层反转，之后交替。入队顺序一直是先左后右；也可以用双端队列决定每层头插还是尾插。时间 $O(n)$，额外空间 $O(w)$。"
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 103. 二叉树的锯齿形层序遍历
    url: https://leetcode.cn/problems/binary-tree-zigzag-level-order-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一棵二叉树，按层返回节点值，但相邻两层的读取方向交替。根所在第 0 层从左到右，第 1 层从右到左，第 2 层再从左到右，依此类推。

### 输入与输出

实现 `zigzagLevelOrder(root: Optional[TreeNode]) -> List[List[int]]`。外层列表按从浅到深排列，内层列表按该层要求的方向排列；空树返回 `[]`。示例的树使用层序列表表示，`null` 代表缺失的子节点，实际接口接收节点对象。

### 约束

- 节点数为 0 到 2000。
- `-100 <= Node.val <= 100`。

### 示例

```text
输入：root = [3,9,20,null,null,15,7]
输出：[[3],[20,9],[15,7]]
```

第二层原本从左到右是 `[9,20]`，该层要求反向，因此输出 `[20,9]`。

## 解题思路与参考答案

## 题意

层序遍历，但方向交替：第 $0$ 层从左到右，第 $1$ 层从右到左，再交替。

## 思路

我会先按 LC 102 的写法切层，收完一层再决定要不要 `reverse`。入队顺序始终是左孩子再右孩子，不在队列里来回改方向。要反转的是从 $1$ 数的偶数层，根算第 $1$ 层、从左到右。

拿 `[3,9,20,null,null,15,7]` 看。第一层 `[3]` 不动；第二层按入队顺序收到 `[9,20]`，反转成 `[20,9]`；第三层 `[15,7]` 不动。

也可以用双端队列，奇数层尾插、偶数层头插，这样就不用事后反转。

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


def zigzagLevelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []
    q = deque([root])
    ans: List[List[int]] = []
    while q:
        level: List[int] = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        if len(ans) % 2 == 1:
            level.reverse()
        ans.append(level)
    return ans


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert zigzagLevelOrder(root) == [[3], [20, 9], [15, 7]]
    assert zigzagLevelOrder(TreeNode(1)) == [[1]]
    assert zigzagLevelOrder(None) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
assert zigzagLevelOrder(root) == [[3], [20, 9], [15, 7]]
assert zigzagLevelOrder(TreeNode(1)) == [[1]]
assert zigzagLevelOrder(None) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，反转一层也是线性的。额外空间 $O(w)$。

## 边界

空树返回 `[]`。只有一层时不用反转。该反转的那一层只有一个节点时，反不反转都一样。

## 追问

**层号从 $1$ 计还是从 $0$ 计？**
先和面试官对齐再写。题面里第 $0$ 层（根）从左到右，第 $1$ 层从右到左。口头说「奇数层左到右」或「偶数层反转」，用的就是从 $1$ 计。代码里用 `len(ans)` 的奇偶最稳，已经有奇数层时当前这层要反，别和入队顺序搞反。

**能不能层内双端插入、不事后 `reverse`？**
可以。队列照样先左孩子再右孩子，只是当前层用一个 `deque` 收值，从左到右就 `append`，从右到左就 `appendleft`。指针版的「之字」打印也是这个道理，先切层，再决定头插还是尾插。时间仍是 $O(n)$。

```python
from collections import deque

def zigzagLevelOrder(root):
    if root is None:
        return []
    q, ans, l2r = deque([root]), [], True
    while q:
        level = deque()
        for _ in range(len(q)):
            node = q.popleft()
            if l2r:
                level.append(node.val)
            else:
                level.appendleft(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(list(level))
        l2r = not l2r
    return ans
```
