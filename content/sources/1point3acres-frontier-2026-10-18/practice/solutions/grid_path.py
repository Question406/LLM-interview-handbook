MOD = 10**9 + 7


def grid_path(grid, start, k, bonus=0):
    """从 (0, start) 走到最后一行，每步下移 1 行或 2 行（下移 2 行算一次 jump，最多 k 次），
    列变化 -1/0/+1。分数是经过格子的值之和；下移 1 行且列不变时额外加 bonus。

    返回 (最高分, 最高分路径条数 mod 1e9+7, 一条最优路径的坐标列表)。
    """
    if not grid or not grid[0]:
        raise ValueError("grid must be non-empty")
    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("grid must be rectangular")
    if k < 0:
        raise ValueError("k must be non-negative")
    if not 0 <= start < len(grid[0]):
        raise ValueError("start column out of range")

    rows, cols = len(grid), len(grid[0])
    # 状态 (row, col, jumps_used)；只记录可达状态
    origin = (0, start, 0)
    best = {origin: grid[0][start]}
    count = {origin: 1}
    parent = {}

    # 所有转移都让行号变大，按行从上到下处理就是拓扑序：处理某个状态时，它的所有前驱都已处理完
    for row in range(rows):
        for col in range(cols):
            for used in range(k + 1):
                state = (row, col, used)
                if state not in best:
                    continue
                for step in (1, 2):
                    next_row = row + step
                    next_used = used + (step == 2)
                    if next_row >= rows or next_used > k:
                        continue
                    for next_col in (col - 1, col, col + 1):
                        if not 0 <= next_col < cols:
                            continue
                        target = (next_row, next_col, next_used)
                        score = best[state] + grid[next_row][next_col]
                        if step == 1 and next_col == col:
                            score += bonus
                        if target not in best or score > best[target]:
                            best[target] = score
                            count[target] = count[state]
                            parent[target] = state
                        elif score == best[target]:
                            # 同分时累加路径数；只统计达到最优分的路径
                            count[target] = (count[target] + count[state]) % MOD

    finals = [state for state in best if state[0] == rows - 1]
    top_score = max(best[state] for state in finals)
    winners = [state for state in finals if best[state] == top_score]
    total = sum(count[state] for state in winners) % MOD

    path = []
    state = min(winners)
    while True:
        path.append(state[:2])
        if state not in parent:
            break
        state = parent[state]
    path.reverse()
    return top_score, total, path


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 单列，逐行走最好
    assert grid_path([[1], [2], [3]], 0, 1) == (6, 1, [(0, 0), (1, 0), (2, 0)])
    assert grid_path([[1], [2], [3]], 0, 0)[0] == 6

    # 用一次 jump 跳过负分行，被跳过的行不计分
    assert grid_path([[1], [-100], [3]], 0, 1) == (4, 1, [(0, 0), (2, 0)])

    # 两条同分路径：(0,0)->(1,0) 和 (0,0)->(1,1)
    assert grid_path([[0, 0], [0, 0]], 0, 0)[1] == 2

    # 下移 1 行且列不变，加 bonus
    assert grid_path([[1], [2]], 0, 0, 5)[0] == 8

    # 只有一行时，起点就是终点
    assert grid_path([[-3]], 0, 2) == (-3, 1, [(0, 0)])

    # 非法输入
    expect_value_error(grid_path, [[1, 2], [3]], 0, 0)
    expect_value_error(grid_path, [[1]], 1, 0)
    expect_value_error(grid_path, [[1]], 0, -1)


if __name__ == "__main__":
    test()
