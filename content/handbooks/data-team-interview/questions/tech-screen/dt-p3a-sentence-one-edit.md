---
id: dt-p3a-sentence-one-edit
section: tech-screen
order: 71
level: A
title: Apple Siri MLE 原帖：判断两句话是否恰好相差一次编辑
quick: >-
  先确认编辑单位以及要求恰好一次还是至多一次。恰好一次时，相同输入应返回
  False；长度差不超过一，用双指针只允许一次替换或跳过较长串的一个字符，避免完整编辑距离 DP。
companies:
  - apple
tags:
  - Apple
  - 一亩三分地原帖核对
  - AFM 专项 2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: Apple MLE Onsite，候选人原帖，Chrome 核对2026-10-26
    url: 'https://www.1point3acres.com/bbs/thread-1170085-1-1.html'
    type: interview
---

## 题目描述

### 原帖核对与练习约定

- 原帖：[Apple MLE Onsite](https://www.1point3acres.com/bbs/thread-1170085-1-1.html)。发帖时间为页面显示的 2026-03-24 20:41:21；作者后续回复说明面试团队为 Siri response generation。岗位信息按原帖记录。
- 采集日期：2026-10-26。Chrome 中可见主楼及作者回复，没有依赖搜索摘要补题。
- 原帖披露：编程题判断两句话是否只差一次编辑，返回布尔值；作者指出不需要完整编辑距离动态规划。原帖未定义字符或词级编辑、相等输入和大小写规则。
- **本题练习约定**：按 Python 字符串字符位置编辑，恰好一次，大小写敏感；函数接口、约束与测试均为手册补充。

### 输入与接口

实现 `one_edit_sentence(a: str, b: str) -> bool`。a、b 为任意 Unicode 字符串，可为空，长度各不超过 100000。一次编辑是插入、删除或替换一个 Python 字符；空格和标点也算字符。不做 Unicode 规范化、分词或大小写转换。

### 输出与约束

返回是否可用恰好一次编辑把 a 变成 b。相同字符串返回 False；相邻字符交换不是单次操作。不修改输入。期望时间为 $O(|a|+|b|)$，额外空间为 $O(1)$。

### 示例

```text
one_edit_sentence('book a room', 'book room') -> False
one_edit_sentence('book room', 'book rooms') -> True
one_edit_sentence('cat', 'cut') -> True
one_edit_sentence('same', 'same') -> False
```

## 解题思路与参考答案

长度差大于一直接失败。使 a 不长于 b；双指针遇到相等字符一起前进。首次不相等时，长度相等就替换一个字符，即两个指针都前进；长度不同就只跳过 b 的一个字符。第二次不相等直接失败。循环结束后，较长串剩下的唯一尾字符也算一次编辑。

```python
def one_edit_sentence(a, b):
    if len(a) > len(b):
        a, b = b, a
    if len(b) - len(a) > 1:
        return False
    i = j = 0
    edited = False
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        if edited:
            return False
        edited = True
        if len(a) == len(b):
            i += 1
        j += 1
    if j < len(b):
        if edited:
            return False
        edited = True
    return edited
```

长度差最多一，循环只允许一次结构偏移，所以尾部不可能再剩多个合法待处理字符。无需保存 DP 表，也没有 evaluation slices 复制。

## 简单测试怎么写

把实现与测试依次保存成 `solution.py`，运行 `python3 solution.py`，不需要第三方库。先检查替换和尾部插入，再检查恰好一次、两处差异、空串和中文。

```python
assert one_edit_sentence('cat', 'cut') is True
assert one_edit_sentence('book room', 'book rooms') is True
assert one_edit_sentence('book rooms', 'book room') is True
assert one_edit_sentence('book a room', 'book room') is False
assert one_edit_sentence('same', 'same') is False
assert one_edit_sentence('', '') is False
assert one_edit_sentence('', 'a') is True
assert one_edit_sentence('ab', 'ba') is False
assert one_edit_sentence('abc', 'axcd') is False
assert one_edit_sentence('明天见', '明天再见') is True
assert one_edit_sentence('a b', 'ab') is True
```

## 面试追问

**如果按词编辑呢？** 先明确分词规则和标点语义。按空白 split 之后可以复用序列上的双指针思想，但会把分词所需空间计入成本，也会改变多空格等输入的含义。

**为什么不是通用编辑距离？** 只判断距离是否为一，长度关系和第一次不匹配已经限制了可选操作。完整 DP 在最坏情况下需要平方级计算，解决了比题目更大的问题。

**可以用来做训练数据 near-duplicates 吗？** 可以作为非常局部的判定器，但不能把一次字符编辑自动视为语义等价。“有”和“无”只差一个字，训练标签可能完全相反。
