---
id: openai-resumable-iter
section: openai
order: 41
level: A
title: OpenAI：可恢复迭代器，getState 之后还能接着 next
quick: "我会把状态定义为下一次 next 要读取的位置，保存时返回独立值，setState 后能重复恢复，耗尽状态也一样。比如读完 1、2 时保存，恢复后下一项仍是 3；多文件时再把文件标识、版本和内部偏移嵌进状态。"
tags:
  - 完整编程练习
  - OpenAI
  - Coding
  - Iterator
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Targeting OpenAI SWE Roles, r/leetcode
    url: https://www.reddit.com/r/leetcode/comments/1qlzflr/targeting_openai_swe_roles_insights_on_what_to/
    type: secondary
  - title: "FAANG-Coding-Interview-Questions, OpenAI bank"
    url: https://github.com/ombharatiya/FAANG-Coding-Interview-Questions/blob/main/FAANG-Recent-Questions.md
    type: secondary
---

## 题目描述

实现嵌套数据的整数叶子遍历、结构恢复，以及可保存并恢复下一读取位置的迭代器。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `flatten(x) -> list[int]`：按深度优先、从左到右列出嵌套结构里的 int 叶子。容器支持 list、tuple 和键为字符串的 dict，dict 按插入顺序遍历；bool 不当作 int。
- `unflatten(template, values)`：用 `values` 依次替换 `template` 的叶子，保留容器类型和 dict 顺序。`values` 的整数个数与模板叶子数相同。
- `Iterator(x)`：`next` 依次返回叶子，读完抛 `StopIteration`；`get_state()` 返回下一项的下标；`set_state(i)` 可以反复恢复，要求 $0\le i\le$ 叶子数。
- 约束：数据在构造后视为不可变；最多 $10^4$ 个叶子，嵌套深度不超过 100。

### 输入输出示例

```text
flatten([1, (), {"a": [2, 3]}])                 -> [1, 2, 3]
unflatten([1, (), {"a": [2, 3]}], [7, 8, 9])    -> [7, (), {"a": [8, 9]}]
it = Iterator(...); next(it) -> 1; s = it.get_state()   # s == 1
list(it) -> [2, 3]; it.set_state(s); next(it) -> 2
```

## 解题思路与参考答案

我会先定义清楚状态代表「下一次要读哪里」，再实现 next、保存和恢复。比如列表读出 1、2 后保存，继续读过 3，再恢复，下一次仍应返回 3；保存的状态不能随着后续迭代一起变化。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或隐藏测试；公开来源只给了题型（见下面「题怎么来的」）。Python 3，只用标准库。

### 题面、接口与约束

- `flatten(x) -> list[int]`：按深度优先、从左到右列出嵌套结构里的 int 叶子。容器支持 list、tuple 和键为字符串的 dict，dict 按插入顺序遍历；bool 不当作 int。
- `unflatten(template, values)`：用 `values` 依次替换 `template` 的叶子，保留容器类型和 dict 顺序。值太少、太多或叶子非法时抛 `ValueError`。
- `Iterator(x)`：`next` 依次返回叶子；`get_state()` 返回下一项的下标；`set_state(i)` 可以反复恢复，要求 $0\le i\le$ 叶子数，否则抛 `ValueError`。
- 约束：数据在构造后视为不可变；最多 $10^4$ 个叶子，嵌套深度不超过 100。

### 输入输出示例

```text
flatten([1, (), {"a": [2, 3]}])                 -> [1, 2, 3]
unflatten([1, (), {"a": [2, 3]}], [7, 8, 9])    -> [7, (), {"a": [8, 9]}]
it = Iterator(...); next(it) -> 1; s = it.get_state()   # s == 1
list(it) -> [2, 3]; it.set_state(s); next(it) -> 2
```

### 解题思路与正确性

`unflatten` 递归遍历模板：遇到容器就用同样的构造方式（list、tuple、dict）重建，遇到叶子就从 `values` 里取恰好一个值。遍历顺序和 `flatten` 完全一样，所以结构和顺序都能还原；最后再检查 `values` 是否刚好用完。

