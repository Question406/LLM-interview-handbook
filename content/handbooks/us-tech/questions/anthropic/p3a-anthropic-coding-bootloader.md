---
id: p3a-anthropic-coding-bootloader
section: anthropic
order: 613
level: A
title: "Anthropic：指令模拟：检测死循环并修复单条指令"
quick: "用访问过的 pc 集合判断死循环，累加器单独维护；修复时枚举每条 next/jump 互换后重跑，O(n²)，用反向可达终止位置的集合可降到 O(n)。"
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
  - title: "1Point3Acres · Anthropic · coding-bootloader"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/coding-bootloader
    type: secondary
---

## 题目

模拟一段只有三种指令的程序：累加（题卡里叫 plus）、顺序执行下一条（next）、相对跳转（jump）。先判断程序会不会陷入死循环，再找出那条出错的指令：把它在 next 和 jump 之间互换一次，让程序能正常结束。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题，累加指令在练习里写作 `acc`。

## 思路

模拟部分用程序计数器 pc 和一个访问过的 pc 集合。程序是确定性的，同一个 pc 第二次出现时，之后的执行会完全重复，所以这时就能断定是死循环。累加器的值和判环无关，单独维护。

修复部分的基础解法是暴力：枚举每一条 next/jump，互换后从头重新模拟一次，第一次能正常结束的就是答案，O($n^{2}$)。

想做到 O(n) 可以反过来想：先在「所有指令都不改」的图上，从终止位置 n 出发沿反向边找出所有最终能走到 n 的 pc。然后沿原来的执行路径走，对路径上每条 next/jump 看一眼：互换之后的下一个 pc 是否在「能终止」的集合里。第一个满足的就是修复点。这里要注意两点：

- 改动的指令必须在原路径上真的被执行到，没执行到的指令改了也不影响结果；
- 原路径在遇到修复点之前不会被改动影响，所以只需要检查互换后那一步的去向。

和面试官确认越界（跳到 n 以外或负数下标）算正常结束还是错误，以及有多个可行修复时返回哪一个。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- 程序是 `(op, arg)` 列表。`acc` 把 `arg` 加到累加器并让 pc 加一；`next` 忽略 `arg`，pc 加一；`jump` 让 pc 加 `arg`。未知指令抛 `ValueError`。
- `run(program, flip=None) -> (terminated, acc)`：只有 pc 恰好等于 `len(program)` 才算正常结束。死循环或跳出范围都返回 `False`，同时返回停下时累加器的值。`flip` 是执行时临时互换 next/jump 的那条指令下标。
- `repair(program) -> (index, acc) | None`：恰好互换一条 next/jump（不能改 `acc`），按下标从小到大返回第一个能让程序正常结束的修改及最终累加器；无解返回 `None`。
- $n \le 2000$。

### 输入输出示例

```text
run([("acc", 1), ("jump", -1)])                  -> (False, 1)   # pc 1 跳回 0，再次访问 pc 0
repair([("acc", 1), ("jump", -1)])               -> (1, 1)       # 下标 1 改成 next 后正常结束
repair([("next", 0), ("acc", 1), ("jump", -1)])  -> (2, 1)       # 改下标 0 会变成 jump 0，原地打转
run([("jump", 3)])                               -> (False, 0)   # 跳出范围不算正常结束
```

### 解题思路与正确性

判环：一旦 pc 重复，之后的状态转移只依赖 pc（累加器不影响控制流），会无限重复同一段，所以 `visited` 足以判定死循环；而 pc 不重复时最多执行 n 步就会离开范围或结束。

修复：`repair` 枚举了所有合法的单条修改，并对每种修改独立从头模拟，所以不会漏掉可行修复，返回的也一定是下标最小的那个。

### 完整参考实现（Python 3）

```python
SWAPPED = {"next": "jump", "jump": "next"}


def run(program, flip=None):
    """执行 (op, arg) 指令列表，返回 (是否正常结束, acc)。

    flip 是要把 next/jump 互换的那条指令下标。只有 pc 恰好等于 len(program) 才算正常结束；
    重复访问同一个 pc（死循环）或跳出范围都返回 False。
    """
    pc = 0
    acc = 0
    visited = set()
    while 0 <= pc < len(program) and pc not in visited:
        visited.add(pc)
        op, arg = program[pc]
        if pc == flip:
            op = SWAPPED.get(op, op)
        if op == "acc":
            acc += arg
            pc += 1
        elif op == "next":
            pc += 1
        elif op == "jump":
            pc += arg
        else:
            raise ValueError(f"unknown op at {pc}: {op!r}")
    return pc == len(program), acc


def repair(program):
    """恰好互换一条 next/jump，返回第一个能让程序正常结束的 (下标, acc)；无解返回 None。"""
    for index, (op, _) in enumerate(program):
        if op not in SWAPPED:
            continue
        terminated, acc = run(program, flip=index)
        if terminated:
            return index, acc
    return None
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 最小死循环：把下标 1 的 jump 改成 next 就能结束
looping = [("acc", 1), ("jump", -1)]
assert run(looping) == (False, 1)
assert repair(looping) == (1, 1)

# 空程序直接正常结束；跳出范围不算正常结束
assert run([]) == (True, 0)
assert run([("jump", 3)]) == (False, 0)

# 没有 next/jump 可改时无解
assert repair([("acc", 1)]) is None

# 下标 0 的 next 改成 jump 0 会原地打转，所以修复点是下标 2
program = [("next", 0), ("acc", 1), ("jump", -1)]
assert run(program) == (False, 1)
assert repair(program) == (2, 1)

# next 改成 jump 也算一种修复
assert repair([("next", 2), ("jump", -1)]) == (0, 0)

expect_value_error(run, [("nop", 0)])
```

### 复杂度与追问

设程序长度为 n。`run` 是 O(n) 时间和空间；`repair` 最多模拟 n 次，O($n^{2}$)。

- 优化到 O(n)：按「思路」里的方法，先从终止位置做反向可达性，再沿原执行路径找第一个互换后能落进可终止集合的指令。注意这样找到的是原路径上最早被执行到的修复点，不一定是下标最小的那个，如果面试官要求下标最小，就要在路径上收集所有可行点再取最小。
- 允许改 `acc` 或改多条指令时，问题变成在状态图上找最短修改路径，可以把「已改次数」放进状态做 BFS。
