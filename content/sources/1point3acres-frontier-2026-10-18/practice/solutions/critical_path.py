from collections import deque


def _build_producers(tasks):
    """output -> (输入集合, 耗时)。每个数据最多一个生产者，耗时非负。"""
    producers = {}
    for inputs, output, duration in tasks:
        if output in producers:
            raise ValueError(f"{output!r} has more than one producer")
        if duration < 0:
            raise ValueError(f"negative duration for {output!r}: {duration}")
        producers[output] = (set(inputs), duration)
    return producers


def _ancestors(producers, goal):
    """goal 以及它直接或间接依赖的所有数据（迭代 DFS，避免递归深度上限）。"""
    needed = set()
    stack = [goal]
    while stack:
        node = stack.pop()
        if node in needed:
            continue
        needed.add(node)
        if node in producers:
            stack.extend(producers[node][0])
    return needed


def critical_path(tasks, goal):
    """机器无限、任务等全部输入就绪才开始时，goal 最早什么时候可用。"""
    producers = _build_producers(tasks)
    needed = _ancestors(producers, goal)  # 只看 goal 的依赖子图，无关的环不影响结果

    pending = {node: 0 for node in needed}  # 还没就绪的输入个数
    consumers = {node: [] for node in needed}
    ready_time = {node: 0 for node in needed}  # 源数据在时刻 0 就绪
    for node in needed:
        if node in producers:
            inputs, _ = producers[node]
            pending[node] = len(inputs)
            for parent in inputs:
                consumers[parent].append(node)

    # Kahn 拓扑序：出队时所有输入都已处理，ready_time 暂存的是「最晚的输入就绪时间」
    queue = deque(node for node in needed if pending[node] == 0)
    processed = 0
    while queue:
        node = queue.popleft()
        processed += 1
        if node in producers:
            ready_time[node] += producers[node][1]  # 开始时间 + 自身耗时
        for child in consumers[node]:
            ready_time[child] = max(ready_time[child], ready_time[node])
            pending[child] -= 1
            if pending[child] == 0:
                queue.append(child)

    if processed != len(needed):
        raise ValueError(f"dependency cycle on the way to {goal!r}")
    return ready_time[goal]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    tasks = [(["a", "b"], "c", 30), (["b"], "d", 15), (["c", "d"], "g", 60)]

    # 两条前置链取较长的一条：max(30, 15) + 60
    assert critical_path(tasks, "g") == 90

    # 源数据在 0 时刻就绪
    assert critical_path(tasks, "a") == 0

    # 与目标无关的环不影响结果
    assert critical_path(tasks + [(["z"], "z", 1)], "g") == 90

    # 目标依赖子图里有环
    expect_value_error(critical_path, [(["b"], "a", 1), (["a"], "b", 1)], "a")

    # 没有输入的任务从 0 开始
    assert critical_path([([], "a", 7)], "a") == 7

    # 同一个输出有两个生产者、负耗时
    expect_value_error(critical_path, [([], "a", 1), ([], "a", 2)], "a")
    expect_value_error(critical_path, [([], "a", -1)], "a")

    # 长链：不能依赖递归
    chain = [([f"n{i}"], f"n{i + 1}", 1) for i in range(5000)]
    assert critical_path(chain, "n5000") == 5000


if __name__ == "__main__":
    test()