迭代器的状态定义为「下一次 `next` 要读的位置」，是一个整数，返回给调用方后不会随迭代器变化。迭代结束时的状态等于叶子数，也可以保存和恢复。这份实现在构造时先把结构展开成列表，不支持无限流或超大的文件流。

### 完整参考实现（Python 3）

```python
def flatten(x):
    """按深度优先、从左到右的顺序列出嵌套结构里的所有 int 叶子。

    容器可以是 list、tuple 或键为 str 的 dict（按插入顺序）；bool 不算 int。
    """
    if type(x) is int:
        return [x]
    if isinstance(x, dict):
        if not all(isinstance(key, str) for key in x):
            raise ValueError("dict keys must be strings")
        children = x.values()
    elif isinstance(x, (list, tuple)):
        children = x
    else:
        raise ValueError(f"unsupported leaf: {x!r}")
    return [leaf for child in children for leaf in flatten(child)]


def unflatten(template, values):
    """用 values 依次替换 template 里的叶子，保留容器类型和 dict 顺序。

    values 的个数必须恰好等于叶子数，每个值都必须是 int，否则抛 ValueError。
    """
    remaining = iter(values)

    def walk(node):
        if type(node) is int:
            try:
                value = next(remaining)
            except StopIteration:
                raise ValueError("too few values for template") from None
            if type(value) is not int:
                raise ValueError(f"value must be int, got {value!r}")
            return value
        if isinstance(node, dict):
            return {key: walk(child) for key, child in node.items()}
        if isinstance(node, list):
            return [walk(child) for child in node]
        if isinstance(node, tuple):
            return tuple(walk(child) for child in node)
        raise ValueError(f"unsupported template node: {node!r}")

    result = walk(template)
    try:
        next(remaining)
    except StopIteration:
        return result
    raise ValueError("too many values for template")


class Iterator:
    """遍历嵌套结构的叶子；状态是下一次 next 要返回的叶子下标。"""

    def __init__(self, x):
        self.items = flatten(x)   # 构造后数据视为不可变
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos == len(self.items):
            raise StopIteration
        value = self.items[self.pos]
        self.pos += 1
        return value

    def get_state(self):
        return self.pos

    def set_state(self, pos):
        """恢复到某个状态；0 <= pos <= 叶子数，耗尽时的状态也能恢复。"""
        if type(pos) is not int or not 0 <= pos <= len(self.items):
            raise ValueError(f"invalid state {pos!r} for {len(self.items)} items")
        self.pos = pos
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert flatten(nested) == [1, 2, 3]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


nested = [1, (), {"a": [2, 3]}]

# flatten 按顺序取叶子；unflatten 保留容器类型（空 tuple、dict）
assert flatten(nested) == [1, 2, 3]
assert unflatten(nested, [7, 8, 9]) == [7, (), {"a": [8, 9]}]
assert isinstance(unflatten(nested, [7, 8, 9])[1], tuple)

# 保存状态后读完，再恢复，下一项还是 2；可以反复恢复
it = Iterator(nested)
assert next(it) == 1
state = it.get_state()
assert list(it) == [2, 3]
it.set_state(state)
assert list(it) == [2, 3]
it.set_state(state)
assert next(it) == 2

# 耗尽时的状态也能保存和恢复，恢复后仍是耗尽
assert list(it) == [3]
end_state = it.get_state()
assert end_state == 3
it.set_state(0)
it.set_state(end_state)
assert list(it) == []

# 值太少或太多都报错
expect_value_error(unflatten, nested, [1])
expect_value_error(unflatten, nested, [1, 2, 3, 4])

# 全是空容器：没有叶子
assert list(Iterator([[], (), {}])) == []

# bool、非字符串键、越界或非 int 的状态都报错
expect_value_error(flatten, [True])
expect_value_error(flatten, {1: 2})
expect_value_error(it.set_state, 4)
expect_value_error(it.set_state, True)
```

