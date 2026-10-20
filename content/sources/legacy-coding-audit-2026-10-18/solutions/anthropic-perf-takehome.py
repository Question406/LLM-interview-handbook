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
