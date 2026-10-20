CELLS = {"X", ".", "#"}  # 初始感染、可感染、免疫墙
DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def validate(grid, threshold, infectious_days):
    if not grid or not grid[0]:
        raise ValueError("grid must be non-empty")
    width = len(grid[0])
    for row in grid:
        if len(row) != width:
            raise ValueError("grid rows must have the same length")
        if any(cell not in CELLS for cell in row):
            raise ValueError(f"grid cells must be one of {sorted(CELLS)}")
    if threshold not in range(1, 5):
        raise ValueError(f"threshold must be in 1..4, got {threshold}")
    if infectious_days is not None and infectious_days < 1:
        raise ValueError(f"infectious_days must be >= 1, got {infectious_days}")


def spread(grid, threshold=1, infectious_days=None):
    """同步模拟感染扩散，返回 (天数, 感染时间矩阵)。

    每天，一个未感染的 "." 格如果有至少 threshold 个四邻居此刻有传染性，第二天就被感染。
    一个格子在第 d 天被感染，传染期是 [d, d + infectious_days)；None 表示永远有传染性。
    天数是最后一次有新感染的那一天；仍有非墙格子没被感染时返回 -1。墙和未感染格的时间为 None。
    """
    validate(grid, threshold, infectious_days)
    height, width = len(grid), len(grid[0])
    infected_at = [[0 if cell == "X" else None for cell in row] for row in grid]

    def is_contagious(row, col, day):
        start = infected_at[row][col]
        if start is None:
            return False
        return infectious_days is None or day - start < infectious_days

    def contagious_neighbors(row, col, day):
        count = 0
        for d_row, d_col in DIRECTIONS:
            r, c = row + d_row, col + d_col
            if 0 <= r < height and 0 <= c < width and is_contagious(r, c, day):
                count += 1
        return count

    day = 0
    while True:
        # 先算出当天所有新感染，整天算完再写入，保证同一天内的更新是同步的
        newly_infected = []
        for row in range(height):
            for col in range(width):
                if grid[row][col] != "." or infected_at[row][col] is not None:
                    continue
                if contagious_neighbors(row, col, day) >= threshold:
                    newly_infected.append((row, col))
        # 没有新感染时，有传染性的格子只会越来越少，以后也不会再有新感染
        if not newly_infected:
            break
        day += 1
        for row, col in newly_infected:
            infected_at[row][col] = day

    unreachable = any(
        grid[row][col] != "#" and infected_at[row][col] is None
        for row in range(height)
        for col in range(width)
    )
    return (-1 if unreachable else day), infected_at


def test():
    def expect_value_error(fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 传染期 1 天：每个格子只在被感染当天传给下一格
    assert spread(["X.."], infectious_days=1) == (2, [[0, 1, 2]])

    # 墙挡住传播
    assert spread(["X#."])[0] == -1

    # 阈值 2：下面两格各只有一个感染邻居，永远达不到阈值
    assert spread(["XX", ".."], threshold=2)[0] == -1

    # 阈值 2 能传开的情况：中间格同时挨着两个感染源
    assert spread(["X.X"], threshold=2) == (1, [[0, 1, 0]])

    # 左下角要等到第 1 天才凑齐两个邻居；永久传染时能感染，
    # 传染期只有 1 天时左上角那个源已经失效，左下角永远凑不齐
    assert spread(["XX.", "..X"], threshold=2) == (2, [[0, 0, 1], [2, 1, 0]])
    assert spread(["XX.", "..X"], threshold=2, infectious_days=1)[0] == -1

    # 全是墙：不需要任何一天
    assert spread(["##"]) == (0, [[None, None]])

    expect_value_error(spread, [])                      # 空网格
    expect_value_error(spread, ["X.", "."])             # 行长不一致
    expect_value_error(spread, ["X?"])                  # 非法字符
    expect_value_error(spread, ["X."], threshold=5)     # 阈值超出 1..4
    expect_value_error(spread, ["X."], infectious_days=0)


if __name__ == "__main__":
    test()