### 复杂度与追问

设叶子数为 $n$、嵌套深度为 $h$。`unflatten` 是 $O(n)$；`flatten` 和构造迭代器在这份实现里因为每层都拼接一次列表，最坏是 $O(nh)$ 时间、$O(n)$ 空间。`next`、`get_state`、`set_state` 都是 $O(1)$。

- 追问「把 flatten 降到 $O(n)$」：递归时传入同一个结果列表，往里 append，不在每层生成新列表。
- 追问「数据来自文件流」：状态里要放文件路径、文件版本和字节偏移，而不是叶子下标，见下面「多文件」一节。

## 题怎么来的

同一篇 Reddit 上的 OpenAI SWE 题单里有一句：实现一个能在遍历中途停下、之后再从原位置继续的迭代器。GitHub 题单把它写成最多六段递进：列表、多文件、异步、二维、三维，接口是 `getState` / `setState`。没有任何公开帖贴出完整的签名和测试，所以 `realInterview: false`。下面按这两份清单里重复出现的行为来写，现场以面试官的测试为准。

## 列表

`next` 返回当前元素并前进。用完时要抛出明确的结束信号，不要返回 `None` 当哨兵，因为数据里本身可能有 `None`。

`getState` 返回的是「下一次 `next` 会读的位置」，不是上一次已经交出去的那个。以列表 `[1, 2, 3, 4]` 为例：调用两次 `next` 得到 1 和 2，此时状态指向 3。再调用 `next` 得到 3，然后 `setState` 回刚才保存的状态，下一次 `next` 应该仍然得到 3。

状态要做成不可变的小对象或元组，调用方只能改自己的拷贝，改不到迭代器内部。如果要求拒绝来自别的迭代器的状态，就在状态里带上迭代器的 id 一起校验；练习版和下面的 `ListIter` 只用一个整数下标，没有做这一步。

```python
class ListIter:
    def __init__(self, data):
        self.data = data
        self.i = 0

    def next(self):
        if self.i >= len(self.data):
            raise StopIteration
        value = self.data[self.i]
        self.i += 1
        return value

    def get_state(self):
        return self.i

    def set_state(self, state):
        if type(state) is not int or not 0 <= state <= len(self.data):
            raise ValueError(f"invalid state: {state!r}")
        self.i = state
```

## 多文件

外层状态是 `(file_index, inner_state)`。空文件不能让外层卡住：当前文件的 `next` 读完了，就打开下一个文件，直到读到元素或者所有文件都用完。如果只存文件下标、不存文件内的位置，恢复后会从头重读这个文件。

到了异步那一档，`getState` 不要等在途的读操作完成再返回。状态只能处在两种情况之一：「这一次读还没开始」，或者「字节已经拿到、位置已经前进」。如果状态停在半次 `read` 上，恢复时会重复读或者丢掉一块数据。

二维是把内层迭代器的状态嵌进外层状态里。不要假设内层状态一定是整数。接口从第一档开始就接收不透明的状态对象，后面几档就不用改外层协议。

## 追问

**状态能不能直接返回迭代器自己？**
不能。调用方会留着这个对象，你继续 `next` 之后它也跟着变，就无法回到过去。返回时要复制下标。

**`setState` 之后文件被改了怎么办？**
题面通常假设文件不变。如果面试官加上这个条件，状态里要带文件长度或校验值，对不上就报错，不要静默地读到别的记录。

## 相关题

- [[p3a-openai-resumable-iterator]]：同一道 OpenAI 题的另一份整理，正文多讲了嵌套时的游标栈，练习的 flatten/Iterator 契约几乎一样，题面契约不完全一致。
- [[p3a-xai-resumable-iterator-design]]：xAI 的同类题，问法偏「迭代器的迭代器」和跨进程恢复，练习代码与上一张相同。
- [[p3a-xai-flatten-unflatten-nested-structure]]：只做这里的 `flatten` / `unflatten` 两个函数，迭代器部分是附带的。
