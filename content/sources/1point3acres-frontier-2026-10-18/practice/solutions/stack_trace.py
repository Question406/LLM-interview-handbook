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


def test():
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


if __name__ == "__main__":
    test()
