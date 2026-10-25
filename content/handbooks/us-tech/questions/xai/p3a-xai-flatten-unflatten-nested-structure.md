---
id: p3a-xai-flatten-unflatten-nested-structure
section: xai
order: 604
level: A
title: "xAI：嵌套 Python 容器 flatten 与 unflatten"
quick: "我会让 flatten 和 unflatten 使用同一个深度优先顺序，前者取叶子、后者按模板回填，返回新对象。list、tuple、dict 和空容器原样保留，叶子值多了少了都报错；bool 是否算整数、dict key 是否参与遍历要先确认。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · flatten-unflatten-nested-structure"
    url: https://www.1point3acres.com/interview/problems/company/xai/flatten-unflatten-nested-structure
    type: secondary
---

## 题目描述

实现嵌套容器的叶子遍历、结构重建和可保存恢复位置的迭代器。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

数据由整数叶子以及 list、tuple、字符串键 dict 递归组成，bool 不作为整数叶子；字典按插入顺序遍历。构造后数据不再改变，整数叶子不超过 10000，深度不超过 100。

`flatten(x)` 返回深度优先顺序的整数列表。`unflatten(template,values)` 用 values 依次替换模板中的整数叶子，保留所有容器类型、空容器和字典顺序；values 为恰好与叶子数相等的整数序列。

`Iterator(x)` 支持 `next(iterator)`、`get_state()` 和 `set_state(i)`。state 是下一个待返回叶子的零基索引，可取 0 到叶子总数；恢复可前进或回退，多次恢复同状态结果相同。到末尾后 next 抛出 StopIteration。

### 示例

```text
x=[1,(),{"a":[2,3]}]
flatten(x)=[1,2,3]
unflatten(x,[7,8,9])=[7,(),{"a":[8,9]}]
it=Iterator(x)：第一次 next 为 1，此后 get_state()=1。
set_state(1) 后 next 为 2；再次 set_state(1)，next 仍为 2。
```

## 解题思路与参考答案

我会让展开和回填共用同一套深度优先顺序，保证第 k 个整数回到第 k 个叶子位置。例如 `[1, (), {"a": [2, 3]}]` 换一组整数后，空 tuple 和 dict 里的嵌套层级都要保留，模板本身不变。

## 题目

给一个由 list、tuple、dict 层层嵌套、叶子是整数的 Python 对象。写两个函数：`flatten` 按顺序取出所有整数；`unflatten` 拿原对象当模板，把一组新整数按同样顺序填回去，得到结构相同的新对象。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

两个函数共用同一种遍历顺序：深度优先，list/tuple 按下标，dict 按插入顺序走 value。只要 `flatten` 和 `unflatten` 用的是同一个顺序，第 k 个取出来的整数就一定对应回填时的第 k 个位置。

回填时递归创建新容器，tuple 仍然是 tuple，空容器也保留。每到一个整数叶子才取一个新值，所以新值数量必须和叶子数完全一致；多了、少了都报错，模板不做就地修改。

动手前值得和面试官确认两个边界：`True` 算不算整数（Python 里 `bool` 是 `int` 的子类），以及 dict 的 key 要不要参与遍历。这份练习的约定是 `bool` 不算叶子、key 不参与。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `flatten(x) -> list[int]`：支持 `int`、`list`、`tuple` 和 key 为字符串的 `dict`。遇到其他类型的叶子（包括 `bool`）抛 `ValueError`。
- `unflatten(template, values)`：按 `template` 的结构回填 `values`，保留 dict 的插入顺序和容器类型。值不够、值多了或值不是整数，都抛 `ValueError`。
- `Iterator(x)`：逐个返回叶子。`get_state()` 返回下一个要返回的叶子下标；`set_state(i)` 可以反复恢复到任意合法状态，要求 $0 \le i \le$ 叶子数。
- 构造后数据视为不可变。最多 $10^4$ 个叶子，嵌套深度不超过 100。

### 输入输出示例

```text
flatten([1, (), {"a": [2, 3]}])               -> [1, 2, 3]
unflatten([1, (), {"a": [2, 3]}], [7, 8, 9])  -> [7, (), {"a": [8, 9]}]
```

迭代器取出 1 之后 `get_state()` 得到 1；继续取完，再 `set_state(1)`，下一项又是 2。

### 解题思路与正确性

