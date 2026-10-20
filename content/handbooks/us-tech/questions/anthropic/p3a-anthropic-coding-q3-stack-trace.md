---
id: p3a-anthropic-coding-q3-stack-trace
section: anthropic
order: 602
level: A
title: "Anthropic：调用栈重建：事件、采样、递归与去噪"
quick: "比较相邻两次栈采样的最长公共前缀，旧栈多出的帧由深到浅输出 end，新栈多出的帧由浅到深输出 start，递归同名帧用深度区分。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · coding-q3-stack-trace"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/coding-q3-stack-trace
    type: secondary
---

## 题目

题目有两种形式：给一串 enter / exit 事件恢复调用栈；或者反过来，给一串带时间戳的栈采样，推出每个函数的开始和结束事件。后者还会追问递归和去噪。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

比较相邻两次采样，找出最长公共前缀。前缀部分是一直在运行的调用链，什么都不用做。旧栈在前缀之后的部分都结束了，要从最深的帧开始依次输出 end；新栈在前缀之后的部分都是新开始的，从最浅的帧开始依次输出 start。这个顺序保证事件流始终是合法的嵌套。

递归时同一个函数名会在栈里出现多次，所以要按「位置 + 函数名」比较，并在事件里带上深度。比如 `[f, f]` 变成 `[f]`，结束的是深度 1 的那个 f。

要说清楚两点局限：

- 采样只能看到采样时刻的状态。两次采样之间如果有一次很短的调用开始又结束，这份数据里完全看不出来，所以输出的是「观测到的事件」，不是真实的完整执行历史。
- 去噪要先定义规则，例如一个帧至少连续出现 N 次采样才算真的调用过。阈值不同，输出的事件也不同，要和面试官确认。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `events(samples, end_time=None)`：`samples` 是按时间升序的 `(timestamp, stack)` 列表，`stack` 从外到内排列，允许递归重名。返回 `(timestamp, "start" / "end", function, depth)` 事件列表。
- 相邻采样之间先结束旧栈的后缀（由内到外），再开始新栈的后缀（由外到内）。两次采样的栈相同时不输出事件。
- `end_time` 可选，必须不早于最后一次采样，用来在那一刻结束剩下的栈；不给时剩下的栈保持活跃，不输出 end。
- 采样时间倒退或 `end_time` 太早时抛 `ValueError`。采样数不超过 $10^4$，栈深度不超过 100。

### 输入输出示例

```text
events([(0, ["a", "b"]), (1, ["a", "c"])], end_time=2)
  -> (0, start, a, 0)
     (0, start, b, 1)
     (1, end,   b, 1)
     (1, start, c, 1)
     (2, end,   c, 1)
     (2, end,   a, 0)
```

### 解题思路与正确性

两次采样的最长公共前缀，是在这两个时刻都处于活跃状态、而且身份相同的调用链。按位置比较意味着深度也一致，所以递归重名不会混淆。前缀之外的旧帧必须已经返回，前缀之外的新帧必须是新调用的，这正是代码输出的事件。

这份实现不处理采样丢失或抖动：如果某个帧在一次采样里短暂消失又出现，会被当成结束后重新开始。要去噪，需要另外定义缺失模型，不能只凭函数名猜测是不是同一次调用。

### 完整参考实现（Python 3）

```python
def events(samples, end_time=None):
    """把按时间排序的栈采样转换成 (timestamp, "start" / "end", function, depth) 事件。

    stack 从外到内排列。相邻两次采样先结束旧栈多出来的部分（由内到外），
    再开始新栈多出来的部分（由外到内）。给了 end_time 时，在那一刻结束剩余的栈。
    """
    result = []
    prev_stack = []
    last_time = float("-inf")
    for timestamp, stack in samples:
        if timestamp < last_time:
            raise ValueError(f"samples out of order: {timestamp} < {last_time}")
        last_time = timestamp
        stack = list(stack)

        # 最长公共前缀是两次采样之间一直在运行的调用链；按位置比较，递归重名也能区分
        common = 0
        while (common < min(len(prev_stack), len(stack))
               and prev_stack[common] == stack[common]):
            common += 1

        for depth in range(len(prev_stack) - 1, common - 1, -1):
            result.append((timestamp, "end", prev_stack[depth], depth))
        for depth in range(common, len(stack)):
            result.append((timestamp, "start", stack[depth], depth))
        prev_stack = stack

    if end_time is not None:
        if end_time < last_time:
            raise ValueError(f"end_time {end_time} is before the last sample {last_time}")
        for depth in range(len(prev_stack) - 1, -1, -1):
            result.append((end_time, "end", prev_stack[depth], depth))
    return result
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# b 换成 c：先结束 b，再开始 c；end_time 时由内到外结束剩余栈
result = events([(0, ["a", "b"]), (1, ["a", "c"])], 2)
assert result == [
    (0, "start", "a", 0),
    (0, "start", "b", 1),
    (1, "end", "b", 1),
    (1, "start", "c", 1),
    (2, "end", "c", 1),
    (2, "end", "a", 0),
]

# 递归：结束的是深度 1 的 f，深度 0 的 f 还在
assert events([(0, ["f", "f"]), (1, ["f"])])[-1] == (1, "end", "f", 1)

# 相同采样不产生新事件
assert len(events([(0, ["a"]), (1, ["a"])])) == 1

# 时间倒退
expect_value_error(events, [(1, ["a"]), (0, ["a"])])
expect_value_error(events, [(1, ["a"])], 0)
```

### 复杂度与追问

设所有采样栈的元素总数为 N、输出事件数为 E。时间是 O(N + E)，除输出外的工作空间是 O(最大深度)。连续相同的栈不产生事件，相当于自动压缩。

如果追问「输入是 enter / exit 事件流，恢复调用栈」：用一个栈，enter 时压入，exit 时检查栈顶是否是同一个函数再弹出，不匹配就报错或按约定修复。

如果追问去噪：可以给每个深度上的帧记录连续出现的次数，只有达到阈值才输出 start，并把 start 的时间回填到它第一次出现的采样；结束同理，连续消失若干次才算结束。
