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


def test():
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


if __name__ == "__main__":
    test()
