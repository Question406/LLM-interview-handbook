class Tasks:
    """带依赖的任务列表。状态：blocked -> ready -> running -> done / failed。

    只能依赖已经存在的任务，所以依赖图天然无环，添加顺序就是一个拓扑序。
    """

    def __init__(self):
        self.state = {}     # task_id -> 状态字符串
        self.deps = {}      # task_id -> 它依赖的任务集合
        self.children = {}  # task_id -> 直接依赖它的任务集合（反向边）

    def _require(self, task_id):
        if task_id not in self.state:
            raise ValueError(f"unknown task: {task_id!r}")

    def _initial_state(self, deps):
        if any(self.state[dep] == "failed" for dep in deps):
            return "failed"
        if all(self.state[dep] == "done" for dep in deps):
            return "ready"
        return "blocked"

    def add(self, task_id, depends=()):
        if task_id in self.state:
            raise ValueError(f"duplicate task: {task_id!r}")
        for dep in depends:
            self._require(dep)
        deps = set(depends)
        self.state[task_id] = self._initial_state(deps)
        self.deps[task_id] = deps
        self.children[task_id] = set()
        for dep in deps:
            self.children[dep].add(task_id)

    def start(self, task_id):
        self._require(task_id)
        if self.state[task_id] != "ready":
            raise ValueError(f"task {task_id!r} is {self.state[task_id]}, not ready")
        self.state[task_id] = "running"

    def finish(self, task_id, success=True):
        self._require(task_id)
        if self.state[task_id] != "running":
            raise ValueError(f"task {task_id!r} is {self.state[task_id]}, not running")
        if success:
            self.state[task_id] = "done"
            self._unblock_children(task_id)
        else:
            self.state[task_id] = "failed"
            self._fail_descendants(task_id)

    def _unblock_children(self, task_id):
        # 只需看直接后继：更远的后继至少还依赖一个没完成的直接后继
        for child in self.children[task_id]:
            if self.state[child] == "blocked" and all(
                self.state[dep] == "done" for dep in self.deps[child]
            ):
                self.state[child] = "ready"

    def _fail_descendants(self, task_id):
        # 菱形依赖里同一个后代会被多次碰到，用 seen 去重
        stack = list(self.children[task_id])
        seen = set()
        while stack:
            task = stack.pop()
            if task in seen:
                continue
            seen.add(task)
            if self.state[task] not in ("done", "failed"):
                self.state[task] = "failed"
            stack.extend(self.children[task])

    def snapshot(self):
        return dict(self.state)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 链式依赖 a -> b -> c：a 完成后只有 b 变 ready
    tasks = Tasks()
    tasks.add("a")
    tasks.add("b", ["a"])
    tasks.add("c", ["b"])
    tasks.start("a")
    tasks.finish("a")
    assert tasks.snapshot() == {"a": "done", "b": "ready", "c": "blocked"}

    # b 失败，下游 c 级联失败，已完成的 a 不受影响
    tasks.start("b")
    tasks.finish("b", False)
    assert tasks.snapshot()["c"] == "failed"
    assert tasks.snapshot()["a"] == "done"

    # 依赖已失败任务的新任务直接是 failed
    tasks.add("d", ["b"])
    assert tasks.snapshot()["d"] == "failed"

    # 菱形依赖：两个前置都完成后汇合点才 ready
    tasks = Tasks()
    tasks.add("root")
    tasks.add("left", ["root"])
    tasks.add("right", ["root"])
    tasks.add("join", ["left", "right"])
    tasks.start("root")
    tasks.finish("root")
    tasks.start("left")
    tasks.finish("left")
    assert tasks.snapshot()["join"] == "blocked"
    tasks.start("right")
    tasks.finish("right")
    assert tasks.snapshot()["join"] == "ready"

    # 非法操作
    expect_value_error(tasks.add, "root")              # 重复 id
    expect_value_error(tasks.add, "x", ["missing"])    # 依赖不存在
    expect_value_error(tasks.start, "root")            # 已完成的任务不能再 start
    expect_value_error(tasks.finish, "join")           # ready 还没 start
    expect_value_error(tasks.start, "missing")         # 未知任务


if __name__ == "__main__":
    test()
