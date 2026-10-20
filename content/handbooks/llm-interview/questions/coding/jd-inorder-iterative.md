---
id: jd-inorder-iterative
section: coding
order: 191
level: B
title: 京东零售二面：二叉树中序遍历如何非递归写？
quick: >-
  用栈：一路向左压栈，弹出访问，再转入右子树。不要递归版充数。边界是空树、只有左链或只有右链。
tags:
  - JD
  - Coding
  - Tree
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 京东零售平台产品与研发中心二面
    url: https://www.nowcoder.com/feed/main/detail/6a94272eee68460d9e8f90c72ddb8dab
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：零售平台产品与研发中心
- 届别 / 流程：二面
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“手撕：二叉树的中序遍历（非递归方式），在本地txt文件里写”**

常见误区是：交递归版，或把「先访问再压左」写成前序。中序是左-根-右：必须先沿左链压栈，弹出才访问，再把指针转到右子树。原帖要求本地 txt 手写，边界要自己测：空树、单节点、只有左链、只有右链。BST 上中序即有序，可用来验证。
## 栈模拟：左链压完再访根

维护 `cur` 与 `stack`。`cur` 非空就一路向左压；否则弹出访问，`cur = cur.right`。循环条件是 `stack or cur`：右子树还没走完时栈可空但 `cur` 非空。

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

只有左链：全部压栈后依次弹出，对。只有右链：每次栈里一个节点，访完走向右孩子，对。空树：循环不进，返回 `[]`。不要在内层 `while cur` 里访问，那会变成根在左前。

## 复杂度与 Morris（口头即可）

时间 $O(n)$，额外空间最坏 $O(n)$（左斜树），平均 $O(h)$。Morris 用空右指针穿线索，额外 $O(1)$，但必须还原指针，现场容易写坏；京东这题栈写法更稳。若追问前序/后序：前序是访了再入栈走左；后序可用双栈或「记上次弹出」避免把右子树访两次。BST 校验：中序应严格递增（或非递减，看是否允许重复）。

## 追问

- **为什么不能递归？** 题面写明非递归；深层左链还会爆 Python 默认递归深度。栈就是显式调用栈。
- **和前序差在哪一行？** 前序在压栈前 `visit`；中序在弹出后 `visit`。不要背模板不说访问时机。
- **右子树入栈吗？** 不直接把右孩子压进去，而是 `cur = cur.right` 后下一轮当新根走左链。
- **Morris 要不要写？** 能讲清线索化与还原即可；写错指针会改树。默认交栈版。
- **输出用来干什么？** BST 有序检查、表达式树（中序是中缀）。面试补一句应用，比只写循环更完整。
