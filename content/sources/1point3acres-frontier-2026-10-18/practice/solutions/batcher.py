class Batcher:
    """按权重确定性地轮流从多个数据源取样本，调度位置跨 batch 保留，可保存和恢复状态。"""

    def __init__(self, sources, weights):
        if not sources or len(sources) != len(weights):
            raise ValueError("need one weight per source and at least one source")
        if any(not source for source in sources):
            raise ValueError("every source must be non-empty")
        if any(type(weight) is not int or weight < 1 for weight in weights):
            raise ValueError("weights must be positive ints")
        self.sources = [list(source) for source in sources]
        # 一个调度周期：源 0 连续 weights[0] 次，源 1 连续 weights[1] 次……
        self.schedule = [index for index, weight in enumerate(weights) for _ in range(weight)]
        self.pos = 0  # 在调度周期里的位置
        self.offsets = [0] * len(sources)  # 每个源下一个要读的下标

    def next_batch(self, n):
        """取 n 个样本。n 不必整除权重和，周期位置会延续到下一个 batch。"""
        if n < 0:
            raise ValueError(f"batch size must be non-negative, got {n}")
        batch = []
        for _ in range(n):
            index = self.schedule[self.pos]
            source = self.sources[index]
            batch.append(source[self.offsets[index]])
            self.offsets[index] = (self.offsets[index] + 1) % len(source)  # 源读完后从头循环
            self.pos = (self.pos + 1) % len(self.schedule)
        return batch

    def state(self):
        return self.pos, tuple(self.offsets)

    def restore(self, state):
        """恢复到 state()，之后的输出与不中断运行完全一致。"""
        pos, offsets = state
        if not 0 <= pos < len(self.schedule):
            raise ValueError(f"schedule position out of range: {pos}")
        if len(offsets) != len(self.sources):
            raise ValueError("need one offset per source")
        if any(not 0 <= offset < len(source) for offset, source in zip(offsets, self.sources)):
            raise ValueError(f"source offset out of range: {offsets}")
        self.pos = pos
        self.offsets = list(offsets)


def test():
    def make():
        return Batcher([["a0", "a1"], ["b0"]], [2, 1])

    # 按 2:1 的周期取数
    batcher = make()
    assert batcher.next_batch(2) == ["a0", "a1"]

    # 保存状态后继续取，再恢复，应得到同样的输出
    saved = batcher.state()
    expected = batcher.next_batch(7)
    batcher.restore(saved)
    assert batcher.next_batch(7) == expected

    # batch 大小不整除权重和：分两次取和一次取完结果相同，小权重源不会被饿死
    batcher = make()
    assert batcher.next_batch(2) + batcher.next_batch(3) == make().next_batch(5)
    assert make().next_batch(3) == ["a0", "a1", "b0"]

    # 非法状态
    try:
        make().restore((3, (0, 0)))
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-range state should raise ValueError")


if __name__ == "__main__":
    test()
