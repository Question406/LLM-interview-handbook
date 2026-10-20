def schedule(tasks, models, humans, start_task=0):
    """为每个任务的每个模型输出分配一名标注员，返回 [(task, model, human), ...]。

    任务 t 上模型 m 的输出交给 (t + m) % humans 号标注员。
    start_task 用于分批调用：先排 [0, 3) 再从 3 开始排，结果和一次排完相同。
    """
    if tasks < 0:
        raise ValueError(f"tasks must be >= 0, got {tasks}")
    if models < 1:
        raise ValueError(f"models must be >= 1, got {models}")
    if humans < models:
        raise ValueError(f"need at least as many humans as models ({humans} < {models})")
    if start_task < 0:
        raise ValueError(f"start_task must be >= 0, got {start_task}")

    assignments = []
    for task in range(start_task, start_task + tasks):
        # 同一任务内 m 取 0..models-1，且 models <= humans，所以 (task + m) % humans 互不相同
        for model in range(models):
            assignments.append((task, model, (task + model) % humans))
    return assignments


def test():
    from collections import Counter

    assert schedule(2, 2, 3) == [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 2)]

    # 小范围穷举检查三条不变量
    humans = 5
    for tasks in range(10):
        for models in range(1, 5):
            result = schedule(tasks, models, humans)

            # 每个 (任务, 模型) 恰好分配一次
            pairs = {(task, model) for task, model, _ in result}
            assert len(pairs) == tasks * models
            assert len(result) == tasks * models

            # 同一任务内标注员不重复
            for task in range(tasks):
                assert len({h for t, _, h in result if t == task}) == models

            # 标注员之间的负载差不超过 models
            counts = Counter(h for _, _, h in result)
            loads = [counts[h] for h in range(humans)]
            assert max(loads) - min(loads) <= models

    # 分批调用和一次调用结果一致
    assert schedule(3, 2, 3) + schedule(4, 2, 3, 3) == schedule(7, 2, 3)


if __name__ == "__main__":
    test()
