---
id: anthropic-perf-takehome
section: anthropic
order: 26
level: A
title: Anthropic：开源的性能 take-home，是一台 VLIW SIMD 机器
quick: "我会先保证标量结果正确，再向量化并把独立操作装进同一周期，减少执行周期数。同周期读旧值、周期末才写回，所以依赖链必须跨周期；官方 anthropics/original_performance_takehome 是旧版作业，多核在这版里故意关闭。"
tags:
  - 完整编程练习
  - Anthropic
  - Coding
  - Performance
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: anthropics/original_performance_takehome
    url: https://github.com/anthropics/original_performance_takehome
    type: primary
  - title: Machine class in problem.py
    url: https://github.com/anthropics/original_performance_takehome/blob/main/problem.py
    type: primary
---

## 题目描述

为一台具有多个执行引擎的 VLIW SIMD 模拟机生成确定性指令调度，并执行调度得到所有寄存器的最终值。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- 指令是 `(engine, op, dst, args)`：`op` 取 `+`、`*`、`^`；寄存器值是形状相同的 `uint32` 向量，运算按 $2^{32}$ 取模。寄存器是 SSA 形式：每个 `dst` 只被定义一次，也不能和初始寄存器重名；`args` 可以引用任意一条指令定义的寄存器。
- `schedule(instructions, initial, slots) -> list[list[int]]`：把指令下标打包成若干个周期（bundle）。`slots[engine]` 是该引擎每周期的槽数，必须为正。同一周期内，所有依赖在该周期开始前已经满足的待执行指令，按原下标升序获得对应引擎的可用槽位。输入的依赖有定义且无环。
- `execute(instructions, bundles, initial, slots) -> dict`：校验并执行这份调度。同一周期的所有槽读周期开始时的旧状态，周期结束时一起写回，所以一条依赖链不能出现在同一个周期里。每条指令恰好执行一次，每周期各引擎不得超过槽数，也不能使用该周期内刚产生的寄存器值。
- 目标是结果正确、把独立指令打包到同一周期，不要求最优调度。

### 输入输出示例

```text
initial = {"a": uint32([1]), "b": uint32([5])}
instructions = [("alu", "+", "t", ("a", "b")),
                ("alu", "^", "x", ("a", "b")),
                ("alu", "*", "out", ("t", "x"))]
slots = {"alu": 2}
schedule(instructions, initial, slots) -> [[0, 1], [2]]
execute(instructions, [[0, 1], [2]], initial, slots)["out"] -> uint32([24])
```

## 解题思路与参考答案

这题的优化方向是向量化和指令调度：先把标量核跑对，再让独立操作共享一个周期。比如 `valu` 做两条算术时，独立的 `load` 也可以一起执行；但本周期刚产生的值，要到下一周期才能使用。

## 完整编程练习（手册重构版）

> 下面是手册自己设计的简化 VLIW/SIMD 小练习，接口、约束和测试都是手册约定，不是官方仓库的完整机器或提交答案。Python 3 + NumPy，CPU 上验证。

### 题面、接口与约束

- 指令是 `(engine, op, dst, args)`：`op` 取 `+`、`*`、`^`；寄存器值是形状相同的 `uint32` 向量，运算按 $2^{32}$ 取模。寄存器是 SSA 形式：每个 `dst` 只被定义一次，也不能和初始寄存器重名；`args` 可以引用任意一条指令定义的寄存器。
- `schedule(instructions, initial, slots) -> list[list[int]]`：把指令下标打包成若干个周期（bundle）。`slots[engine]` 是该引擎每周期的槽数，必须为正。每一轮按原指令下标顺序，把依赖已满足的指令贪心填进还有空槽的引擎。遇到未定义寄存器或依赖环时抛 `ValueError`。
- `execute(instructions, bundles, initial, slots) -> dict`：校验并执行这份调度。同一周期的所有槽读周期开始时的旧状态，周期结束时一起写回，所以一条依赖链不能出现在同一个周期里。重复执行、漏执行、超出槽数、同周期依赖都抛 `ValueError`。
- 目标是结果正确、把独立指令打包到同一周期，不要求最优调度。

### 输入输出示例

```text
slots = {"alu": 2}
t = a + b;  x = a ^ b;  out = t * x
schedule(...)              -> [[0, 1], [2]]   # 两条独立 alu 同周期，乘法要等下一周期
execute(..., [[0, 2], [1]]) -> ValueError       # out 和它的输入 t 放在了同一周期
```

### 解题思路与正确性

