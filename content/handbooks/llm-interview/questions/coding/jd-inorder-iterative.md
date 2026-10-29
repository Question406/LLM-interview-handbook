---
id: jd-inorder-iterative
section: coding
order: 191
level: B
title: 京东零售二面：二叉树中序遍历如何非递归写？
quick: 用栈：一路向左压栈，弹出时访问，再转到右子树。题目要非递归，递归版不算数。edge-case tests 覆盖空树、只有左链、只有右链。
tags:
  - JD
  - Coding
  - Tree
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 京东零售平台产品与研发中心二面
    url: 'https://www.nowcoder.com/feed/main/detail/6a94272eee68460d9e8f90c72ddb8dab'
    type: candidate-first-hand
---

## 题目描述

给定一棵二叉树的根节点 `root`，实现 `inorder(root)`，**不使用递归**，返回按“左子树、节点自身、右子树”顺序访问得到的节点值列表。

候选人记录明确要求非递归中序遍历；以下对象接口为手册重构练习约定：节点提供 `val`、`left`、`right` 属性，空孩子和空树用 `None` 表示。节点值可为整数，树中允许重复值；输入为有限、无环的二叉树，不要求是二叉搜索树。不得修改树的连接关系。

### 接口、输入与输出要求

### 示例

```text
输入：root 的值为2，左孩子为1，右孩子为3
输出：[1,2,3]

输入：root=None
输出：[]

输入：根为1，1只有右孩子2，2只有左孩子3
输出：[1,3,2]
```

## 解题思路与参考答案

非递归中序用一个栈加一个指针：`cur` 不空就一路向左压栈，走到头就弹出一个节点访问，再把 `cur` 转到它的右子树，循环到栈空、`cur` 也空为止。

这是京东零售平台产品与研发中心的二面题，来自牛客候选人原帖，可信度 B，原话是**“手撕：二叉树的中序遍历（非递归方式），在本地 txt 文件里写”**。原帖要求在本地 txt 里手写，edge cases 需要自行测试：空树、单节点、只有左链、只有右链。常见翻车是交了递归版，或者写成「先访问再压左」，那其实是前序。中序是左-根-右，所以要先把左链压完，弹出时才访问。BST 的中序是有序的，可以拿来验证结果。

## 栈模拟：左链压完再访问根

维护 `cur` 和 `stack`。循环条件写 `stack or cur`，因为右子树还没走完时，栈可能已经空了，但 `cur` 不空。

```python
def inorder(root):
    stack, cur, out = [], root, []
    while stack or cur:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out
```

用几个 edge cases 手动检查：只有左链时，全部压栈后依次弹出，对；只有右链时，栈里每次只有一个节点，访问完走向右孩子，对；空树不进循环，返回 `[]`。别在内层 `while cur` 里访问，那样根就跑到左子树前面去了。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

构造根为 2、左右孩子为 1 和 3 的树，预期中序是 [1,2,3]；再测空树和只有右孩子的树，检查栈和游标的退出条件。

```python
from types import SimpleNamespace


def node(value, left=None, right=None):
    return SimpleNamespace(val=value, left=left, right=right)


assert inorder(node(2, node(1), node(3))) == [1, 2, 3]
assert inorder(None) == []
assert inorder(node(1, right=node(2))) == [1, 2]
print("simple tests passed")
```

## 复杂度与 Morris

时间 $O(n)$，额外空间最坏 $O(n)$（左斜树），平均 $O(h)$。Morris 遍历用空的右指针穿线索，额外空间 $O(1)$，但必须把指针还原，现场容易写坏，京东这题用栈更稳，Morris 口头讲讲就行。中序的输出常用在 BST 有序检查和表达式树上，表达式树的中序就是中缀表达式，面试时补一句应用会更完整。BST 校验时中序应该严格递增，允许重复的话是非递减。

## 追问

**为什么不能递归？**
题面写明了非递归；而且左链很深时会爆 Python 默认的递归深度。栈其实就是把调用栈显式写出来。

**和前序差在哪一行？**
差在访问时机：前序在压栈前 `visit`，中序在弹出后 `visit`。讲模板时要把访问时机说出来。

**右孩子要入栈吗？**
不直接压。`cur = cur.right` 之后，下一轮把它当新根继续走左链。

**Morris 要不要写？**
能讲清线索化和还原就行，指针写错会把树改坏，默认交栈版。

**前序、后序的非递归怎么写？**
前序是访问了再入栈、往左走；后序可以用双栈，或者记住上次弹出的节点，避免把右子树访问两次。
