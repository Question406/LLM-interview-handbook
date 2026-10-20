---
id: p3a-xai-resumable-iterator-design
section: xai
order: 602
level: A
title: "xAI：迭代器 checkpoint：跨进程与嵌套恢复"
quick: "把状态定义成下一个要返回的位置；嵌套结构用游标栈记录每层下标，保存时复制，跨进程恢复还要记下文件路径、版本和偏移。"
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
  - title: "1Point3Acres · xAI · resumable-iterator-design"
    url: https://www.1point3acres.com/interview/problems/company/xai/resumable-iterator-design
    type: secondary
---

## 题目

设计一个可以保存进度、之后再恢复的迭代器：先支持在当前位置保存状态并恢复，再扩展到「迭代器的迭代器」，也就是嵌套结构的情况。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先定义状态的含义：状态是「下一个要返回的位置」，而不是「刚才返回的值」。这样迭代器耗尽之后也有一个明确的状态，恢复多少次结果都一样。

扁平的列表只需要一个下标。嵌套结构的标准答案是游标栈：栈里每一层记录「当前在哪个容器、下一个要看第几个元素」。`next` 从栈顶推进，遇到子容器就压栈，遇到叶子就返回，一层走完就弹栈。保存状态就是把每层的下标复制一份；恢复时从根开始，按这些下标逐层走回原来的位置。这个做法只用 O(h) 的额外内存（h 是嵌套深度），面试里应该讲这个。

几个容易漏的边界：空的子容器、连续好几层都是空的、在末尾保存再恢复。保存的状态必须是一份拷贝，否则继续迭代时快照也跟着变了。

如果数据来自文件流、要跨进程恢复，状态里还要有资源标识，比如文件路径、文件版本和字节偏移，不能只存活着的对象引用。

下面的练习代码和 [[p3a-xai-flatten-unflatten-nested-structure]] 共用。为了简短，它没有实现游标栈，而是先把结构展开成列表，用列表下标做状态，代价是 O(n) 的额外内存。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `flatten(x) -> list[int]`：支持 `int`、`list`、`tuple` 和 key 为字符串的 `dict`，按深度优先顺序返回整数叶子。遇到其他类型的叶子（包括 `bool`）抛 `ValueError`。
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

迭代器的状态定义成「下一个要返回的位置」，耗尽之后也能保存和恢复，恢复多少次结果都一样。

这份实现没有维护游标栈，而是在构造时先 `flatten` 成列表，状态就是列表下标。这样 `next`、`get_state`、`set_state` 都是 O(1)，代码也短，但要多占 O(n) 内存存所有叶子，也不支持无限流或放不进内存的输入。面试时如果被要求省内存，就要换成上面「思路」里的游标栈写法。

`unflatten` 递归地按模板重建：碰到容器就用同样的构造方式重建子节点，碰到整数叶子就从 `values` 里取一个。每个叶子恰好消费一个值，所以结构和顺序都不变；遍历结束后还能从 `values` 里取到值，说明值多了。

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

设叶子数为 n、嵌套深度为 h。`flatten` 和构造迭代器是 O(n) 时间、O(n) 空间（递归栈另占 O(h)）。实现里所有层共用一个 `leaves` 列表；如果每层各自返回列表再 `extend` 拼接，每个叶子会在每一层被复制一次，最坏变成 O(n·h)。`unflatten` 是 O(n)；`next`、`get_state`、`set_state` 都是 O(1)。

- 不想预先展开，怎么做？用游标栈：栈里每层存「当前容器、下一个要看的下标」，`next` 时从栈顶往下推进，遇到容器就压栈，遇到叶子就返回，走完一层就弹栈。状态是整个栈里的下标列表（加上耗尽标记），保存时要复制一份，不能把正在用的栈直接交出去。额外内存只有 O(h)，但 `set_state` 要按下标逐层重新定位，代价是 O(h)。
- 数据来自文件流、要跨进程恢复呢？状态不能存活着的对象引用，要存文件路径、文件版本（恢复时校验文件没变）、字节偏移，再加上嵌套结构里的游标栈。

## 相关题

- [[p3a-openai-resumable-iterator]]：OpenAI 的同类题，练习代码和本题完全相同，题面按一维、二维、三维递进。
- [[openai-resumable-iter]]：手册里较早的 OpenAI 版本，接口是 `next` / `getState` / `setState`，正文多了多文件的递进。
- [[p3a-xai-flatten-unflatten-nested-structure]]：同为 xAI，练习代码共用，问法只问嵌套容器的 `flatten` / `unflatten`。