`schedule` 先为每个寄存器记下定义它的指令，再算出每条指令依赖哪些指令。每一轮里，依赖全部在“已完成集合”中的指令就是 ready 的，按下标顺序逐条放进还有空槽的引擎。如果某一轮一条都放不进去，说明剩下的指令互相等待，也就是有环。

关键是“已完成集合”只在一轮结束后才更新。这样同一周期新产生的值不会被同周期的消费者用到，对应机器“周期末才写回”的规则。`execute` 用同样的规则做独立校验：本周期的结果先写进 `pending`，周期结束才并入 `state`，所以同周期依赖会因为读不到输入而被拒绝。

寄存器用 `uint32` 数组，一条指令一次算完所有 lane，方便直接和标量公式对照。

### 完整参考实现（Python 3）

```python
import numpy as np

OPERATIONS = {"+": np.add, "*": np.multiply, "^": np.bitwise_xor}


def schedule(instructions, initial, slots):
    """把 SSA 指令贪心打包成周期列表；返回每个周期内的指令下标。"""
    producers = {}  # 寄存器名 -> 定义它的指令下标
    for index, (engine, op, dst, _) in enumerate(instructions):
        if slots.get(engine, 0) < 1:
            raise ValueError(f"instruction {index}: engine {engine!r} has no slots")
        if op not in OPERATIONS:
            raise ValueError(f"instruction {index}: unknown op {op!r}")
        if dst in producers or dst in initial:
            raise ValueError(f"instruction {index}: register {dst!r} defined twice (not SSA)")
        producers[dst] = index

    dependencies = []
    for index, (_, _, _, args) in enumerate(instructions):
        deps = set()
        for arg in args:
            if arg in producers:
                deps.add(producers[arg])
            elif arg not in initial:
                raise ValueError(f"instruction {index}: undefined register {arg!r}")
        dependencies.append(deps)

    done = set()
    bundles = []
    while len(done) < len(instructions):
        ready = [
            index for index in range(len(instructions))
            if index not in done and dependencies[index] <= done
        ]
        used = {}
        bundle = []
        for index in ready:
            engine = instructions[index][0]
            if used.get(engine, 0) < slots[engine]:
                bundle.append(index)
                used[engine] = used.get(engine, 0) + 1
        if not bundle:
            raise ValueError("dependency cycle")
        bundles.append(bundle)
        done.update(bundle)  # 周期结束才更新，同周期的结果不能被同周期使用
    return bundles


def execute(instructions, bundles, initial, slots):
    """按调度执行并校验：每周期读旧状态、周期末统一写回。返回最终寄存器状态。"""
    state = {name: np.asarray(value, dtype=np.uint32).copy() for name, value in initial.items()}
    executed = set()
    for cycle, bundle in enumerate(bundles):
        pending = {}
        used = {}
        for index in bundle:
            if index in executed:
                raise ValueError(f"cycle {cycle}: instruction {index} executed twice")
            engine, op, dst, args = instructions[index]
            used[engine] = used.get(engine, 0) + 1
            if used[engine] > slots.get(engine, 0):
                raise ValueError(f"cycle {cycle}: engine {engine!r} over its slot limit")
            if dst in pending or dst in state:
                raise ValueError(f"cycle {cycle}: register {dst!r} written twice")
            if any(arg not in state for arg in args):
                raise ValueError(f"cycle {cycle}: instruction {index} reads a value not yet written")
            pending[dst] = OPERATIONS[op](*(state[arg] for arg in args))
            executed.add(index)
        state.update(pending)
    if len(executed) != len(instructions):
        raise ValueError("some instructions were never executed")
    return state
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert bundles == [[0, 1], [2]]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


initial = {
    "a": np.array([1, 2, 3, 4], np.uint32),
    "b": np.array([5, 6, 7, 8], np.uint32),
}
instructions = [
    ("alu", "+", "t", ("a", "b")),
    ("alu", "^", "x", ("a", "b")),
    ("alu", "*", "out", ("t", "x")),
]
slots = {"alu": 2}

# 两条独立 alu 同周期，乘法放到下一周期
bundles = schedule(instructions, initial, slots)
assert bundles == [[0, 1], [2]]

# 打包后的结果和逐条执行一致，也和直接计算一致
packed = execute(instructions, bundles, initial, slots)
serial = execute(instructions, [[0], [1], [2]], initial, slots)
expected = (initial["a"] + initial["b"]) * (initial["a"] ^ initial["b"])
assert np.array_equal(packed["out"], serial["out"])
assert np.array_equal(packed["out"], expected)

# 只有 1 个 alu 槽时每周期一条
assert schedule(instructions, initial, {"alu": 1}) == [[0], [1], [2]]

# uint32 乘法按 2^32 回绕
big = {"a": np.array([2**31], np.uint32)}
wrap = [("alu", "*", "y", ("a", "a"))]
assert execute(wrap, schedule(wrap, big, slots), big, slots)["y"][0] == 0

# 同周期使用生产者的结果被拒绝
expect_value_error(execute, instructions, [[0, 2], [1]], initial, slots)

# 漏执行、重复执行、超出槽数
expect_value_error(execute, instructions, [[0, 1]], initial, slots)
expect_value_error(execute, instructions, [[0], [0], [1], [2]], initial, slots)
expect_value_error(execute, instructions, [[0, 1], [2]], initial, {"alu": 1})

# 依赖环、未定义寄存器、重复定义
cyclic = [("alu", "+", "x", ("y", "a")), ("alu", "+", "y", ("x", "a"))]
expect_value_error(schedule, cyclic, initial, slots)
expect_value_error(schedule, [("alu", "+", "z", ("a", "missing"))], initial, slots)
expect_value_error(schedule, [("alu", "+", "a", ("a", "b"))], initial, slots)
```