`unflatten` 递归地按模板重建：碰到容器就用同样的构造方式（dict 推导、list 推导、`tuple(...)`）重建子节点，碰到整数叶子就从 `values` 的迭代器里取一个。每个叶子恰好消费一个值，所以结构和顺序都不变。遍历结束后再从迭代器多取一次，取得到说明值多了。

迭代器的状态定义成「下一个要返回的位置」，所以耗尽之后也能保存和恢复。这份实现在构造时先 flatten 成列表，换来 O(1) 的 `next` 和状态操作，代价是不支持无限流或放不进内存的超大输入。

### 完整参考实现（Python 3）

```python
def flatten(node):
    """按深度优先顺序返回所有整数叶子。dict 按插入顺序遍历 value。"""
    leaves = []
    _collect_leaves(node, leaves)
    return leaves


def _collect_leaves(node, leaves):
    # 所有层共用一个 leaves 列表，每个叶子只追加一次，总时间 O(n)
    if type(node) is int:  # bool 是 int 的子类，这里故意排除
        leaves.append(node)
        return
    if isinstance(node, dict):
        if not all(isinstance(key, str) for key in node):
            raise ValueError("dict keys must be str")
        children = node.values()
    elif isinstance(node, (list, tuple)):
        children = node
    else:
        raise ValueError(f"unsupported leaf: {node!r}")
    for child in children:
        _collect_leaves(child, leaves)


def unflatten(template, values):
    """按 template 的结构依次填入 values，返回新对象，不修改 template。"""
    remaining = iter(values)

    def rebuild(node):
        if type(node) is int:
            try:
                value = next(remaining)
            except StopIteration:
                raise ValueError("too few values") from None
            if type(value) is not int:
                raise ValueError(f"value must be int: {value!r}")
            return value
        if isinstance(node, dict):
            return {key: rebuild(child) for key, child in node.items()}
        if isinstance(node, list):
            return [rebuild(child) for child in node]
        if isinstance(node, tuple):
            return tuple(rebuild(child) for child in node)
        raise ValueError(f"unsupported template node: {node!r}")

    result = rebuild(template)
    leftover = object()
    if next(remaining, leftover) is not leftover:
        raise ValueError("too many values")
    return result


class Iterator:
    """遍历嵌套结构的整数叶子；状态是「下一个要返回的叶子下标」。"""

    def __init__(self, data):
        self.leaves = flatten(data)
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos == len(self.leaves):
            raise StopIteration
        value = self.leaves[self.pos]
        self.pos += 1
        return value

    def get_state(self):
        return self.pos

    def set_state(self, pos):
        if type(pos) is not int or not 0 <= pos <= len(self.leaves):
            raise ValueError(f"invalid state: {pos!r}")
        self.pos = pos
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert flatten(data) == [1, 2, 3]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

data = [1, (), {"a": [2, 3]}]
assert flatten(data) == [1, 2, 3]
assert unflatten(data, [7, 8, 9]) == [7, (), {"a": [8, 9]}]

# 保存状态后继续迭代，再恢复，应能重放同一段
it = Iterator(data)
assert next(it) == 1
state = it.get_state()
assert list(it) == [2, 3]
it.set_state(state)
assert list(it) == [2, 3]

expect_value_error(unflatten, data, [1])           # 值不够
expect_value_error(unflatten, data, [1, 2, 3, 4])  # 值多了
expect_value_error(flatten, [True])                # bool 不算整数叶子
expect_value_error(it.set_state, 4)                # 超出叶子数
assert list(Iterator([[], (), {}])) == []
```

### 复杂度与追问

设叶子数为 n、嵌套深度为 h。`flatten` 和构造迭代器是 O(n) 时间、O(n) 空间（递归栈另占 O(h)）；`unflatten` 是 O(n)；`next`、`get_state`、`set_state` 都是 O(1)。

常见追问是「数据来自文件流，不能一次读进内存怎么办」。这时状态不能只是一个下标，要记下文件路径、文件版本（防止恢复时文件已经变了）和字节偏移，再加上当前在嵌套结构里的游标栈。

## 相关题

- [[p3a-xai-resumable-iterator-design]]：练习代码和本题共用，问法换成迭代器的保存与恢复，重点在状态定义和游标栈。
- [[p3a-openai-resumable-iterator]]：OpenAI 的可恢复迭代器题，同样共用这份练习代码。
- [[openai-resumable-iter]]：手册里较早的同类题，练习也带 `flatten` / `unflatten`，正文多了多文件的递进。
