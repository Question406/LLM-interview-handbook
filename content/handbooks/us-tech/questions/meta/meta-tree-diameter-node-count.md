---
id: meta-tree-diameter-node-count
section: meta
order: 900
level: A
title: "Meta：Tree diameter 改成按 nodes 计数"
quick: "这道变体最容易错在计数单位。若空子树 height=0、叶子 height=1，经过当前节点的路径就是 left height + right height + 1。"
companies:
  - meta
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "候选人自述：Meta ML Research Scientist loop"
    url: "https://www.reddit.com/r/leetcode/comments/1r37w7q/meta_ml_research_scientist_interview_experience/"
    type: interview
---

## 题目描述

来源：ML Research Scientist 候选人自述，standard coding 第一题是 LC 543 的 node-count 变体。下面使用数组形式表达 binary tree，数据表示由手册设定。

### 输入、接口与规则

实现 `diameter_nodes(children, root=0) -> int`。children 是长度 N 的数组；`children[i]=(left,right)`，child 为节点下标或 None。N=0 表示空树，返回 0；非空时输入是一棵合法 binary tree，root 是根，所有节点都从 root 可达，无环且不共享 child。

返回任意两个节点间最长 simple path 上的节点数。路径可经过某个内部节点，而不必经过 root；单节点结果为 1。节点数 N 可到 100000，应避免依赖 Python recursion limit；不修改 children。请说明本题与按 edges 计数时的差别，并给出时间和额外空间复杂度。

### 输入输出示例

```text
children=[(1,2),(3,None),(None,None),(None,None)], root=0
最长路径 3→1→0→2，返回 4，而不是 3。空树返回 0。
```

## 回答思路

> **输入与任务：** 确认答案计算 nodes，单节点为 1。  
> **做法与原因：** Postorder 计算每个子树的 node-height，再比较 left+right+1。  
> **正确性检查：** 检查空树、链状树和最长路径不经过 root 的情况。

## 解题思路与参考答案

这道变体最容易错在计数单位。若空子树 height=0、叶子 height=1，经过当前节点的路径就是 left height + right height + 1。

我会用一次遍历记录顺序，再反向计算 heights，这样长链也不会因为递归过深失败。最终答案取所有节点上的最大值。

### 完整参考实现

```python
def diameter_nodes(children, root=0):
    if not children:
        return 0
    order, stack = [], [root]
    while stack:
        node = stack.pop()
        order.append(node)
        stack.extend(child for child in children[node] if child is not None)
    heights, answer = {}, 0
    for node in reversed(order):
        left, right = children[node]
        lh, rh = heights.get(left, 0), heights.get(right, 0)
        heights[node] = 1 + max(lh, rh)
        answer = max(answer, lh + rh + 1)
    return answer
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
assert diameter_nodes([]) == 0
assert diameter_nodes([(None, None)]) == 1
assert diameter_nodes([(1, 2), (3, None), (None, None), (None, None)]) == 4
inside = [
    (1, None),
    (2, 3),
    (4, None),
    (5, None),
    (6, None),
    (None, None),
    (None, None),
]
assert diameter_nodes(inside) == 6  # Longest path does not pass through root 0.
chain = [(i + 1, None) for i in range(3999)] + [(None, None)]
assert diameter_nodes(chain) == 4000
print("Meta node-count diameter: passed")
```

## 复杂度与追问

时间 `O(N)`，额外空间 `O(N)`。若使用递归，辅助 stack 与树高有关，但 Python 中长链可能触发 RecursionError。Tree diameter 按 edges 计数时，非空树的结果比本题少 1。