### 复杂度与追问

设指令数为 $I$，向量 lane 数为 $L$。`schedule` 每一轮都重新扫描全部指令找 ready 集，最坏要 $I$ 轮，是 $O(I^2)$；`execute` 是 $O(IL)$，寄存器存储 $O(IL)$。

- 追问「调度太慢」：维护每条指令还剩几个未完成依赖，依赖清零时放进 ready 队列，就是拓扑排序，总时间 $O(I + \text{依赖边数})$。
- 追问「能和官方排行榜比吗」：不能。官方完整机器、kernel 和 submission 测试以原仓库为准，这个小练习的周期数没有可比性。

## 题怎么来的

来源是 Anthropic 放在 GitHub 上的早期性能 take-home，并非某次 onsite 泄漏的脚本。README 写明：最初限时 4 小时；Claude Opus 4 超过多数人之后改成 2 小时，起点已经是 18532 个周期，大约比仓库里这份慢起点快 7.97 倍；Opus 4.5 之后，限时作业又换了底座。仓库里放的是“新指令和调试工具，加上最慢的那份起点”。现在招聘发的不是这一份，所以 `realInterview: false`。

验收看 `python tests/submission_tests.py` 打出的周期数。`tests/` 必须和 `origin/main` 一致，`git diff origin/main tests/` 应该为空。

## 机器

一条指令是一个字典，键是引擎，值是该引擎本周期要执行的槽，例如 `valu` 里放两条算术，同时 `load` 里放一条。每个引擎的槽数上限写在 `SLOT_LIMITS`。所有效果在周期结束时才写回：本周期所有槽先读旧值，再一起写。所以在同一周期里用“自己刚写的地址”做输入，读到的是旧值。

内存和 scratch 都是 32 位字。scratch 同时充当寄存器、常量区和手动管理的缓存。SIMD 的 `vload` / `vstore` 只能搬连续的 `VLEN` 个元素，不能按任意下标 gather。标量要先 `vbroadcast` 才能进 `valu`。

仓库自带的 `KernelBuilder.build` 默认一个 bundle 只放一个槽，所以标量核结果对但很慢。加速的办法是把独立的 load、alu、valu、flow 填进同一条指令，并让连续地址走向量槽。

## 优化时保留机器和测试的约定

`problem.py` 里有多核。README 专门点名了一种错误优化：模型发现多核没有加速，就去改 `N_CORES = 1`。这一版的多核是故意关掉的。如果周期数下降来自改模拟器或改测试，提交测试不会承认。

调试用 `flow` 引擎的 `pause` 和 `debug` 引擎。提交用的模拟器会忽略 debug。`pause` 要和参考核的 yield 对齐，否则本地对照会错位；提交端不看这些 pause。

## 追问

**先向量化还是先打包槽？**
先让标量结果和参考核一致，再把内层循环改成 `vload` 加 `valu`。槽打包不改变结果，只减少周期。如果两件事一起改，结果对不上时就分不清是打包后读到了旧值，还是向量下标错了。

**同一周期的依赖怎么排？**
生产者和消费者不能放进同一条指令。中间值先留在 scratch，下一条指令再用。周期结束才写回，就是在要求你把这条依赖显式排开。
