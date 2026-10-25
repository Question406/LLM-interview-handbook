---
id: lc-173-binary-search-tree-iterator
section: binary-tree
order: 12
level: A
title: LC 173 · 二叉搜索树迭代器
quick: "实现 `BSTIterator` 时用栈做一个可以暂停的中序遍历：初始化把根的左链压栈，`next` 弹出栈顶，再把它右孩子的左链压进去。每个节点只进出栈一次，`next` / `hasNext` 均摊 $O(1)$，空间 $O(h)$。"
tags:
  - Tree
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 173. 二叉搜索树迭代器
    url: https://leetcode.cn/problems/binary-search-tree-iterator/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

实现二叉搜索树的迭代器，使调用者能够按节点值非递减的顺序逐个读取整棵树。初始化时迭代位置在最小值之前，每次 next 调用前进一步，不能一次 next 返回整个剩余序列。

### 接口与输出

实现 `BSTIterator(root)`、`next() -> int` 和 `hasNext() -> bool`。next 返回尚未读取的最小值；hasNext 只判断是否还有值，不消耗元素。调用者只在 hasNext 为 True 时调用 next。目标是 next/hasNext 平均 `O(1)` 时间、`O(h)` 额外空间，h 为树高。

### 合法输入与约束

树是有效 BST，节点数为 1 到 100000，节点值为 0 到 1000000；next 与 hasNext 合计调用不超过 100000 次。示例操作序列的第一项是构造器，输出中的首个 `null` 表示构造操作无返回值。

### 示例

```text
输入：["BSTIterator", "next", "next", "hasNext", "next", "hasNext", "next", "hasNext", "next", "hasNext"]
[[[7, 3, 15, null, null, 9, 20]], [], [], [], [], [], [], [], [], []]
输出：[null, 3, 7, true, 9, true, 15, true, 20, false]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/binary-search-tree-iterator/description/)。

## 解题思路与参考答案

## 题意

给 BST 实现一个迭代器：`next()` 返回中序的下一个元素，也就是剩下的最小值；`hasNext()` 判断还有没有。初始化时不要一次性遍历整棵树。

## 思路

我会用栈手动模拟中序遍历，因为这样遍历可以停在任意位置，调用一次 `next` 才往前走一步。栈里放的是中序里还没返回的节点，沿左链入栈之后，栈顶就是下一个最小值。构造时从根一路向左压栈。`next` 弹出栈顶作为当前最小值，如果它有右孩子，就把右孩子和它的左链压进去。`hasNext` 只看栈是否非空。

拿示例走一遍：根 $7$，左孩子 $3$，右孩子 $15$（下面挂 $9$、$20$）。构造后栈里是 $7$、$3$。第一次 `next` 弹出 $3$，它没有右孩子；第二次弹出 $7$，把 $15$ 和它的左链 $9$ 压进去；接下来依次吐出 $9$、$15$、$20$。

一次性把中序结果放进数组也正确，但空间是 $O(n)$，也做不到需要下一个元素时才继续遍历。均摊分析很直接：每个节点入栈、出栈各一次。

## 参考代码

```python
from __future__ import annotations

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


class BSTIterator:
    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        self._push_left(root)

    def _push_left(self, node: Optional[TreeNode]) -> None:
        while node:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

    def hasNext(self) -> bool:
        return bool(self.stack)


if __name__ == "__main__":
    root = TreeNode(7, TreeNode(3), TreeNode(15, TreeNode(9), TreeNode(20)))
    it = BSTIterator(root)
    assert it.hasNext()
    assert [it.next() for _ in range(5)] == [3, 7, 9, 15, 20]
    assert not it.hasNext()
    empty = BSTIterator(None)
    assert not empty.hasNext()
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
root = TreeNode(7, TreeNode(3), TreeNode(15, TreeNode(9), TreeNode(20)))
it = BSTIterator(root)
assert it.hasNext()
assert [it.next() for _ in range(5)] == [3, 7, 9, 15, 20]
assert not it.hasNext()
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`next` / `hasNext` 均摊 $O(1)$，单次 `next` 最坏 $O(h)$。空间 $O(h)$。

## 边界

空树时 `hasNext` 为假，这时不要调 `next`。只有左链的树，构造时栈先涨到 $h$，之后每次 `next` 几乎都是 $O(1)$。只有右链的树，栈里几乎总是只有 $1$ 个节点。

## 追问

**调了 `hasNext` 却不调 `next`，会出问题吗？**
不会。栈状态不变，可以反复问，必须一直返回同一个布尔值。`hasNext` 只读 `len(stack)`，不要在里面 `pop`，实现时把「找下一个」全部放进 `next`。

**要反向迭代，从大到小，或者求第 $k$ 大呢？**
把中序反过来：构造时沿右链压栈，`next` 弹出当前最大值，再把它的左孩子及其右链压进去。均摊仍是 $O(1)$，空间 $O(h)$。第 $k$ 大就是反向迭代 $k$ 次。

```python
class BSTIteratorReverse:
    def __init__(self, root):
        self.stack = []
        self._push_right(root)

    def _push_right(self, node):
        while node:
            self.stack.append(node)
            node = node.right

    def next(self):
        node = self.stack.pop()
        self._push_right(node.left)
        return node.val

    def hasNext(self):
        return bool(self.stack)
```
