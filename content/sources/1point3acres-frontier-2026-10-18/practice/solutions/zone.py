from collections import deque

# 固定的邻居顺序：上、左、右、下，保证结果确定
NEIGHBOR_STEPS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def escape(rows, cols, start, is_premium):
    """在 rows x cols 网格上从 start 出发四邻接移动，返回到最近的非 premium 格的最短路径。

    路径包含起点和终点；起点本身不是 premium 时返回 [start]；整个网格都是 premium 时返回 None。
    """
    if rows < 1 or cols < 1:
        raise ValueError(f"grid must be non-empty, got {rows}x{cols}")
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        raise ValueError(f"start {start} is outside the grid")

    queue = deque([start])
    prev = {start: None}  # 兼作 visited：入队时就记录，避免同一格重复入队
    while queue:
        cell = queue.popleft()
        if not is_premium(cell):
            return rebuild_path(prev, cell)
        row, col = cell
        for d_row, d_col in NEIGHBOR_STEPS:
            neighbor = (row + d_row, col + d_col)
            inside = 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols
            if inside and neighbor not in prev:
                prev[neighbor] = cell
                queue.append(neighbor)
    return None


def rebuild_path(prev, end):
    path = []
    cell = end
    while cell is not None:
        path.append(cell)
        cell = prev[cell]
    return path[::-1]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 只有中心是 premium，一步就能出去
    path = escape(3, 3, (1, 1), lambda cell: cell == (1, 1))
    assert len(path) == 2
    assert path[0] == (1, 1)

    # 整个网格都是 premium
    assert escape(2, 2, (0, 0), lambda cell: True) is None

    # 起点已经在外面
    assert escape(2, 2, (0, 0), lambda cell: False) == [(0, 0)]

    # 最短路径：只有最右一列在外面，从 (1, 0) 出发要走 3 步
    path = escape(3, 4, (1, 0), lambda cell: cell[1] < 3)
    assert len(path) == 4
    assert path[-1][1] == 3

    expect_value_error(escape, 0, 3, (0, 0), lambda cell: True)
    expect_value_error(escape, 2, 2, (2, 0), lambda cell: True)


if __name__ == "__main__":
    test()
